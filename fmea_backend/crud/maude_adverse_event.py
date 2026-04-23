"""CRUD helpers for MAUDE adverse event persistence."""
from __future__ import annotations

from datetime import date
from typing import List, Optional

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from models.maude_adverse_event import MaudeAdverseEvent
from models.maude_nlp_extraction import MaudeNlpExtraction


def exists_dedup_key(
    db: Session,
    *,
    source_system: str,
    source_report_key: str,
    device_sequence: int,
) -> bool:
    found = (
        db.query(MaudeAdverseEvent.id)
        .filter(MaudeAdverseEvent.source_system == source_system)
        .filter(MaudeAdverseEvent.source_report_key == source_report_key)
        .filter(MaudeAdverseEvent.device_sequence == device_sequence)
        .first()
    )
    return found is not None


def insert_event(db: Session, row: MaudeAdverseEvent) -> MaudeAdverseEvent:
    db.add(row)
    db.flush()
    return row


def _device_type_clause(device_type: str):
    dt = (device_type or "").strip()
    if not dt:
        return None
    like = f"%{dt}%"
    return or_(
        MaudeAdverseEvent.generic_name.ilike(like),
        MaudeAdverseEvent.normalized_device_name.ilike(like),
        MaudeAdverseEvent.brand_name.ilike(like),
    )


def _date_clause(date_from: Optional[date], date_to: Optional[date]):
    clauses = []
    if date_from is not None:
        clauses.append(MaudeAdverseEvent.date_received >= date_from)
    if date_to is not None:
        clauses.append(MaudeAdverseEvent.date_received <= date_to)
    if not clauses:
        return None
    return and_(*clauses)


def list_event_ids_missing_extraction(
    db: Session,
    *,
    device_type: str,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = 500,
) -> List[str]:
    """
    MAUDE events in the device/date window that have narrative text but no NLP extraction row yet.
    """
    dc = _device_type_clause(device_type)
    if dc is None:
        return []

    q = (
        db.query(MaudeAdverseEvent.id)
        .outerjoin(MaudeNlpExtraction, MaudeNlpExtraction.maude_event_id == MaudeAdverseEvent.id)
        .filter(dc)
        .filter(MaudeNlpExtraction.id.is_(None))
        .filter(MaudeAdverseEvent.narrative_text.isnot(None))
        .filter(MaudeAdverseEvent.narrative_text != "")
    )
    dclause = _date_clause(date_from, date_to)
    if dclause is not None:
        q = q.filter(dclause)

    rows = q.order_by(MaudeAdverseEvent.date_received.desc()).limit(limit).all()
    return [r[0] for r in rows]
