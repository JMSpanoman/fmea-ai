"""Persisted PMS plan generations (FMEA + MAUDE signals + AI sections)."""
from __future__ import annotations

import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class PmsGeneratedPlan(Base):
    """
    Database-backed PMS plan artifact.
    `id` matches `generation_id` returned by POST /pms/generate and AI event context_id.
    """

    __tablename__ = "pms_generated_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    device_name = Column(String(512), nullable=False)
    intended_use = Column(Text, nullable=False)
    summary = Column(Text, nullable=True)
    status = Column(String(32), nullable=False, default="draft", index=True)  # draft | final
    version = Column(Integer, nullable=False, default=1)

    # Full snapshot: sections dict, maude_signals, fmea_row_count, model, ai_generated, warning (optional)
    payload_json = Column(JSON, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    project = relationship("Project", back_populates="pms_generated_plans")
    user = relationship("User", foreign_keys=[user_id])
