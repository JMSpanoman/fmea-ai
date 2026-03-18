"""Project risk controls: controls linked to a project risk item, optionally from risk control library."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class ProjectRiskControl(Base):
    """
    Risk control associated with a project risk item.
    May reference the risk_control_library or hold free-text control_text.
    """
    __tablename__ = "project_risk_controls"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_risk_item_id = Column(
        String, ForeignKey("project_risk_items.id"), nullable=False, index=True
    )
    risk_control_library_id = Column(
        String, ForeignKey("risk_control_library.id"), nullable=True, index=True
    )
    control_text = Column(Text, nullable=True)
    implementation_reference = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project_risk_item = relationship(
        "ProjectRiskItem", back_populates="controls", foreign_keys=[project_risk_item_id]
    )
    risk_control_library = relationship(
        "RiskControlLibrary", foreign_keys=[risk_control_library_id]
    )
    verifications = relationship(
        "ProjectVerification",
        back_populates="project_risk_control",
        cascade="all, delete-orphan",
    )
