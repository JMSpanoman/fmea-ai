"""
Structured NLP extraction from MAUDE adverse-event narratives (LLM-assisted).

Linked 1:1 to ``maude_adverse_events`` (re-runs replace the same row by ``maude_event_id``).
"""
from __future__ import annotations

import uuid

from sqlalchemy import Column, String, Text, DateTime, Float, ForeignKey, JSON, UniqueConstraint, Index
from sqlalchemy.orm import backref, relationship
from sqlalchemy.sql import func

from database import Base


class MaudeNlpExtraction(Base):
    __tablename__ = "maude_nlp_extractions"
    __table_args__ = (
        UniqueConstraint("maude_event_id", name="uq_maude_nlp_extraction_event"),
        Index("ix_maude_nlp_outcome", "outcome_classification"),
        Index("ix_maude_nlp_normalized_phrase", "normalized_risk_phrase"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    maude_event_id = Column(
        String,
        ForeignKey("maude_adverse_events.id", ondelete="CASCADE"),
        nullable=False,
    )

    failure_mode = Column(Text, nullable=True)
    cause = Column(Text, nullable=True)
    effect = Column(Text, nullable=True)
    component = Column(Text, nullable=True)
    harm = Column(Text, nullable=True)
    outcome_classification = Column(String(32), nullable=True, index=True)
    confidence_score = Column(Float, nullable=True)
    normalized_risk_phrase = Column(Text, nullable=True)

    llm_model = Column(String(128), nullable=True)
    raw_llm_response = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    maude_event = relationship(
        "MaudeAdverseEvent",
        backref=backref("nlp_extraction", uselist=False),
        foreign_keys=[maude_event_id],
    )
