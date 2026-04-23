"""
Keep the ``pms_report`` **project document** row aligned with MAUDE/NLP + PMS signals.

WHY THIS EXISTS:
    The Documentation hub shows ``documents.content`` from GET /projects/{id}/documents — not
    POST /postmarket/report. Historically, after the first profile init the body became
    ``_draft_pms_report`` text starting with "PMS Report — Draft". That string did **not**
    match ``_content_is_placeholder_for_type`` (which only looked for "pms report starter"),
    so ``_should_populate`` stayed false forever and the stored document never refreshed
    even when MAUDE data appeared.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from sqlalchemy.orm import Session

from business_logic.project_initializer import _default_content_for
from crud import document as document_crud
from crud import project as project_crud
from models.document import Document
from models.postmarket_intelligence import PostmarketProjectRun
from schemas.document import DocumentCreate, DocumentUpdate
from schemas.postmarket_report import PostmarketReportRequest

logger = logging.getLogger(__name__)

PMS_REPORT_DOCUMENT_TYPE = "pms_report"
PMS_REPORT_DOCUMENT_KEY = "pms_report"
PMS_REPORT_DOCUMENT_NAME = "PMS Report"


@dataclass
class PmsReportRegenerationResult:
    project_id: str
    report_mode: str
    document_id: str
    document_key: str
    created_new_document: bool
    updated_existing_document: bool
    previous_document_found: bool
    updated_at: Optional[datetime]
    preview_excerpt: str
    linked_maude_rows_count: int
    pms_signal_count: int
    scoring_summary_present: bool


def get_or_create_pms_report_document_row(db: Session, *, project_id: str) -> Tuple[Document, bool]:
    """
    Resolve the project's PMS Report document row. Creates it if missing (same shape as required docs).
    Scans by lowercase type in case legacy rows used mixed casing.
    """
    doc = document_crud.get_document_by_type(db, project_id=project_id, doc_type=PMS_REPORT_DOCUMENT_TYPE)
    if doc:
        return doc, False
    for d in document_crud.get_documents_by_project(db, project_id):
        if (d.type or "").strip().lower() == PMS_REPORT_DOCUMENT_TYPE:
            return d, False
    create = DocumentCreate(
        project_id=project_id,
        name=PMS_REPORT_DOCUMENT_NAME,
        type=PMS_REPORT_DOCUMENT_TYPE,
        status="draft",
        content=_default_content_for(PMS_REPORT_DOCUMENT_TYPE),
    )
    created = document_crud.create_document(db, create)
    logger.info("pms_report sync: created missing pms_report document id=%s project=%s", created.id, project_id)
    return created, True


def pms_report_content_is_auto_refreshable_placeholder(content: Optional[str]) -> bool:
    """
    True for empty content, registry starter text, or legacy static draft bodies that
    should be replaced during project initialization.
    """
    if not (content or "").strip():
        return True
    raw = (content or "").strip()
    c = raw.lower()
    if c.startswith("pms report starter"):
        return True
    if "no pms data included" in c:
        return True
    if c.startswith("pms report — draft") or c.startswith("pms report - draft"):
        return True
    if "system-generated draft template" in c and "pms report" in raw[:120].lower():
        return True
    return False


def collect_pms_report_refs(db: Session, project_id: str) -> Dict[str, Any]:
    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = {(d.type or "").lower(): d for d in docs}
    return {
        "pms_plan": by_type.get("pms_plan"),
        "hazard_analysis": by_type.get("hazard_analysis"),
        "fmea": by_type.get("fmea"),
    }


def _scoring_summary_present(db: Session, project_id: str) -> bool:
    try:
        run = (
            db.query(PostmarketProjectRun)
            .filter(PostmarketProjectRun.project_id == project_id)
            .order_by(PostmarketProjectRun.started_at.desc())
            .first()
        )
    except Exception:
        # Some dev DBs may not have postmarket_project_runs yet.
        logger.exception("pms_report sync: scoring_summary lookup failed")
        return False
    if run is None or run.scoring_summary is None:
        return False
    if isinstance(run.scoring_summary, dict) and not run.scoring_summary:
        return False
    return True


def regenerate_pms_report_document_for_project(
    db: Session,
    *,
    project_id: str,
    user_id: str,
) -> PmsReportRegenerationResult:
    """
    Rebuild/Upsert ``pms_report`` document body from live post-market data (draft or populated).
    """
    project = project_crud.get_project(db, project_id, user_id)
    if not project:
        raise ValueError("Project not found")

    doc, created_new = get_or_create_pms_report_document_row(db, project_id=project_id)
    previous_found = not created_new
    previous_content = doc.content or ""

    from services.postmarket_report import build_postmarket_report, render_postmarket_report_markdown

    report = build_postmarket_report(
        db,
        user_id=user_id,
        body=PostmarketReportRequest(project_id=project_id),
    )
    refs = collect_pms_report_refs(db, project_id)
    content = render_postmarket_report_markdown(report, refs=refs)

    # Content-only: if the row was ``approved``, ``update_document`` demotes to draft when content changes.
    updated = document_crud.update_document(db, doc.id, DocumentUpdate(content=content), project_id)
    if not updated:
        raise RuntimeError("Failed to persist pms_report document update")
    logger.info("pms_report sync: updated document id=%s project=%s", doc.id, project_id)
    updated_existing = previous_found and (previous_content != content)
    excerpt = content[:320].replace("\n", " ").strip()
    return PmsReportRegenerationResult(
        project_id=project_id,
        report_mode=report.report_mode,
        document_id=updated.id,
        document_key=PMS_REPORT_DOCUMENT_KEY,
        created_new_document=created_new,
        updated_existing_document=updated_existing,
        previous_document_found=previous_found,
        updated_at=updated.updated_at,
        preview_excerpt=excerpt,
        linked_maude_rows_count=report.summary.maude_nlp_linked_records_reviewed,
        pms_signal_count=report.summary.pms_signal_records_in_scope,
        scoring_summary_present=_scoring_summary_present(db, project_id),
    )


def refresh_pms_report_document_for_project(
    db: Session,
    *,
    project_id: str,
    user_id: str,
) -> Document:
    """
    Backward-compatible wrapper used by existing callers needing DocumentOut shape.
    """
    result = regenerate_pms_report_document_for_project(db, project_id=project_id, user_id=user_id)
    updated = document_crud.get_document(db, result.document_id, project_id)
    if not updated:
        raise RuntimeError("PMS report document not found after regeneration")
    return updated

