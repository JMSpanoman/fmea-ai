from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ProjectRiskCriteriaBase(BaseModel):
    evaluation_method: str = Field(default="matrix", description="matrix | score | hybrid")
    severity_scale: Optional[List[Dict[str, Any]]] = None
    probability_scale: Optional[List[Dict[str, Any]]] = None
    detection_scale: Optional[List[Dict[str, Any]]] = None
    risk_matrix: Optional[Dict[str, Dict[str, str]]] = None
    score_thresholds: Optional[Dict[str, Any]] = None
    special_rules: Optional[Dict[str, Any]] = None


class ProjectRiskCriteriaCreate(ProjectRiskCriteriaBase):
    """Create a new criteria version (draft)."""


class ProjectRiskCriteriaUpdate(BaseModel):
    evaluation_method: Optional[str] = None
    severity_scale: Optional[List[Dict[str, Any]]] = None
    probability_scale: Optional[List[Dict[str, Any]]] = None
    detection_scale: Optional[List[Dict[str, Any]]] = None
    risk_matrix: Optional[Dict[str, Dict[str, str]]] = None
    score_thresholds: Optional[Dict[str, Any]] = None
    special_rules: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


class ProjectRiskCriteriaOut(ProjectRiskCriteriaBase):
    id: str
    project_id: str
    version: int
    status: str
    approval_metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ProjectRiskCriteriaApprove(BaseModel):
    approval_metadata: Optional[Dict[str, Any]] = None


class RuleEvaluationAuditOut(BaseModel):
    id: str
    fmea_row_id: str
    project_id: str
    criteria_version: int
    evaluation_type: str
    inputs_json: Optional[Dict[str, Any]] = None
    matched_rules_json: Optional[List[Any]] = None
    output_json: Optional[Dict[str, Any]] = None
    decision_path_text: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class EvaluationResponse(BaseModel):
    ok: bool
    evaluation_type: str
    result: Dict[str, Any]
    row: Any  # FMEARowOut — avoid circular import; filled at runtime


class GlobalResidualAcceptabilityOut(BaseModel):
    """Aggregate overall residual risk acceptability (criteria policy + line items + project attestations)."""

    ok: bool = True
    overall_acceptable: bool
    blockers: List[str] = Field(default_factory=list)
    decision_path: List[str] = Field(default_factory=list)
    matched_rules: List[str] = Field(default_factory=list)
    policy_applied: bool = True


class GlobalResidualRiskSummaryOut(BaseModel):
    project_id: str
    criteria_version: int
    total_rows: int
    residual_summary: Dict[str, int]
    benefit_risk_required_count: int
    approval_blocked_count: int
    critical_function_count: int
    top_unresolved_risks: List[Dict[str, Any]]
    global_residual_acceptability: GlobalResidualAcceptabilityOut


class SeedRiskCriteriaRequest(BaseModel):
    template: str = Field(default="iso14971_default_pacemaker")
