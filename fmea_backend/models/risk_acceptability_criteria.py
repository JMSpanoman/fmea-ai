"""
Models for Risk Acceptability Criteria report and configuration (ISO 14971).
Supports 3-tier precedence: project-approved → org default → system draft.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON, Boolean
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
    status = Column(String(50), nullable=False, default="draft", index=True)  # draft, in_review, pending_approval, approved, obsolete
    title = Column(String(500), nullable=True)

    # Full report as structured JSON (all sections + metadata)
    content_json = Column(Text, nullable=True)
    sections_json = Column(Text, nullable=True)
    content_html = Column(Text, nullable=True)
    section_document_version = Column(Integer, nullable=False, default=1)

    # Source metadata: which tier each section came from
    source_metadata = Column(JSON, nullable=True)
    section_metadata = Column(JSON, nullable=True)  # source/completeness/review flags and section approvals
    readiness_metrics = Column(JSON, nullable=True)  # completeness %, approved %, blocked reasons
    review_comments = Column(JSON, nullable=True)  # section-level comments
    approval_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    supersedes_id = Column(String, ForeignKey("risk_acceptability_criteria.id"), nullable=True)

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
    organization_id = Column(String(255), nullable=True, index=True)
    name = Column(String(255), nullable=False, default="default")  # e.g. "default", "EU", "FDA"
    template_name = Column(String(255), nullable=True)
    severity_scale = Column(JSON, nullable=True)  # [{level, label, definition}, ...]
    probability_scale = Column(JSON, nullable=True)
    risk_matrix = Column(JSON, nullable=True)  # severity x probability -> acceptability
    decision_rules = Column(Text, nullable=True)
    severity_rationale = Column(Text, nullable=True)
    probability_rationale = Column(Text, nullable=True)
    matrix_rationale = Column(Text, nullable=True)
    decision_rules_rationale = Column(Text, nullable=True)
    overall_residual_risk_methods = Column(JSON, nullable=True)
    terminology_overrides = Column(JSON, nullable=True)
    approval_policy = Column(JSON, nullable=True)
    is_approved = Column(Boolean, nullable=False, default=False)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
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
    terminology_overrides = Column(JSON, nullable=True)
    severity_rationale = Column(Text, nullable=True)
    probability_rationale = Column(Text, nullable=True)
    matrix_rationale = Column(Text, nullable=True)
    decision_rules_rationale = Column(Text, nullable=True)
    overall_residual_risk_methods = Column(JSON, nullable=True)
    workflow_state = Column(String(50), nullable=False, default="draft", index=True)  # draft, in_review, pending_approval, approved, obsolete
    approved_by = Column(String, ForeignKey("users.id"), nullable=True, index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_notes = Column(Text, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", backref="risk_criteria_overrides")
