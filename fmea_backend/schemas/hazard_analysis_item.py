"""
Pydantic schemas for HazardAnalysisItem — ISO 14971-style hazard analysis row.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
from datetime import datetime


class HazardAnalysisItemBase(BaseModel):
    """Base fields for hazard analysis item."""
    component_id: Optional[str] = None
    device_id: Optional[str] = None
    risk_item_id: Optional[str] = None
    risk_item_version_id: Optional[str] = None
    fmea_row_id: Optional[str] = None
    risk_key: Optional[str] = None
    version_no: int = 1
    hazard_category: Optional[str] = None
    hazard: Optional[str] = None
    foreseeable_sequence_of_events: Optional[str] = None
    hazardous_situation: Optional[str] = None
    harm: Optional[str] = None
    affected_user: Optional[str] = None
    failure_mode: Optional[str] = None
    cause_of_failure: Optional[str] = None
    clinical_effect: Optional[str] = None
    operating_mode: Optional[str] = None
    use_environment: Optional[str] = None
    initial_severity: Optional[int] = None
    initial_probability: Optional[int] = None
    initial_risk_level: Optional[str] = None
    risk_control_measures: Optional[List[str]] = None
    risk_control_type: Optional[List[str]] = None
    control_implementation_notes: Optional[str] = None
    residual_severity: Optional[int] = None
    residual_probability: Optional[int] = None
    residual_risk_level: Optional[str] = None
    residual_risk_acceptability: Optional[str] = None
    related_design_input: Optional[List[str]] = None
    related_design_output: Optional[List[str]] = None
    verification_reference: Optional[List[str]] = None
    validation_reference: Optional[List[str]] = None
    requirement_ids: Optional[List[str]] = None
    approval_status: Optional[str] = "draft"
    reviewer_comments: Optional[str] = None
    ai_generated: Optional[bool] = None
    ai_confidence: Optional[str] = None
    source_context: Optional[str] = None
    assumptions: Optional[List[str]] = None


class HazardAnalysisItemCreate(HazardAnalysisItemBase):
    """Create payload; project_id required."""
    project_id: str


class HazardAnalysisItemUpdate(BaseModel):
    """Update payload; all fields optional."""
    component_id: Optional[str] = None
    device_id: Optional[str] = None
    risk_key: Optional[str] = None
    version_no: Optional[int] = None
    hazard_category: Optional[str] = None
    hazard: Optional[str] = None
    foreseeable_sequence_of_events: Optional[str] = None
    hazardous_situation: Optional[str] = None
    harm: Optional[str] = None
    affected_user: Optional[str] = None
    failure_mode: Optional[str] = None
    cause_of_failure: Optional[str] = None
    clinical_effect: Optional[str] = None
    operating_mode: Optional[str] = None
    use_environment: Optional[str] = None
    initial_severity: Optional[int] = None
    initial_probability: Optional[int] = None
    initial_risk_level: Optional[str] = None
    risk_control_measures: Optional[List[str]] = None
    risk_control_type: Optional[List[str]] = None
    control_implementation_notes: Optional[str] = None
    residual_severity: Optional[int] = None
    residual_probability: Optional[int] = None
    residual_risk_level: Optional[str] = None
    residual_risk_acceptability: Optional[str] = None
    related_design_input: Optional[List[str]] = None
    related_design_output: Optional[List[str]] = None
    verification_reference: Optional[List[str]] = None
    validation_reference: Optional[List[str]] = None
    requirement_ids: Optional[List[str]] = None
    approval_status: Optional[str] = None
    reviewer_comments: Optional[str] = None
    ai_generated: Optional[bool] = None
    ai_confidence: Optional[str] = None
    source_context: Optional[str] = None
    assumptions: Optional[List[str]] = None


class HazardAnalysisItemResponse(HazardAnalysisItemBase):
    """Full response with id and timestamps."""
    id: str
    project_id: str
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    component_name: Optional[str] = None  # populated for display

    class Config:
        from_attributes = True
