from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class ProjectProfile(Base):
    """
    Project-level device context (1:1 with Project).
    This is intentionally separate from the Project model to avoid changing existing Project APIs.
    """

    __tablename__ = "project_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, unique=True, index=True)

    intended_use = Column(Text, nullable=True)
    device_description = Column(Text, nullable=True)
    user_population = Column(String, nullable=True)
    use_environment = Column(String, nullable=True)
    key_safety_characteristics = Column(JSON, nullable=True)  # list[str] (or simple JSON)

    # ISO 14971-style project-level attestations for overall residual risk acceptability (RMF / RMR).
    overall_device_benefit_risk_profile_acceptable = Column(Boolean, nullable=True)
    rmr_overall_residual_risk_conclusion_documented = Column(Boolean, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="profile")

