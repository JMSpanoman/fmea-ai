from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from crud import document as document_crud
from schemas.document import DocumentCreate, DocumentUpdate


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _marker(source_doc_id: str, version_id: str, version_no: int) -> str:
    return f"[CHANGE_IMPACT_ENTRY source_doc_id={source_doc_id} version_id={version_id} version_no={version_no}]"


def _candidate_types_for_change(source_type: str) -> List[str]:
    t = (source_type or "").lower().strip()
    if t == "component":
        return ["fmea", "hazard_analysis", "risk_controls_doc", "traceability_matrix"]
    if t == "fmea":
        return ["risk_controls_doc", "residual_risk", "traceability_matrix"]
    if t in {"risk_controls_doc", "risk_control"}:
        return ["vv_plan", "vv_evidence", "residual_risk", "traceability_matrix"]
    if t == "design_inputs_doc":
        return ["design_outputs_doc", "vv_plan", "traceability_matrix"]
    if t == "design_outputs_doc":
        return ["vv_plan", "traceability_matrix"]
    if t == "vv_plan":
        return ["vv_evidence", "validation_summary", "traceability_matrix"]
    # generic fallback
    return ["traceability_matrix"]


def _ensure_impact_doc(db: Session, project_id: str) -> Any:
    doc = document_crud.get_document_by_type(db, project_id=project_id, doc_type="change_impact_analysis")
    if doc:
        return doc
    return document_crud.create_document(
        db,
        DocumentCreate(
            project_id=project_id,
            name="Change Impact Analysis",
            type="change_impact_analysis",
            status="draft",
            content="Change Impact Analysis starter. System-generated impact candidates are appended when project artifacts change versions.",
        ),
    )


def record_change_impact_for_document_version(
    db: Session,
    *,
    project_id: str,
    source_doc: Any,
    version_obj: Any,
) -> None:
    """
    Append an impact candidate entry when a document gets a new version.
    - Idempotent by (source_doc_id, version_id, version_no) marker
    - Never infers conclusions; human fields remain blank
    - Never overwrites user text (append-only)
    """
    source_type = str(getattr(source_doc, "type", "") or "").lower().strip()
    if source_type in {"change_impact_analysis", "design_change_record"}:
        return

    impact_doc = _ensure_impact_doc(db, project_id)

    m = _marker(
        source_doc_id=str(getattr(source_doc, "id", "") or ""),
        version_id=str(getattr(version_obj, "id", "") or ""),
        version_no=int(getattr(version_obj, "version", 0) or 0),
    )
    existing = impact_doc.content or ""
    if m in existing:
        return

    docs = document_crud.get_documents_by_project(db, project_id)
    by_type = {(d.type or "").lower(): d for d in docs}

    candidates = _candidate_types_for_change(source_type)
    candidate_lines: List[str] = []
    for t in candidates:
        d = by_type.get(t)
        if not d:
            candidate_lines.append(f"- {t}: (not present yet)")
        else:
            candidate_lines.append(f"- {t}: doc_id={d.id} (status={d.status}, version=v{d.version})")

    entry = (
        "\n"
        + ("=" * 72)
        + "\n"
        + "Change Impact Entry — Draft (candidates only)\n"
        + m
        + "\n"
        + f"Timestamp (UTC): {str(getattr(version_obj, 'created_at', '') or _now())}\n"
        + f"Changed artifact: {source_doc.name} (type={source_type}, doc_id={source_doc.id})\n"
        + f"New version: v{version_obj.version} (version_id={version_obj.id})\n"
        + "\n"
        + "Auto-listed impacted artifacts (candidates only; no conclusions):\n"
        + "\n".join(candidate_lines)
        + "\n\n"
        + "Human assessment (required)\n"
        + "- Impact summary: (blank)\n"
        + "- Decision: (blank — No impact / Requires update / TBD)\n"
        + "- Actions and owners: (blank)\n"
    )

    new_content = (existing.rstrip() + "\n" + entry).lstrip() if existing else entry.lstrip()
    document_crud.update_document(
        db,
        impact_doc.id,
        DocumentUpdate(content=new_content, status="draft"),
        project_id,
    )

