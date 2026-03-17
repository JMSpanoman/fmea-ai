"""Reusable Harm Library for medical device risk management (ISO 14971)."""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid


class HarmLibrary(Base):
    """
    Library of reusable harm definitions (clinical outcomes / types of harm).
    Referenced by hazard analysis and FMEA effects to ensure consistent severity
    and to support auto-generation of risk analysis reports.
    """
    __tablename__ = "harm_library"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    harm_id = Column(String(64), nullable=True, unique=True, index=True)  # e.g. HR-001
    harm_name = Column(String(256), nullable=False, index=True)
    description = Column(Text, nullable=True)
    severity_guidance = Column(Text, nullable=True)  # guidance on severity (text)
    clinical_examples = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
