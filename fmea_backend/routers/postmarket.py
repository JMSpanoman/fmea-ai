"""
Post-market data ingestion (FDA openFDA / MAUDE).

Example request — ``POST /postmarket/ingest`` (Pro; Bearer token):

.. code-block:: json

    {
      "device_name": "pacemaker",
      "manufacturer_name": "Medtronic",
      "generic_device_type": null,
      "date_from": "2022-01-01",
      "date_to": "2023-12-31",
      "max_records": 200,
      "page_size": 100
    }

Example response:

.. code-block:: json

    {
      "fetched": 200,
      "inserted": 180,
      "skipped_duplicates": 20,
      "skipped_malformed": 0,
      "openfda_total_hint": 4521,
      "warnings": []
    }
"""
from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from auth.plan import require_pro
from crud import project as project_crud
from database import get_db
from models.user import User
from schemas import document as doc_schemas
from schemas.pms_report_document import PmsReportRegenerateDocumentResponse
from schemas.postmarket_maude import PostmarketIngestRequest, PostmarketIngestResponse
from schemas.postmarket_nlp import PostmarketExtractRequest, PostmarketExtractResponse
from schemas.postmarket_report import PostmarketReportRequest, PostmarketReportResponse
from schemas.postmarket_pipeline import (
    PostmarketAddMissingRiskToFmeaRequest,
    PostmarketAddMissingRiskToFmeaResponse,
    PostmarketMissingRisksResponse,
    PostmarketRunPipelineRequest,
    PostmarketRunPipelineResponse,
)
from schemas.postmarket_risk_scoring import (
    FailureModeScoreRequest,
    FailureModeScoreResponse,
    ProjectRiskScoreResponse,
)
from services.maude_ingestion import OpenFDABadResponseError, OpenFDAError, ingest_openfda_maude
from services.postmarket_fmea_bridge import add_missing_postmarket_risk_to_fmea
from services.postmarket_match_service import build_missing_risks_for_project
from services.postmarket_nlp import extract_maude_events_batch
from services.postmarket_pipeline import run_postmarket_pipeline
from services.postmarket_report import build_postmarket_report
from services.risk_scoring import score_failure_mode_request, score_project_postmarket

logger = logging.getLogger(__name__)


class PostmarketRefreshPmsReportBody(BaseModel):
    """Rebuild the stored PMS Report project document (Documentation / Document Control)."""

    project_id: str = Field(..., min_length=1)


class PostmarketPmsDocumentDebugResponse(BaseModel):
    project_id: str
    expected_document_type: str
    expected_document_name: str
    document_found: bool
    document_id: Optional[str] = None
    document_type_actual: Optional[str] = None
    document_name_actual: Optional[str] = None
    document_updated_at: Optional[str] = None
    contains_legacy_no_data_text: bool
    linked_maude_rows_count: int
    pms_signal_count: int
    scoring_summary_present: bool
    computed_report_mode: str


router = APIRouter(
    prefix="/postmarket",
    tags=["Post-Market — FDA Ingestion"],
    dependencies=[Depends(require_pro)],
)


@router.post(
    "/ingest",
    response_model=PostmarketIngestResponse,
    summary="Ingest MAUDE device adverse events from openFDA",
    description=(
        "Queries openFDA ``device/event`` and stores normalized rows in ``maude_adverse_events``. "
        "Duplicate (report number + device sequence) rows are skipped. "
        "Set ``OPENFDA_API_KEY`` for higher rate limits."
    ),
)
def postmarket_ingest_maude(
    body: PostmarketIngestRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> PostmarketIngestResponse:
    _ = _current_user  # auth + Pro gate
    try:
        return ingest_openfda_maude(db, body)
    except ValueError as e:
        logger.info("Ingest validation error: %s", e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except OpenFDABadResponseError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e)) from e
    except OpenFDAError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e)) from e


