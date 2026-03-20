"""
Pydantic models for the deterministic risk rule engine (typed I/O for APIs, audits, and tests).

Business logic lives in ``services.risk_rule_engine``; these models provide validation and stable contracts.
"""

from __future__ import annotations

from typing import Any, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

EvaluationType = Literal["initial", "residual"]


class MatrixIndices(BaseModel):
    """1-based indices into ``risk_matrix`` rows/columns after FMEA→band mapping."""

    severity: int = Field(..., ge=1, description="Severity band index (row)")
    probability: int = Field(..., ge=1, description="Probability band index (column)")


class FmeaRiskEvaluationInput(BaseModel):
    """
    Row snapshot used for evaluation (initial uses severity/probability/detection;
    residual uses residual_* fields for the residual pass).
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    device_function: Optional[str] = None
    failure_mode: Optional[str] = None
    effect: Optional[str] = None
    harm: Optional[str] = None
    hazard: Optional[str] = None
    cause: Optional[str] = None
    severity: Optional[int] = None
    probability: Optional[int] = None
    detection: Optional[int] = None
    mitigation: Optional[str] = None
    action_taken: Optional[str] = None
    residual_severity: Optional[int] = None
    residual_probability: Optional[int] = None
    residual_detection: Optional[int] = None
    reviewer_justification: Optional[str] = None
    # Release / workflow attestations (stored on FMEA row; engine reads for gating only)
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
    residual_all_feasible_controls_implemented: Optional[bool] = None
    residual_further_reduction_not_practicable: Optional[bool] = None

    def to_engine_dict(self) -> dict[str, Any]:
        """Preserve explicit Nones where set (engine distinguishes missing vs null)."""
        return self.model_dump(mode="python", exclude_none=False)


class RiskCriteriaConfig(BaseModel):
    """
    Versioned criteria payload (matrix, scales, thresholds, special_rules).

    ``extra='allow'`` keeps forward-compatible JSON keys without schema churn.
    """

    model_config = ConfigDict(extra="allow")

    evaluation_method: str = "matrix"
    severity_scale: Any = None
    probability_scale: Any = None
    detection_scale: Any = None
    risk_matrix: Any = None
    score_thresholds: Any = None
    special_rules: Any = None

    def to_engine_dict(self) -> dict[str, Any]:
        return self.model_dump(mode="python")


class RiskEvaluationResult(BaseModel):
    """
    Normalized engine output (success or validation failure).

    Use :meth:`from_engine_dict` to wrap the dict returned by ``evaluate_row`` / ``evaluate_initial_risk``.
    """

    model_config = ConfigDict(extra="ignore")

    ok: bool
    evaluation_type: str
    classification: Optional[str] = None
    risk_score: Optional[int] = None
    benefit_risk_required: bool = False
    reviewer_justification_required: bool = False
    approval_blocked: bool = False
    critical_function_flag: bool = False
    critical_hazard_category_match: bool = False
    system_level_verification_required: bool = False
    input_fmea_severity: Optional[int] = None
    evaluated_fmea_severity: Optional[int] = None
    benefit_risk_formal_approval_required: bool = False
    benefit_risk_structured_workflow_active: bool = False
    benefit_risk_documentation_gates_active: bool = False
    benefit_risk_multi_party_approval_required: bool = False
    cross_functional_review_required: bool = False
    formal_release_approval_required: bool = False
    residual_acceptable_rationale_required: bool = False
    residual_alarp_feasibility_attestations_required: bool = False
    acceptable_for_release: bool = False
    release_status: str = "not_acceptable_for_release"
    release_blockers: List[str] = Field(default_factory=list)
    matched_rules: List[str] = Field(default_factory=list)
    decision_path: List[str] = Field(default_factory=list)
    validation_errors: Optional[List[str]] = None
    matrix_indices: Optional[MatrixIndices] = None

    @classmethod
    def from_engine_dict(cls, data: dict[str, Any]) -> RiskEvaluationResult:
        """Coerce raw engine dict (including nested ``matrix_indices``) into a model."""
        payload = dict(data)
        mi = payload.get("matrix_indices")
        if isinstance(mi, dict):
            try:
                payload["matrix_indices"] = MatrixIndices.model_validate(mi)
            except Exception:
                payload["matrix_indices"] = None
        return cls.model_validate(payload)
