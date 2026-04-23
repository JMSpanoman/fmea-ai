"""
Post-market intelligence persistence: pipeline runs, FMEA evidence linkage.

EXTENSION_POINTS (audit / versioning — not implemented here):
    - Add ``version`` + ``supersedes_run_id`` on ``PostmarketProjectRun`` for immutable audit trails.
    - Add ``created_by_user_id`` FK to ``users`` on runs and evidence links.
    - Tie ``PostmarketFmeaEvidenceLink`` to CAPA / complaints via nullable FKs when those feeds are wired.
    - FDA recall rows can mirror ``MaudeAdverseEvent`` pattern with ``source_system='openfda_recall'``.
"""
from __future__ import annotations

import uuid

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Index, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class PostmarketProjectRun(Base):
    """
    One record per invocation of the orchestrated post-market pipeline for a project.

    Stores denormalized counters and scoring snapshot JSON for dashboards and compliance snapshots.
    """

    __tablename__ = "postmarket_project_runs"
    __table_args__ = (
        Index("ix_postmarket_project_runs_project_id", "project_id"),
        Index("ix_postmarket_project_runs_started_at", "started_at"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    status = Column(String(32), nullable=False, default="completed")
    """completed | partial | failed"""

    request_snapshot = Column(JSON, nullable=True)
    """Sanitized copy of pipeline request for replay / support."""

    records_fetched = Column(Integer, nullable=False, default=0)
    records_inserted = Column(Integer, nullable=False, default=0)
    records_skipped = Column(Integer, nullable=False, default=0)
    records_extracted = Column(Integer, nullable=False, default=0)
    extracted_failure_modes_count = Column(Integer, nullable=False, default=0)

    scoring_summary = Column(JSON, nullable=True)
    top_missing_risks = Column(JSON, nullable=True)
    warnings = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)

    project = relationship("Project", backref="postmarket_runs")


class PostmarketFmeaEvidenceLink(Base):
    """
    Links a draft FMEA row created from post-market analysis to supporting MAUDE event IDs.

    FK to ``fmea_rows`` ensures traceability; ``maude_event_ids`` is a JSON list of string UUIDs.
    """

    __tablename__ = "postmarket_fmea_evidence_links"
    __table_args__ = (
        Index("ix_postmarket_fmea_evidence_project", "project_id"),
        Index("ix_postmarket_fmea_evidence_fmea_row", "fmea_row_id"),
    )

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    fmea_row_id = Column(String, ForeignKey("fmea_rows.id", ondelete="CASCADE"), nullable=False)

    normalized_failure_mode = Column(Text, nullable=False)
    maude_event_ids = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    project = relationship("Project", backref="postmarket_fmea_evidence_links")
    fmea_row = relationship("FMEARow", backref="postmarket_evidence_links")
