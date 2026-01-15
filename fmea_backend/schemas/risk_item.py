from pydantic import BaseModel
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime
import re

try:
    # Pydantic v2
    from pydantic import field_validator  # type: ignore
except Exception:  # pragma: no cover
    # Pydantic v1 fallback
    field_validator = None  # type: ignore

if TYPE_CHECKING:
    from schemas.risk_item import RiskItemVersionOut

# Legacy schemas (backward compatible)
class RiskItemBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    risk_type: Optional[str] = None
    severity: Optional[int] = None
    probability: Optional[int] = None  # Legacy
    impact: Optional[int] = None  # Legacy
    mitigation_strategy: Optional[str] = None
    control_measures: Optional[str] = None
    residual_risk_score: Optional[int] = None  # Legacy
    owner: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    source: Optional[str] = None
    detected_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class RiskItemCreate(RiskItemBase):
    project_id: str  # UUID
    fmea_row_id: Optional[str] = None  # UUID
    component_id: Optional[str] = None  # UUID (for component-scoped reports)
    component_name: Optional[str] = None  # fallback string tag

class RiskItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    risk_type: Optional[str] = None
    severity: Optional[int] = None
    probability: Optional[int] = None  # Legacy
    impact: Optional[int] = None  # Legacy
    mitigation_strategy: Optional[str] = None
    control_measures: Optional[str] = None
    residual_risk_score: Optional[int] = None  # Legacy
    owner: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    source: Optional[str] = None
    detected_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    fmea_row_id: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    component_id: Optional[str] = None
    component_name: Optional[str] = None
    # ISO 14971 fields (optional in update)
    hazard: Optional[str] = None
    hazardous_situation: Optional[str] = None
    harm: Optional[str] = None
    failure_mode: Optional[str] = None
    probability_of_harm: Optional[int] = None
    occurrence: Optional[int] = None
    detection: Optional[int] = None
    inherent_safety: Optional[str] = None
    protective_measures: Optional[str] = None
    information_for_safety: Optional[str] = None
    residual_severity: Optional[int] = None
    residual_probability_of_harm: Optional[int] = None
    residual_occurrence: Optional[int] = None
    residual_detection: Optional[int] = None
    benefit_risk_summary: Optional[str] = None
    overall_residual_risk_conclusion: Optional[str] = None
    risk_acceptability: Optional[str] = None
    risk_rationale: Optional[str] = None
    change_summary: Optional[str] = None

class RiskItemOut(RiskItemBase):
    id: str  # UUID
    project_id: str  # UUID
    fmea_row_id: Optional[str] = None  # UUID
    component_id: Optional[str] = None
    component_name: Optional[str] = None
    current_version_id: Optional[str] = None
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    residual_risk_level: Optional[str] = None  # Legacy
    closed_date: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Forward reference handled via optional fields or separate endpoint

# ISO 14971 compliant version schema
class RiskItemVersionCreate(BaseModel):
    # ISO 14971: Hazard analysis chain
    hazard: Optional[str] = None
    hazardous_situation: Optional[str] = None
    harm: Optional[str] = None
    failure_mode: Optional[str] = None
    sequence_of_events: Optional[str] = None
    
    # Risk estimation (ISO 14971)
    severity: Optional[int] = None
    probability_of_harm: Optional[int] = None
    occurrence: Optional[int] = None  # Alias for probability_of_harm
    detection: Optional[int] = None
    probability: Optional[int] = None  # Legacy
    impact: Optional[int] = None  # Legacy
    
    # Risk control measures
    inherent_safety: Optional[str] = None
    protective_measures: Optional[str] = None
    information_for_safety: Optional[str] = None
    control_measures_summary: Optional[str] = None
    
    # Residual risk evaluation
    residual_severity: Optional[int] = None
    residual_probability_of_harm: Optional[int] = None
    residual_occurrence: Optional[int] = None
    residual_detection: Optional[int] = None
    
    # Benefit-risk analysis
    benefit_risk_summary: Optional[str] = None
    overall_residual_risk_conclusion: Optional[str] = None
    
    # Risk acceptability
    risk_acceptability: Optional[str] = None  # "acceptable", "unacceptable", "needs_benefit_risk"
    risk_rationale: Optional[str] = None
    
    # Metadata
    change_summary: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class RiskItemVersionOut(RiskItemVersionCreate):
    id: str  # UUID
    risk_item_id: str  # UUID
    version_number: int
    risk_score: Optional[int] = None
    risk_level: Optional[str] = None
    residual_risk_score: Optional[int] = None
    residual_risk_level: Optional[str] = None
    changed_by: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Risk Control schemas
class RiskControlBase(BaseModel):
    control_name: str
    control_description: Optional[str] = None
    control_type: str  # "inherent_safety", "protective", "information"
    implementation_details: Optional[str] = None
    verification_method: Optional[str] = None
    trace_to_design_input: Optional[str] = None
    trace_to_design_output: Optional[str] = None
    trace_to_verification_test: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[str] = None
    assigned_to: Optional[str] = None
    proposed_date: Optional[datetime] = None
    implemented_date: Optional[datetime] = None
    verified_date: Optional[datetime] = None
    effectiveness_notes: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

    # Enforce a structured text format (not free notes).
    # Accepted examples:
    # - "Test: <...>"
    # - "Inspection: <...>"
    # - "Analysis: <...>"
    # - "Demonstration: <...>"
    # - Multi-line with a first line starting with one of the above prefixes.
    if field_validator:
        @field_validator("verification_method")  # type: ignore[misc]
        @classmethod
        def _validate_verification_method(cls, v: Optional[str]):
            if v is None:
                return v
            s = str(v).strip()
            if not s:
                return None
            if len(s) > 1200:
                raise ValueError("verification_method is too long (max 1200 chars)")
            first_line = s.splitlines()[0].strip()
            ok = bool(re.match(r"^(Test|Inspection|Analysis|Demonstration)\\s*:\\s*.+", first_line, flags=re.IGNORECASE))
            if not ok:
                raise ValueError(
                    "verification_method must be structured text starting with one of: "
                    "'Test:', 'Inspection:', 'Analysis:', 'Demonstration:'"
                )
            return s

class RiskControlCreate(RiskControlBase):
    risk_item_id: str  # UUID
    project_id: str  # UUID

class RiskControlUpdate(BaseModel):
    control_name: Optional[str] = None
    control_description: Optional[str] = None
    control_type: Optional[str] = None
    implementation_details: Optional[str] = None
    verification_method: Optional[str] = None
    trace_to_design_input: Optional[str] = None
    trace_to_design_output: Optional[str] = None
    trace_to_verification_test: Optional[str] = None
    status: Optional[str] = None
    owner: Optional[str] = None
    assigned_to: Optional[str] = None
    proposed_date: Optional[datetime] = None
    implemented_date: Optional[datetime] = None
    verified_date: Optional[datetime] = None
    effectiveness_notes: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class RiskControlOut(RiskControlBase):
    id: str  # UUID
    risk_item_id: str  # UUID
    project_id: str  # UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Approval request schema
class RiskItemApprovalRequest(BaseModel):
    version_id: str
    decision: str  # "approved", "rejected"
    rationale: str
    comment: Optional[str] = None

