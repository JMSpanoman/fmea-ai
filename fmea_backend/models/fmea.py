from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Numeric, JSON, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class FMEARow(Base):
    __tablename__ = "fmea_rows"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    component_id = Column(String, ForeignKey("components.id"), nullable=True, index=True)
    
    # FMEA fields
    device_function = Column(Text, nullable=True)  # row-level function (optional; component may also define scope)
    failure_mode = Column(Text, nullable=True)
    effect = Column(Text, nullable=True)
    cause = Column(Text, nullable=True)
    hazard = Column(Text, nullable=True)  # hazardous situation / scenario (free text, traceability)
    harm = Column(Text, nullable=True)  # harm description (free text)
    severity = Column(Integer, nullable=True)
    probability = Column(Integer, nullable=True)
    detection = Column(Integer, nullable=True)
    rpn = Column(Integer, nullable=True)  # Auto-calculated: severity * probability * detection
    mitigation = Column(Text, nullable=True)
    action_taken = Column(Text, nullable=True)  # post-mitigation / implemented action narrative
    
    # Residual risk fields
    residual_severity = Column(Integer, nullable=True)
    residual_probability = Column(Integer, nullable=True)
    residual_detection = Column(Integer, nullable=True)
    residual_rpn = Column(Integer, nullable=True)  # Auto-calculated: residual_severity * residual_probability * residual_detection

    # Risk acceptability rule engine (deterministic; ISO 14971–aligned workflow flags)
    initial_risk_classification = Column(String(32), nullable=True)  # Acceptable | ALARP | Unacceptable
    residual_risk_classification = Column(String(32), nullable=True)
    benefit_risk_required = Column(Boolean, nullable=False, default=False)
    reviewer_justification = Column(Text, nullable=True)
    reviewer_name = Column(String(255), nullable=True)
    reviewer_date = Column(DateTime(timezone=True), nullable=True)
    critical_function_flag = Column(Boolean, nullable=False, default=False)
    approval_blocked = Column(Boolean, nullable=False, default=False)
    # Derived from rule_engine_result_json on each evaluation (AND across stored phases).
    acceptable_for_release = Column(Boolean, nullable=False, default=True)
    # Attestations for mandatory release policies (ISO 14971 workflow; read by rule engine)
    benefit_risk_formal_approval_recorded = Column(Boolean, nullable=False, default=False)
    # Structured benefit–risk analysis (documentation + multi-party acceptance)
    bra_clinical_benefit_documented = Column(Boolean, nullable=False, default=False)
    bra_benefit_vs_residual_risk_documented = Column(Boolean, nullable=False, default=False)
    bra_state_of_the_art_documented = Column(Boolean, nullable=False, default=False)
    bra_supporting_evidence_addressed = Column(Boolean, nullable=False, default=False)
    bra_approval_clinical_medical_recorded = Column(Boolean, nullable=False, default=False)
    bra_approval_quality_regulatory_recorded = Column(Boolean, nullable=False, default=False)
    bra_approval_design_authority_recorded = Column(Boolean, nullable=False, default=False)
    cross_functional_review_completed = Column(Boolean, nullable=False, default=False)
    formal_release_approval_recorded = Column(Boolean, nullable=False, default=False)
    additional_controls_reduced_risk = Column(Boolean, nullable=False, default=False)
    benefit_risk_analysis_approved = Column(Boolean, nullable=False, default=False)
    # Critical hazard policy (life-sustaining device) — attestations + aggregates from rule engine
    critical_hazard_severity_floor_waived = Column(Boolean, nullable=False, default=False)
    risk_eliminated = Column(Boolean, nullable=False, default=False)
    system_level_verification_recorded = Column(Boolean, nullable=False, default=False)
    critical_hazard_category_flag = Column(Boolean, nullable=False, default=False)
    system_level_verification_required = Column(Boolean, nullable=False, default=False)
    # Residual ALARP feasibility attestations (ISO 14971 residual acceptability workflow)
    residual_all_feasible_controls_implemented = Column(Boolean, nullable=False, default=False)
    residual_further_reduction_not_practicable = Column(Boolean, nullable=False, default=False)
    rule_engine_result_json = Column(JSON, nullable=True)
    ai_suggested_values_json = Column(JSON, nullable=True)
    risk_criteria_version_applied = Column(Integer, nullable=True)

    # Financial and AI fields
    financial_impact = Column(Numeric, nullable=True)
    ai_metadata = Column(JSON, nullable=True)
    
    # Risk Knowledge Base library references (optional)
    hazard_library_id = Column(String, nullable=True, index=True)  # FK to hazard_library.id
    harm_library_id = Column(String, nullable=True, index=True)   # FK to harm_library.id
    risk_control_library_id = Column(String, nullable=True, index=True)  # FK to risk_control_library.id
    verification_library_id = Column(String, nullable=True, index=True)   # FK to verification_library.id
    
    # Version control
    version = Column(Integer, default=1, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="fmea_rows")
    component = relationship("Component", back_populates="fmea_rows")
    versions = relationship("FMEAVersion", back_populates="fmea_row", cascade="all, delete-orphan")
    risk_items = relationship("RiskItem", back_populates="fmea_row", cascade="all, delete-orphan")
