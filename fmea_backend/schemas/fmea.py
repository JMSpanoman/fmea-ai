from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

class FMEARowBase(BaseModel):
    device_function: Optional[str] = None
    failure_mode: Optional[str] = None
    effect: Optional[str] = None
    cause: Optional[str] = None
    hazard: Optional[str] = None
    harm: Optional[str] = None
    severity: Optional[int] = None
    probability: Optional[int] = None
    detection: Optional[int] = None
    mitigation: Optional[str] = None
    action_taken: Optional[str] = None
    residual_severity: Optional[int] = None
    residual_probability: Optional[int] = None
    residual_detection: Optional[int] = None
    financial_impact: Optional[Decimal] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    evidence_source: Optional[str] = None
    postmarket_review_status: Optional[str] = None
    postmarket_evidence_summary: Optional[str] = None
    # Risk Knowledge Base library references
    hazard_library_id: Optional[str] = None
    harm_library_id: Optional[str] = None
    risk_control_library_id: Optional[str] = None
    verification_library_id: Optional[str] = None
    initial_risk_classification: Optional[str] = None
    residual_risk_classification: Optional[str] = None
    benefit_risk_required: Optional[bool] = None
    reviewer_justification: Optional[str] = None
    reviewer_name: Optional[str] = None
    reviewer_date: Optional[datetime] = None
    critical_function_flag: Optional[bool] = None
    approval_blocked: Optional[bool] = None
    acceptable_for_release: Optional[bool] = None
    benefit_risk_formal_approval_recorded: Optional[bool] = None
    bra_clinical_benefit_documented: Optional[bool] = None
    bra_benefit_vs_residual_risk_documented: Optional[bool] = None
    bra_state_of_the_art_documented: Optional[bool] = None
    bra_supporting_evidence_addressed: Optional[bool] = None
    bra_approval_clinical_medical_recorded: Optional[bool] = None
    bra_approval_quality_regulatory_recorded: Optional[bool] = None
    bra_approval_design_authority_recorded: Optional[bool] = None
    cross_functional_review_completed: Optional[bool] = None
    formal_release_approval_recorded: Optional[bool] = None
    additional_controls_reduced_risk: Optional[bool] = None
    benefit_risk_analysis_approved: Optional[bool] = None
    critical_hazard_severity_floor_waived: Optional[bool] = None
    risk_eliminated: Optional[bool] = None
    system_level_verification_recorded: Optional[bool] = None
    critical_hazard_category_flag: Optional[bool] = None
    system_level_verification_required: Optional[bool] = None
    residual_all_feasible_controls_implemented: Optional[bool] = None
    residual_further_reduction_not_practicable: Optional[bool] = None
    rule_engine_result_json: Optional[Dict[str, Any]] = None
    ai_suggested_values_json: Optional[Dict[str, Any]] = None
    risk_criteria_version_applied: Optional[int] = None

class FMEARowCreate(FMEARowBase):
    project_id: Optional[str] = None  # UUID - will be set from path parameter
    component_id: Optional[str] = None  # UUID

class FMEARowUpdate(BaseModel):
    device_function: Optional[str] = None
    failure_mode: Optional[str] = None
    effect: Optional[str] = None
    cause: Optional[str] = None
    hazard: Optional[str] = None
    harm: Optional[str] = None
    severity: Optional[int] = None
    probability: Optional[int] = None
    detection: Optional[int] = None
    mitigation: Optional[str] = None
    action_taken: Optional[str] = None
    residual_severity: Optional[int] = None
    residual_probability: Optional[int] = None
    residual_detection: Optional[int] = None
    financial_impact: Optional[Decimal] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    evidence_source: Optional[str] = None
    postmarket_review_status: Optional[str] = None
    postmarket_evidence_summary: Optional[str] = None
    component_id: Optional[str] = None
    hazard_library_id: Optional[str] = None
    harm_library_id: Optional[str] = None
    risk_control_library_id: Optional[str] = None
    verification_library_id: Optional[str] = None
    initial_risk_classification: Optional[str] = None
    residual_risk_classification: Optional[str] = None
    benefit_risk_required: Optional[bool] = None
    reviewer_justification: Optional[str] = None
    reviewer_name: Optional[str] = None
    reviewer_date: Optional[datetime] = None
    critical_function_flag: Optional[bool] = None
    approval_blocked: Optional[bool] = None
    acceptable_for_release: Optional[bool] = None
    benefit_risk_formal_approval_recorded: Optional[bool] = None
    bra_clinical_benefit_documented: Optional[bool] = None
    bra_benefit_vs_residual_risk_documented: Optional[bool] = None
    bra_state_of_the_art_documented: Optional[bool] = None
    bra_supporting_evidence_addressed: Optional[bool] = None
    bra_approval_clinical_medical_recorded: Optional[bool] = None
    bra_approval_quality_regulatory_recorded: Optional[bool] = None
    bra_approval_design_authority_recorded: Optional[bool] = None
    cross_functional_review_completed: Optional[bool] = None
    formal_release_approval_recorded: Optional[bool] = None
    additional_controls_reduced_risk: Optional[bool] = None
    benefit_risk_analysis_approved: Optional[bool] = None
    critical_hazard_severity_floor_waived: Optional[bool] = None
    risk_eliminated: Optional[bool] = None
    system_level_verification_recorded: Optional[bool] = None
    critical_hazard_category_flag: Optional[bool] = None
    system_level_verification_required: Optional[bool] = None
    residual_all_feasible_controls_implemented: Optional[bool] = None
    residual_further_reduction_not_practicable: Optional[bool] = None
    rule_engine_result_json: Optional[Dict[str, Any]] = None
    ai_suggested_values_json: Optional[Dict[str, Any]] = None
    risk_criteria_version_applied: Optional[int] = None

class FMEARowOut(FMEARowBase):
    id: str  # UUID
    project_id: str  # UUID
    component_id: Optional[str] = None  # UUID
    rpn: Optional[int] = None
    residual_rpn: Optional[int] = None
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Backward compatibility aliases
FMEACreate = FMEARowCreate
FMEAUpdate = FMEARowUpdate
FMEAOut = FMEARowOut

# AI Request/Response schemas
class AIFMEASuggestRequest(BaseModel):
    component: str
    failure_mode: str
    effect: str
    cause: str

class AIFMEASuggestResponse(BaseModel):
    severity: int
    probability: int
    detection: int
    rpn: int
    mitigation: str
    financial_impact: Decimal
    residual_severity: int
    residual_probability: int
    residual_detection: int
    residual_rpn: int

class AIConsistencyCheckRequest(BaseModel):
    fmea_row: FMEARowOut

class AIConsistencyCheckResponse(BaseModel):
    issues: list[str]
    recommendations: list[str]

# Backward compatibility - additional schemas used in main.py
class AISuggestionRequest(BaseModel):
    component: str
    failure_mode: Optional[str] = None
    effect: Optional[str] = None
    cause: Optional[str] = None
