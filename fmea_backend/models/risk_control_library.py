"""Reusable Risk Control Library for medical device risk management (ISO 14971)."""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid


class RiskControlLibrary(Base):
    """
    Library of reusable risk control measures (design, protective, information).
    Referenced by risk controls and FMEA mitigations to ensure consistent control types
    and to support auto-generation of risk control documentation.
    """
    __tablename__ = "risk_control_library"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    control_id = Column(String(64), nullable=True, unique=True, index=True)  # e.g. RC-001
    control_name = Column(String(256), nullable=False, index=True)
    control_type = Column(String(64), nullable=False, index=True)  # design | protective | information
    description = Column(Text, nullable=True)
    example_application = Column(Text, nullable=True)
    typical_verification_method = Column(Text, nullable=True)
    related_standards = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
