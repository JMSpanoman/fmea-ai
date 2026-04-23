"""
Match post-market failure-mode themes to existing project FMEA rows (rule-based).

Future: swap ``find_matching_fmea_row`` implementation for embedding similarity or
admin-configured synonym tables without changing API contracts.
"""
from __future__ import annotations

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from crud import fmea as fmea_crud
from models.project import Project
from schemas.postmarket_pipeline import (
    PostmarketMatchedThemeOut,
    PostmarketMissingRisksResponse,
    PostmarketUnmatchedThemeOut,
)
from services.risk_scoring import _norm_text, _postmarket_covers_fmea, score_project_postmarket


def find_matching_fmea_row(
    db: Session, project_id: str, postmarket_normalized_key: str
) -> Tuple[Optional[str], Optional[str]]:
    """Returns (fmea_row_id, failure_mode_text) when a project FMEA row covers the theme."""
    if not postmarket_normalized_key or postmarket_normalized_key == "unknown":
        return None, None
    for row in fmea_crud.get_fmea_rows_by_project(db, project_id):
        n = _norm_text(row.failure_mode)
        if len(n) < 3:
            continue
        if _postmarket_covers_fmea(postmarket_normalized_key, {n}):
            return row.id, (row.failure_mode or n)
    return None, None


def build_missing_risks_for_project(
    db: Session,
    *,
    project_id: str,
    project: Project,
    device_type_override: Optional[str] = None,
) -> PostmarketMissingRisksResponse:
    """
    Helper: full scoring response split into matched / unmatched / likely-missing lists.
    """
    score = score_project_postmarket(
        db,
        project_id=project_id,
        project=project,
        device_type_override=device_type_override,
    )
    matched: List[PostmarketMatchedThemeOut] = []
    unmatched: List[PostmarketUnmatchedThemeOut] = []

    for it in score.items:
        rid, rfm = find_matching_fmea_row(db, project_id, it.normalized_failure_mode)
        if rid:
            matched.append(
                PostmarketMatchedThemeOut(
                    normalized_failure_mode=it.normalized_failure_mode,
                    suggested_probability_score=it.suggested_probability_score,
                    supporting_event_count=it.supporting_event_count,
                    weighted_event_count=it.weighted_event_count,
                    matched_fmea_row_id=rid,
                    matched_fmea_failure_mode=rfm,
                )
            )
        else:
            unmatched.append(
                PostmarketUnmatchedThemeOut(
                    normalized_failure_mode=it.normalized_failure_mode,
                    suggested_probability_score=it.suggested_probability_score,
                    supporting_event_count=it.supporting_event_count,
                    weighted_event_count=it.weighted_event_count,
                )
            )

    return PostmarketMissingRisksResponse(
        project_id=project_id,
        device_type_used=score.device_type_used,
        date_from=score.date_from,
        date_to=score.date_to,
        matched_themes=matched,
        unmatched_themes=unmatched,
        likely_missing_risks=score.suggested_missing_risks,
    )
