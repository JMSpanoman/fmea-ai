"""Persistence for MAUDE NLP extractions (one row per maude_event_id)."""
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models.maude_nlp_extraction import MaudeNlpExtraction


def get_by_event_id(db: Session, maude_event_id: str) -> Optional[MaudeNlpExtraction]:
    return (
        db.query(MaudeNlpExtraction)
        .filter(MaudeNlpExtraction.maude_event_id == maude_event_id)
        .first()
    )


def upsert_extraction(db: Session, maude_event_id: str, fields: Dict[str, Any]) -> MaudeNlpExtraction:
    row = get_by_event_id(db, maude_event_id)
    if row:
        for k, v in fields.items():
            if hasattr(row, k):
                setattr(row, k, v)
        db.flush()
        return row
    row = MaudeNlpExtraction(maude_event_id=maude_event_id, **fields)
    db.add(row)
    db.flush()
    return row