@router.post(
    "/extract",
    response_model=PostmarketExtractResponse,
    summary="Extract structured risk fields from MAUDE narratives (OpenAI)",
    description=(
        "Runs LLM extraction on ``maude_adverse_events.narrative_text`` for one or many IDs. "
        "Upserts into ``maude_nlp_extractions``. Requires ``OPENAI_API_KEY``."
    ),
)
def postmarket_extract_narratives(
    body: PostmarketExtractRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> PostmarketExtractResponse:
    _ = _current_user
    try:
        return extract_maude_events_batch(db, body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e


@router.post(
    "/risk-score/failure-mode",
    response_model=FailureModeScoreResponse,
    summary="Score a specific failure-mode theme for a device type (MAUDE NLP)",
    description=(
        "Example body: "
        '{"device_type":"infusion pump","component":"battery","failure_mode":"power","date_from":null,"date_to":null}. '
        "Returns suggested FMEA probability (1–5), weighted counts, trend, and top related causes/effects."
    ),
)
def post_postmarket_risk_score_failure_mode(
    body: FailureModeScoreRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(get_current_user),
) -> FailureModeScoreResponse:
    _ = _current_user
    try:
        return score_failure_mode_request(db, body)
    except Exception as e:
        logger.exception("failure-mode risk score failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get(
    "/risk-score/{project_id}",
    response_model=ProjectRiskScoreResponse,
    summary="Post-market probability signals for a project (MAUDE NLP aggregates)",
    description=(
        "Derives a device-type filter from project profile / name, aggregates ``maude_nlp_extractions`` "
        "with MAUDE event dates, and suggests 1–5 probability scores plus possible FMEA gaps. "
        "MAUDE frequency is supporting evidence only—not true incidence."
    ),
)
def get_postmarket_risk_score_for_project(
    project_id: str,
    device_type: Optional[str] = Query(
        None,
        description="Override MAUDE device-type filter (else derived from project profile / name).",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ProjectRiskScoreResponse:
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return score_project_postmarket(
        db,
        project_id=project_id,
        project=project,
        device_type_override=device_type,
    )


@router.post(
    "/run-pipeline",
    response_model=PostmarketRunPipelineResponse,
    summary="Run end-to-end post-market pipeline for a project",
    description=(
        "Optional stages: openFDA ingest, NLP extraction on pending MAUDE rows, project risk scoring. "
        "Persists a ``postmarket_project_runs`` audit row. MAUDE data are supporting evidence only."
    ),
)
def postmarket_run_pipeline(
    body: PostmarketRunPipelineRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostmarketRunPipelineResponse:
    try:
        return run_postmarket_pipeline(db, user_id=current_user.id, body=body)
    except Exception as e:
        logger.exception("postmarket run-pipeline failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.get(
    "/missing-risks/{project_id}",
    response_model=PostmarketMissingRisksResponse,
    summary="Matched vs unmatched post-market themes and likely FMEA gaps",
)
def get_postmarket_missing_risks(
    project_id: str,
    device_type: Optional[str] = Query(
        None,
        description="Override MAUDE device-type filter for scoring.",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostmarketMissingRisksResponse:
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return build_missing_risks_for_project(
        db,
        project_id=project_id,
        project=project,
        device_type_override=device_type,
    )


@router.post(
    "/add-missing-risk-to-fmea",
    response_model=PostmarketAddMissingRiskToFmeaResponse,
    summary="Create a draft FMEA row from a post-market gap theme",
    description=(
        "Creates an FMEA row with evidence_source=postmarket_maude, draft review flags, and optional "
        "MAUDE event ID linkage. Does not finalize severity/detection — expert review required."
    ),
)
def postmarket_add_missing_risk_to_fmea(
    body: PostmarketAddMissingRiskToFmeaRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostmarketAddMissingRiskToFmeaResponse:
    try:
        return add_missing_postmarket_risk_to_fmea(db, user_id=current_user.id, body=body)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.exception("add-missing-risk-to-fmea failed")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e


@router.post(
    "/report",
    response_model=PostmarketReportResponse,
    summary="Generate structured post-market (MAUDE) report for a project",
    description=(
        "Aggregates NLP-linked MAUDE data, in-scope PMS signals, and optional pipeline snapshots. "
        "Returns ``report_mode`` populated vs draft, ``signals_identified``, ``summary``, and "
        "``recommended_actions``. Intended for expert review; JSON is suitable for future PDF export."
    ),
)
def postmarket_generate_report(
    body: PostmarketReportRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostmarketReportResponse:
    try:
        try:
            payload = body.model_dump(mode="json", default=str)
        except Exception:
            payload = {}
        logger.info(
            "POST /postmarket/report user_id=%s project_id=%s payload=%s",
            current_user.id,
            body.project_id,
            payload,
        )
        resp = build_postmarket_report(db, user_id=current_user.id, body=body)
        if resp.report_mode == "populated":
            try:
                from services.pms_report_document_sync import refresh_pms_report_document_for_project

                refresh_pms_report_document_for_project(
                    db, project_id=body.project_id, user_id=current_user.id
                )
            except Exception:
                logger.exception(
                    "postmarket report: failed to sync pms_report document project=%s",
                    body.project_id,
                )
        return resp
    except ValueError as e:
        logger.warning("POST /postmarket/report not found: %s", e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.exception("postmarket report: unexpected failure after safeguards project=%s", body.project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Post-market report failed: {e}",
        ) from e


@router.post(
    "/refresh-pms-report-document",
    response_model=PmsReportRegenerateDocumentResponse,
    summary="Refresh stored PMS Report document (alias; prefer /report/regenerate-document)",
    description="Same payload as ``POST /postmarket/report/regenerate-document``.",
)
def postmarket_refresh_pms_report_document(
    body: PostmarketRefreshPmsReportBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PmsReportRegenerateDocumentResponse:
    return postmarket_report_regenerate_document(body, db, current_user)


@router.post(
    "/report/regenerate-document",
    response_model=PmsReportRegenerateDocumentResponse,
    summary="Regenerate stored PMS Report document row",
    description=(
        "Builds the PMS report from current MAUDE/signals data, determines draft/populated mode, "
        "upserts the Document Control row (`type=pms_report`), and returns refresh metadata."
    ),
)
def postmarket_report_regenerate_document(
    body: PostmarketRefreshPmsReportBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PmsReportRegenerateDocumentResponse:
    project = project_crud.get_project(db, body.project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied.",
        )
    from services.pms_report_document_sync import regenerate_pms_report_document_for_project

    try:
        result = regenerate_pms_report_document_for_project(
            db,
            project_id=body.project_id,
            user_id=current_user.id,
        )
        return PmsReportRegenerateDocumentResponse(
            project_id=result.project_id,
            report_mode=result.report_mode,
            document_id=result.document_id,
            document_key=result.document_key,
            created_new_document=result.created_new_document,
            updated_existing_document=result.updated_existing_document,
            previous_document_found=result.previous_document_found,
            updated_at=result.updated_at.isoformat() if result.updated_at else None,
            preview_excerpt=result.preview_excerpt,
            linked_maude_rows_count=result.linked_maude_rows_count,
            pms_signal_count=result.pms_signal_count,
            scoring_summary_present=result.scoring_summary_present,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.exception("postmarket report regenerate-document failed project=%s", body.project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PMS report regenerate-document failed: {e}",
        ) from e


@router.post(
    "/report/document-debug",
    response_model=PostmarketPmsDocumentDebugResponse,
    summary="Debug PMS document existence and computed mode",
)
def postmarket_report_document_debug(
    body: PostmarketRefreshPmsReportBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> PostmarketPmsDocumentDebugResponse:
    project = project_crud.get_project(db, body.project_id, current_user.id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found or access denied.",
        )
    from services.pms_report_document_sync import (
        PMS_REPORT_DOCUMENT_NAME,
        PMS_REPORT_DOCUMENT_TYPE,
        _scoring_summary_present,
    )
    from services.postmarket_report import build_postmarket_report

    doc = None
    try:
        from crud import document as document_crud

        docs = document_crud.get_documents_by_project(db, body.project_id)
        for d in docs:
            if (d.type or "").strip().lower() == PMS_REPORT_DOCUMENT_TYPE:
                doc = d
                break
    except Exception:
        logger.exception("document-debug: failed reading documents table")
    report = build_postmarket_report(
        db,
        user_id=current_user.id,
        body=PostmarketReportRequest(project_id=body.project_id),
    )
    content = (doc.content or "") if doc else ""
    return PostmarketPmsDocumentDebugResponse(
        project_id=body.project_id,
        expected_document_type=PMS_REPORT_DOCUMENT_TYPE,
        expected_document_name=PMS_REPORT_DOCUMENT_NAME,
        document_found=doc is not None,
        document_id=doc.id if doc else None,
        document_type_actual=doc.type if doc else None,
        document_name_actual=doc.name if doc else None,
        document_updated_at=doc.updated_at.isoformat() if doc and doc.updated_at else None,
        contains_legacy_no_data_text=("no pms data included" in content.lower()),
        linked_maude_rows_count=report.summary.maude_nlp_linked_records_reviewed,
        pms_signal_count=report.summary.pms_signal_records_in_scope,
        scoring_summary_present=_scoring_summary_present(db, body.project_id),
        computed_report_mode=report.report_mode,
    )
