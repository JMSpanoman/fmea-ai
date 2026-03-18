"""Project verifications: verification records linked to a project risk control."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class ProjectVerification(Base):
    """
    Verification associated with a project risk control.
    May reference the verification_library or hold free-text verification_text.
    """
    __tablename__ = "project_verifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_risk_control_id = Column(
        String, ForeignKey("project_risk_controls.id"), nullable=False, index=True
    )
    verification_library_id = Column(
        String, ForeignKey("verification_library.id"), nullable=True, index=True
    )
    verification_text = Column(Text, nullable=True)
    evidence_reference = Column(Text, nullable=True)
    status = Column(String(64), nullable=False, default="pending", index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project_risk_control = relationship(
        "ProjectRiskControl", back_populates="verifications", foreign_keys=[project_risk_control_id]
    )
    verification_library = relationship(
        "VerificationLibrary", foreign_keys=[verification_library_id]
    )
