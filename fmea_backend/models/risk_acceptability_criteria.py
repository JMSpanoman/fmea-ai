"""
Models for Risk Acceptability Criteria report and configuration (ISO 14971).
Supports 3-tier precedence: project-approved → org default → system draft.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class RiskAcceptabilityCriteria(Base):
    """
    Generated Risk Acceptability Criteria report (one per project version).
    Stores full structured JSON and rendered HTML; supports versioning.
    """
    __tablename__ = "risk_acceptability_criteria"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    status = Column(String(50), nullable=False, default="draft", index=True)  # draft, in_review, approved
    title = Column(String(500), nullable=True)

    # Full report as structured JSON (all sections + metadata)
    content_json = Column(Text, nullable=True)
    content_html = Column(Text, nullable=True)

    # Source metadata: which tier each section came from
    source_metadata = Column(JSON, nullable=True)

    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    generated_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", backref="risk_acceptability_criteria_reports")
    generator = relationship("User", foreign_keys=[generated_by])
    approver = relationship("User", foreign_keys=[approved_by])


class OrganizationRiskCriteriaConfig(Base):
    """
    Organization-level default criteria (severity scale, probability scale, risk matrix).
    When no project override exists, these are used. Single row per "org" or global default.
    """
    __tablename__ = "organization_risk_criteria_configs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String(255), nullable=False, default="default")  # e.g. "default", "EU", "FDA"
    severity_scale = Column(JSON, nullable=True)  # [{level, label, definition}, ...]
    probability_scale = Column(JSON, nullable=True)
    risk_matrix = Column(JSON, nullable=True)  # severity x probability -> acceptability
    decision_rules = Column(Text, nullable=True)
    terminology_overrides = Column(JSON, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProjectRiskCriteriaOverride(Base):
    """
    Project-specific approved overrides. When set, these take precedence over org config.
    """
    __tablename__ = "project_risk_criteria_overrides"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    severity_scale = Column(JSON, nullable=True)
    probability_scale = Column(JSON, nullable=True)
    risk_matrix = Column(JSON, nullable=True)
    decision_rules = Column(Text, nullable=True)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", backref="risk_criteria_overrides")
