"""
Versioned, project-scoped risk acceptability rule criteria for the deterministic rule engine.

Separate from RiskAcceptabilityCriteria (narrative RAC report) and ProjectRiskCriteriaOverride
(matrix overrides for document generation). This model powers row-level FMEA evaluation.
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class ProjectRiskCriteria(Base):
    """
    Project-specific configurable criteria: scales, matrix, score thresholds, special rules JSON.
    Versioned; only one 'approved' active version should be used for formal evaluation (configurable).
    """

    __tablename__ = "project_risk_criteria"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    version = Column(Integer, nullable=False, default=1)
    status = Column(String(32), nullable=False, default="draft", index=True)  # draft, approved, archived

    evaluation_method = Column(String(32), nullable=False, default="matrix")  # matrix, score, hybrid

    severity_scale = Column(JSON, nullable=True)
    probability_scale = Column(JSON, nullable=True)
    detection_scale = Column(JSON, nullable=True)
    risk_matrix = Column(JSON, nullable=True)
    score_thresholds = Column(JSON, nullable=True)
    special_rules = Column(JSON, nullable=True)

    approval_metadata = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", backref="project_risk_criteria_versions")


class RuleEvaluationAudit(Base):
    """Immutable audit trail for each deterministic evaluation run on an FMEA row."""

    __tablename__ = "rule_evaluation_audits"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    fmea_row_id = Column(String, ForeignKey("fmea_rows.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    criteria_version = Column(Integer, nullable=False)

    evaluation_type = Column(String(32), nullable=False)  # initial, residual

    inputs_json = Column(JSON, nullable=True)
    matched_rules_json = Column(JSON, nullable=True)
    output_json = Column(JSON, nullable=True)
    decision_path_text = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    fmea_row = relationship("FMEARow", backref="rule_evaluation_audits")
