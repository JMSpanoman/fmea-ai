from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class VVTestBase(BaseModel):
    test_method: str
    acceptance_criteria: str
    rationale: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class VVTestCreate(VVTestBase):
    project_id: str  # UUID
    design_output_id: str  # UUID

class VVTestUpdate(BaseModel):
    test_method: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    rationale: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class VVTestOut(VVTestBase):
    id: str  # UUID
    project_id: str  # UUID
    design_output_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

# AI Generation Request/Response
class VVGenerateRequest(BaseModel):
    design_output_id: str  # UUID

class VVGenerateResponse(BaseModel):
    test_method: str
    acceptance_criteria: str
    rationale: str
    ai_metadata: Optional[Dict[str, Any]] = None


# Risk-based V&V generation (from FMEA/risk row)
class VVFromRiskGenerateRequest(BaseModel):
    component: str
    failure_mode: str
    effect: str
    cause: str
    severity: int
    occurrence: Optional[int] = None
    probability: Optional[int] = None
    detection: Optional[int] = None
    mitigation: Optional[str] = None
    risk_control: Optional[str] = None
    residual_severity: Optional[int] = None
    residual_occurrence: Optional[int] = None
    residual_probability: Optional[int] = None
    residual_detection: Optional[int] = None
    residual_rpn: Optional[int] = None

    def to_payload(self) -> dict:
        occ = self.occurrence if self.occurrence is not None else self.probability
        res_occ = self.residual_occurrence if self.residual_occurrence is not None else self.residual_probability
        return {
            "component": self.component,
            "failure_mode": self.failure_mode,
            "effect": self.effect,
            "cause": self.cause,
            "severity": self.severity,
            "occurrence": occ if occ is not None else 1,
            "detection": self.detection if self.detection is not None else 1,
            "mitigation": (self.mitigation or self.risk_control or "").strip(),
            "residual_severity": self.residual_severity,
            "residual_occurrence": res_occ,
            "residual_detection": self.residual_detection,
            "residual_rpn": self.residual_rpn,
        }


class CalculationItem(BaseModel):
    name: str
    formula: str
    description: Optional[str] = None
    inputs: Optional[List[str]] = None
    unit_or_threshold: Optional[str] = None


class TraceabilityBlock(BaseModel):
    source_component: str
    source_failure_mode: str
    source_mitigation: str
    source_effect: Optional[str] = None
    source_cause: Optional[str] = None
    source_severity: Optional[int] = None
    source_occurrence: Optional[int] = None
    source_detection: Optional[int] = None
    source_rpn: Optional[int] = None
    source_residual_severity: Optional[int] = None
    source_residual_occurrence: Optional[int] = None
    source_residual_detection: Optional[int] = None
    source_residual_rpn: Optional[int] = None


class VVFromRiskGenerateResponse(BaseModel):
    verification_test_name: str
    verification_objective: str
    verification_method: str
    validation_test_name: Optional[str] = None
    validation_objective: Optional[str] = None
    validation_method_or_scenario: Optional[str] = None
    validation_scenario: Optional[str] = None  # legacy; prefer validation_method_or_scenario
    acceptance_criteria: List[str]
    calculations: List[CalculationItem]
    worst_case_conditions: List[str]
    sample_size_rationale: Optional[str] = None
    traceability: TraceabilityBlock


class VVFromRiskSaveRequest(BaseModel):
    """Save generated V&V to project (for traceability and later protocol generation)."""
    project_id: str
    fmea_row_id: Optional[str] = None
    risk_item_id: Optional[str] = None
    verification_test_name: str
    verification_objective: str = ""
    verification_method: str = ""
    validation_test_name: Optional[str] = None
    validation_objective: Optional[str] = None
    validation_method_or_scenario: Optional[str] = None
    validation_scenario: str = ""
    acceptance_criteria: List[str] = []
    calculations: List[CalculationItem] = []
    worst_case_conditions: List[str] = []
    sample_size_rationale: Optional[str] = None
    traceability: TraceabilityBlock


class VVFromRiskSaveResponse(BaseModel):
    id: str
    project_id: str
    created_at: Optional[datetime] = None

