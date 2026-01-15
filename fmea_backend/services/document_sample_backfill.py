from __future__ import annotations

from sqlalchemy.orm import Session
from typing import Dict, Any

from crud import document as document_crud
from models.document import Document
from schemas.document import DocumentUpdate


DEFAULT_SAMPLE_MARKERS = [
    "DRAFT — Generated from Project Setup",
    "DRAFT — Generated deterministically from ProjectProfile + Components",
]


def backfill_default_sample_flags(db: Session) -> Dict[str, Any]:
    """
    Best-effort: mark documents that already contain SmartQS-provided starter content so
    the UI can hide the 'Generate AI sample' button consistently using ai_metadata flags.

    This does NOT modify document content and does NOT create a new version.
    """
    docs = db.query(Document).all()
    updated = 0
    scanned = 0
    for d in docs:
        scanned += 1
        meta0 = d.ai_metadata if isinstance(getattr(d, "ai_metadata", None), dict) else {}
        if meta0.get("default_sample_provided") is True or meta0.get("ai_sample_generated") is True:
            continue
        c = (d.content or "")
        if not c:
            continue
        if not any(m in c for m in DEFAULT_SAMPLE_MARKERS):
            continue
        document_crud.update_document(  # no version bump: only ai_metadata changes
            db,
            d.id,
            DocumentUpdate(ai_metadata={**meta0, "default_sample_provided": True, "source": "starter_content_backfill"}),
            d.project_id,
        )
        updated += 1
    return {"scanned": scanned, "updated": updated}

