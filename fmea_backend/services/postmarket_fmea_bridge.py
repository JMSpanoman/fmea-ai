"""
Create draft FMEA rows from post-market gap themes with explicit provenance.

EXTENSION:
    - Link ``PostmarketFmeaEvidenceLink`` to CAPA IDs when complaint/CAPA integration is added.
    - Append audit_log_event rows when audit trail service is unified.
"""
from __future__ import annotations

import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from crud import fmea as fmea_crud
from crud import postmarket_intelligence as pm_intel_crud
from crud import project as project_crud
from models.component import Component
from schemas.fmea import FMEARowCreate
from schemas.postmarket_pipeline import PostmarketAddMissingRiskToFmeaRequest, PostmarketAddMissingRiskToFmeaResponse
from schemas.postmarket_risk_scoring import FailureModeScoreRequest
from services.risk_scoring import resolve_device_type_for_postmarket, score_failure_mode_request

logger = logging.getLogger(__name__)

EVIDENCE_SOURCE_POSTMARKET = "postmarket_maude"
REVIEW_STATUS_DRAFT = "draft_expert_review"


def _resolve_component_id(db: Session, project_id: str, component: Optional[str]) -> Optional[str]:
    if not component or not str(component).strip():
        return None
    name = str(component).strip()
    row = (
        db.query(Component.id)
        .filter(Component.project_id == project_id)
        .filter(Component.name.ilike(name))
        .first()
    )
    return row[0] if row else None


def _suggested_probability(
    db: Session, *, device_type: str, failure_mode: str, component: Optional[str]
) -> Optional[int]:
    try:
        body = FailureModeScoreRequest(
            device_type=device_type,
            failure_mode=failure_mode,
            component=component,
        )
        res = score_failure_mode_request(db, body)
        return int(res.suggested_probability_score)
    except Exception:
        logger.info("Could not derive suggested probability for post-market FMEA draft", exc_info=True)
        return None


def add_missing_postmarket_risk_to_fmea(
    db: Session,
    *,
    user_id: str,
    body: PostmarketAddMissingRiskToFmeaRequest,
) -> PostmarketAddMissingRiskToFmeaResponse:
    project = project_crud.get_project(db, body.project_id, user_id)
    if not project:
        raise ValueError("Project not found")

    device_type_for_scoring = (body.device_type or "").strip() or resolve_device_type_for_postmarket(
        db, project_id=body.project_id, project=project
    )

    prob = _suggested_probability(
        db,
        device_type=device_type_for_scoring,
        failure_mode=body.normalized_failure_mode,
        component=body.component,
    )

    effect = body.suggested_effect or (
        "Potential patient or user impact from reported post-market theme — define per ISO 14971 analysis."
    )
    cause = body.suggested_cause or (
        "Cause to be determined — review linked MAUDE narratives and design history."
    )

    evidence_lines = [
        "Source: FDA MAUDE / openFDA-derived post-market NLP theme.",
        f"Normalized failure-mode theme: {body.normalized_failure_mode}.",
    ]
    if body.component:
        evidence_lines.append(f"Component context: {body.component}.")
    if prob is not None:
        evidence_lines.append(f"Suggested probability (1–5) from MAUDE-weighted heuristic: {prob} (review required).")
    summary = "\n".join(evidence_lines)

    ai_meta = {
        "source": EVIDENCE_SOURCE_POSTMARKET,
        "review_required": True,
        "normalized_failure_mode": body.normalized_failure_mode,
        "postmarket_suggested_probability": prob,
    }
    ai_suggested = {
        "postmarket_suggested_probability": prob,
        "source": EVIDENCE_SOURCE_POSTMARKET,
    }

    component_id = _resolve_component_id(db, body.project_id, body.component)

    create = FMEARowCreate(
        project_id=body.project_id,
        component_id=component_id,
        failure_mode=body.normalized_failure_mode,
        effect=effect,
        cause=cause,
        probability=prob,
        severity=None,
        detection=None,
        mitigation=None,
        evidence_source=EVIDENCE_SOURCE_POSTMARKET,
        postmarket_review_status=REVIEW_STATUS_DRAFT,
        postmarket_evidence_summary=summary,
        ai_metadata=ai_meta,
        ai_suggested_values_json=ai_suggested,
        acceptable_for_release=False,
        approval_blocked=True,
    )

    row = fmea_crud.create_fmea_row(db, create)

    event_ids: List[str] = list(body.source_event_ids or [])
    pm_intel_crud.create_fmea_evidence_link(
        db,
        project_id=body.project_id,
        fmea_row_id=row.id,
        normalized_failure_mode=body.normalized_failure_mode,
        maude_event_ids=event_ids,
    )

    return PostmarketAddMissingRiskToFmeaResponse(fmea_row_id=row.id)
