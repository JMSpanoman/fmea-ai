"""Persistence helpers for post-market pipeline runs and FMEA evidence linkage."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from models.postmarket_intelligence import PostmarketFmeaEvidenceLink, PostmarketProjectRun


def create_project_run(
    db: Session,
    *,
    project_id: str,
    status: str,
    request_snapshot: Optional[Dict[str, Any]] = None,
    records_fetched: int = 0,
    records_inserted: int = 0,
    records_skipped: int = 0,
    records_extracted: int = 0,
    extracted_failure_modes_count: int = 0,
    scoring_summary: Optional[Dict[str, Any]] = None,
    top_missing_risks: Optional[List[Dict[str, Any]]] = None,
    warnings: Optional[List[str]] = None,
    error_message: Optional[str] = None,
    completed_at: Optional[datetime] = None,
) -> PostmarketProjectRun:
    row = PostmarketProjectRun(
        project_id=project_id,
        status=status,
        completed_at=completed_at,
        request_snapshot=request_snapshot,
        records_fetched=records_fetched,
        records_inserted=records_inserted,
        records_skipped=records_skipped,
        records_extracted=records_extracted,
        extracted_failure_modes_count=extracted_failure_modes_count,
        scoring_summary=scoring_summary,
        top_missing_risks=top_missing_risks,
        warnings=warnings or [],
        error_message=error_message,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def create_fmea_evidence_link(
    db: Session,
    *,
    project_id: str,
    fmea_row_id: str,
    normalized_failure_mode: str,
    maude_event_ids: List[str],
) -> PostmarketFmeaEvidenceLink:
    row = PostmarketFmeaEvidenceLink(
        project_id=project_id,
        fmea_row_id=fmea_row_id,
        normalized_failure_mode=normalized_failure_mode,
        maude_event_ids=list(maude_event_ids or []),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row
