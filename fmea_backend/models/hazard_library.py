"""Reusable Hazard Library for medical device risk management (ISO 14971)."""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid


class HazardLibrary(Base):
    """
    Library of reusable hazard definitions.
    Referenced by hazard analysis items and FMEA to ensure consistent terminology
    and to support auto-generation of risk analysis content.
    """
    __tablename__ = "hazard_library"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    hazard_id = Column(String(64), nullable=True, unique=True, index=True)  # e.g. HZ-001
    category = Column(String(128), nullable=True, index=True)  # e.g. electrical, mechanical, use
    hazard_name = Column(String(256), nullable=False, index=True)
    description = Column(Text, nullable=True)
    typical_hazardous_situation = Column(Text, nullable=True)
    typical_harms = Column(Text, nullable=True)
    example_controls = Column(Text, nullable=True)
    verification_examples = Column(Text, nullable=True)
    lifecycle_phase = Column(String(128), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
