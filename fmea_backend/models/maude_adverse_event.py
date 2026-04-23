"""
Persisted openFDA device adverse event (MAUDE) records after ingestion.

Works with PostgreSQL (JSONB-friendly via SQLAlchemy JSON) and SQLite (JSON as text).
"""
from __future__ import annotations

import uuid

from sqlalchemy import Column, String, Text, DateTime, Date, Integer, JSON, UniqueConstraint, Index
from sqlalchemy.sql import func

from database import Base


class MaudeAdverseEvent(Base):
    """
    One row per (FDA report number, device sequence) from a MAUDE device/event export.

    Deduplication: unique on (source_system, source_report_key, device_sequence).
    """

    __tablename__ = "maude_adverse_events"
    __table_args__ = (
        UniqueConstraint(
            "source_system",
            "source_report_key",
            "device_sequence",
            name="uq_maude_adverse_event_source_report_device",
        ),
        Index("ix_maude_adverse_events_date_received", "date_received"),
        Index("ix_maude_adverse_events_manufacturer", "manufacturer"),
        Index("ix_maude_adverse_events_normalized_device", "normalized_device_name"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    # Dedup identity (openFDA: report_number + device_sequence_number)
    source_system = Column(String(64), nullable=False, default="openfda_maude", index=True)
    source_report_key = Column(String(512), nullable=False, index=True)
    device_sequence = Column(Integer, nullable=False, default=0)

    # Raw payload for audit / reprocessing (single device slice or full report per your ingest policy)
    raw_record = Column(JSON, nullable=False)

    # Normalized / query-friendly fields
    normalized_device_name = Column(Text, nullable=True)
    event_type = Column(String(512), nullable=True)
    narrative_text = Column(Text, nullable=True)
    manufacturer = Column(Text, nullable=True)
    brand_name = Column(Text, nullable=True)
    generic_name = Column(Text, nullable=True)
    date_received = Column(Date, nullable=True, index=True)
    product_code = Column(String(64), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
