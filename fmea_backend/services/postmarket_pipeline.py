"""
Orchestrates MAUDE ingest → NLP extraction → risk scoring for a Smart Risk project.

Stages are logged independently; failures in optional stages yield ``partial`` status with warnings.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from crud import maude_adverse_event as maude_crud
from crud import postmarket_intelligence as pm_intel_crud
from crud import project as project_crud
from models.maude_nlp_extraction import MaudeNlpExtraction
from schemas.postmarket_maude import PostmarketIngestRequest
from schemas.postmarket_nlp import PostmarketExtractRequest
from schemas.postmarket_pipeline import (
    PostmarketRunPipelineRequest,
    PostmarketRunPipelineResponse,
    PostmarketScoringSummaryOut,
)
from schemas.postmarket_risk_scoring import SuggestedMissingRisk
from services.maude_ingestion import OpenFDABadResponseError, OpenFDAError, ingest_openfda_maude
from services.postmarket_nlp import extract_maude_events_batch
from services.risk_scoring import _failure_mode_key, score_project_postmarket

logger = logging.getLogger(__name__)


def _json_safe_request(body: PostmarketRunPipelineRequest) -> Dict[str, Any]:
    return body.model_dump(mode="json")


def run_postmarket_pipeline(
    db: Session,
    *,
    user_id: str,
    body: PostmarketRunPipelineRequest,
) -> PostmarketRunPipelineResponse:
    warnings: List[str] = []
    records_fetched = records_inserted = records_skipped = 0
    records_extracted = 0
    extracted_failure_modes_count = 0
    scoring_summary: Optional[PostmarketScoringSummaryOut] = None
    top_missing: List[SuggestedMissingRisk] = []
    status: str = "completed"

    project = project_crud.get_project(db, body.project_id, user_id)
    if not project:
        return PostmarketRunPipelineResponse(
            status="failed",
            warnings=["Project not found or access denied."],
        )

    device_ingest_name = (body.device_name or body.device_type or "").strip()
    if not device_ingest_name:
        return PostmarketRunPipelineResponse(
            status="failed",
            warnings=["device_type (or device_name) is required."],
        )

    # --- Ingest ---
    if body.run_ingestion:
        try:
            ingest_req = PostmarketIngestRequest(
                device_name=device_ingest_name,
                manufacturer_name=body.manufacturer_name,
                generic_device_type=body.generic_device_type,
                date_from=body.date_from,
                date_to=body.date_to,
                max_records=body.max_ingest_records,
                page_size=min(1000, max(1, body.max_ingest_records)),
            )
            ir = ingest_openfda_maude(db, ingest_req)
            records_fetched = ir.fetched
            records_inserted = ir.inserted
            records_skipped = ir.skipped_duplicates + ir.skipped_malformed
            warnings.extend(ir.warnings or [])
        except ValueError as e:
            status = "partial"
            warnings.append(f"Ingest validation: {e}")
            logger.warning("Post-market ingest skipped: %s", e)
        except (OpenFDAError, OpenFDABadResponseError) as e:
            status = "partial"
            warnings.append(f"Ingest failed (openFDA): {e}")
            logger.error("Post-market ingest failed: %s", e, exc_info=True)
        except Exception as e:
            status = "partial"
            warnings.append(f"Ingest failed: {e}")
            logger.exception("Post-market ingest unexpected error")

    # --- Extract ---
    ok_event_ids: List[str] = []
    if body.run_extraction:
        try:
            pending = maude_crud.list_event_ids_missing_extraction(
                db,
                device_type=body.device_type.strip(),
                date_from=body.date_from,
                date_to=body.date_to,
                limit=body.max_extract_events,
            )
            if not pending:
                warnings.append("No MAUDE events pending NLP extraction for this device/date filter.")
            else:
                ex_req = PostmarketExtractRequest(event_ids=pending)
                ex_res = extract_maude_events_batch(db, ex_req)
                records_extracted = ex_res.succeeded
                if ex_res.failed:
                    warnings.append(f"NLP extraction failed for {ex_res.failed} event(s); check logs / API keys.")
                    status = "partial"
                ok_event_ids = [r.event_id for r in ex_res.results if r.status == "ok"]
                if ok_event_ids:
                    rows = (
                        db.query(MaudeNlpExtraction)
                        .filter(MaudeNlpExtraction.maude_event_id.in_(ok_event_ids))
                        .all()
                    )
                    themes = {_failure_mode_key(x) for x in rows}
                    extracted_failure_modes_count = len(themes - {"unknown"})
        except Exception as e:
            status = "partial"
            warnings.append(f"Extraction stage failed: {e}")
            logger.exception("Post-market extraction stage failed")

    # --- Score ---
    if body.run_scoring:
        try:
            score = score_project_postmarket(
                db,
                project_id=body.project_id,
                project=project,
                device_type_override=body.device_type.strip(),
            )
            scoring_summary = PostmarketScoringSummaryOut(
                device_type_used=score.device_type_used,
                date_from=score.date_from,
                date_to=score.date_to,
                failure_mode_themes_scored=len(score.items),
                suggested_missing_count=len(score.suggested_missing_risks),
            )
            top_missing = list(score.suggested_missing_risks)[:20]
        except Exception as e:
            status = "partial"
            warnings.append(f"Scoring stage failed: {e}")
            logger.exception("Post-market scoring stage failed")

    run_row = pm_intel_crud.create_project_run(
        db,
        project_id=body.project_id,
        status=status,
        request_snapshot=_json_safe_request(body),
        records_fetched=records_fetched,
        records_inserted=records_inserted,
        records_skipped=records_skipped,
        records_extracted=records_extracted,
        extracted_failure_modes_count=extracted_failure_modes_count,
        scoring_summary=scoring_summary.model_dump(mode="json") if scoring_summary else None,
        top_missing_risks=[m.model_dump(mode="json") for m in top_missing],
        warnings=warnings,
        completed_at=datetime.now(timezone.utc),
    )

    if status != "failed" and (records_inserted > 0 or records_extracted > 0 or scoring_summary is not None):
        try:
            from services.pms_report_document_sync import refresh_pms_report_document_for_project

            refresh_pms_report_document_for_project(db, project_id=body.project_id, user_id=user_id)
        except Exception:
            logger.exception("postmarket pipeline: pms_report document sync failed")

    return PostmarketRunPipelineResponse(
        records_fetched=records_fetched,
        records_inserted=records_inserted,
        records_skipped=records_skipped,
        records_extracted=records_extracted,
        extracted_failure_modes_count=extracted_failure_modes_count,
        scoring_summary=scoring_summary,
        top_missing_risks=top_missing,
        status=status,  # type: ignore[arg-type]
        warnings=warnings,
        pipeline_run_id=run_row.id,
    )
