"""Reusable Verification Method Library for medical device risk management."""
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from database import Base
import uuid


class VerificationLibrary(Base):
    """
    Library of reusable verification methods.
    Referenced by risk controls and V&V to ensure consistent verification approaches
    and to support auto-generation of verification plans and FMEA rows.
    """
    __tablename__ = "verification_library"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    verification_id = Column(String(64), nullable=True, unique=True, index=True)  # e.g. V-001
    verification_method = Column(String(256), nullable=False, index=True)
    description = Column(Text, nullable=True)
    applicable_control_types = Column(Text, nullable=True)  # e.g. design, protective, information
    standard_reference = Column(Text, nullable=True)
    typical_test_output = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
