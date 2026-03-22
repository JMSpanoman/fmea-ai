"""
Enterprise CAPA workflow payload structures (sections A–L).
Validated on save; workflow state is stored separately on the CAPA row.
"""
from __future__ import annotations

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# --- Enumerations (persisted as strings) ---


class TriggerType(str, Enum):
    COMPLAINT = "complaint"
    NONCONFORMANCE = "nonconformance"
    AUDIT_FINDING = "audit_finding"
    TRENDING_SIGNAL = "trending_signal"
    SUPPLIER_ISSUE = "supplier_issue"
    OTHER = "other"


class ScopeLevel(str, Enum):
    LOCAL = "local"
    SYSTEMIC = "systemic"


class RCAMethod(str, Enum):
    FIVE_WHYS = "5_whys"
    FISHBONE = "fishbone"
    FAULT_TREE = "fault_tree"
    DATA_ANALYSIS = "data_analysis"
    OTHER = "other"


class RootCauseStatus(str, Enum):
    HYPOTHESIS = "hypothesis"
    CONFIRMED = "confirmed"


class CorrectiveActionType(str, Enum):
    DESIGN = "design"
    PROCESS = "process"
    SUPPLIER = "supplier"
    TRAINING = "training"
    DOCUMENTATION = "documentation"
    SOFTWARE = "software"
    MANUFACTURING = "manufacturing"
    LABELING = "labeling"
    OTHER = "other"


class ActionStatus(str, Enum):
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    CANCELLED = "cancelled"


class EffectivenessConclusion(str, Enum):
    EFFECTIVE = "effective"
    INEFFECTIVE = "ineffective"
    NEEDS_MORE_MONITORING = "needs_more_monitoring"


class ApprovalKind(str, Enum):
    RCA = "rca"
    ACTION_PLAN = "action_plan"
    CLOSURE = "closure"


class ApproverRole(str, Enum):
    QA = "qa"
    RA = "ra"
    ENGINEERING = "engineering"
    OPERATIONS = "operations"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class CAPAWorkflowState(str, Enum):
    """Gated lifecycle state."""
    DRAFT = "draft"
    INTAKE = "intake"  # A+B+C captured (not yet verified complete)
    INTAKE_COMPLETE = "intake_complete"
    RCA_IN_PROGRESS = "rca_in_progress"
    RCA_PENDING_APPROVAL = "rca_pending_approval"
    ACTIONS_DEFINED = "actions_defined"
    IMPLEMENTATION = "implementation"
    EFFECTIVENESS_PLANNED = "effectiveness_planned"
    EFFECTIVENESS_PENDING = "effectiveness_pending"
    PENDING_CLOSURE = "pending_closure"
    CLOSED = "closed"
    CANCELLED = "cancelled"


# --- Section A: Trigger & classification ---


class TriggerClassification(BaseModel):
    trigger_type: Optional[TriggerType] = None
    source_reference: str = ""
    detection_method: str = ""
    date_detected: Optional[date] = None
    initial_classification: str = ""
    initial_severity_or_risk_indicator: str = ""


# --- Section B: Problem definition ---


class ProblemDefinition(BaseModel):
    problem_statement: str = ""
    affected_products_lots_subsystems_processes: str = ""
    scope: Optional[ScopeLevel] = None
    initial_impact_assessment: str = ""
    patient_impact: str = ""
    user_impact: str = ""
    business_impact: str = ""
    compliance_impact: str = ""


# --- Section C: Immediate containment ---


class ImmediateContainment(BaseModel):
    containment_actions: str = ""
    date_implemented: Optional[date] = None
    owner: str = ""
    containment_verified: bool = False
    field_impact: Optional[bool] = None
    released_product_affected: Optional[bool] = None


# --- Section D: Root cause analysis ---


class RootCauseAnalysis(BaseModel):
    rca_method: Optional[RCAMethod] = None
    root_cause_summary: str = ""
    contributing_factors: str = ""
    detection_failure_analysis: str = ""
    objective_evidence: str = ""
    evidence_attachment_references: List[str] = Field(default_factory=list)
    root_cause_status: RootCauseStatus = RootCauseStatus.HYPOTHESIS


# --- Sections E & F: Actions ---


class CorrectiveActionItem(BaseModel):
    id: str = Field(default="", description="Client-generated UUID for stable keys")
    description: str = ""
    owner: str = ""
    due_date: Optional[date] = None
    status: ActionStatus = ActionStatus.PLANNED
    action_type: Optional[CorrectiveActionType] = None
    linked_root_cause_id: str = Field(
        default="",
        description="Must reference a root-cause line id or RCA narrative key when enforced",
    )


class PreventiveActionsBlock(BaseModel):
    items: List[CorrectiveActionItem] = Field(default_factory=list)
    scope_expansion_analysis: str = ""
    where_else_evaluation: str = ""


# --- G & H: Effectiveness ---


class VerificationOfEffectivenessPlan(BaseModel):
    success_criteria: str = ""
    metrics_thresholds: str = ""
    data_source: str = ""
    method: str = ""
    review_date: Optional[date] = None
    owner: str = ""


class EffectivenessResults(BaseModel):
    """Populated only when objective evidence exists (server-enforced)."""
    evidence_summary: str = ""
    result: str = ""
    date_reviewed: Optional[date] = None
    reviewer: str = ""
    conclusion: Optional[EffectivenessConclusion] = None
    referenced_evidence_ids: List[str] = Field(default_factory=list)


# --- I: Risk / FMEA linkage ---


class RiskFmeaLinkage(BaseModel):
    related_hazard_ids: List[str] = Field(default_factory=list)
    related_hazardous_situation_ids: List[str] = Field(default_factory=list)
    related_fmea_row_ids: List[str] = Field(default_factory=list)
    related_risk_control_ids: List[str] = Field(default_factory=list)
    pre_action_risk_notes: str = ""
    post_action_risk_notes: str = ""
    risk_file_update_required: Optional[bool] = None
    benefit_risk_profile_changed: Optional[bool] = None


# --- J: Regulatory ---


class RegulatoryQualityImpact(BaseModel):
    mdr_reportability_review: str = ""
    advisory_recall_field_action_assessment: str = ""
    design_change_required: Optional[bool] = None
    procedure_training_update_required: Optional[bool] = None
    validation_required: Optional[bool] = None


# --- K: Approvals ---


class ApprovalRecord(BaseModel):
    id: str = ""
    kind: ApprovalKind = ApprovalKind.RCA
    role: ApproverRole = ApproverRole.QA
    approver_name: str = ""  # TBD until e-signature integration
    status: ApprovalStatus = ApprovalStatus.PENDING
    decided_at: Optional[datetime] = None
    comment: str = ""


# --- L: Closure ---


class ClosureChecklist(BaseModel):
    root_cause_verified: bool = False
    actions_implemented: bool = False
    effectiveness_supported_by_evidence: bool = False
    risk_documentation_updated: bool = False
    required_approvals_complete: bool = False
    documentation_complete: bool = False


class ClosureBlock(BaseModel):
    closure_date: Optional[date] = None
    closure_rationale: str = ""
    checklist: ClosureChecklist = Field(default_factory=ClosureChecklist)


class AIReviewHooksState(BaseModel):
    """
    Placeholders for AI-assisted review prompts (never auto-closes CAPA).
    Keys are hook ids; values are last model output or user notes.
    """
    problem_statement_review: Optional[str] = None
    root_cause_challenge: Optional[str] = None
    missing_evidence_detection: Optional[str] = None
    systemic_scope_challenge: Optional[str] = None
    capa_risk_consistency: Optional[str] = None


class CAPAWorkflowPayload(BaseModel):
    """Full structured CAPA content (sections A–L)."""
    trigger: TriggerClassification = Field(default_factory=TriggerClassification)
    problem: ProblemDefinition = Field(default_factory=ProblemDefinition)
    containment: ImmediateContainment = Field(default_factory=ImmediateContainment)
    rca: RootCauseAnalysis = Field(default_factory=RootCauseAnalysis)
    corrective_actions: List[CorrectiveActionItem] = Field(default_factory=list)
    preventive: PreventiveActionsBlock = Field(default_factory=PreventiveActionsBlock)
    voe_plan: VerificationOfEffectivenessPlan = Field(default_factory=VerificationOfEffectivenessPlan)
    effectiveness_results: Optional[EffectivenessResults] = None
    risk_linkage: RiskFmeaLinkage = Field(default_factory=RiskFmeaLinkage)
    regulatory: RegulatoryQualityImpact = Field(default_factory=RegulatoryQualityImpact)
    approvals: List[ApprovalRecord] = Field(default_factory=list)
    closure: ClosureBlock = Field(default_factory=ClosureBlock)
    ai_review_hooks: AIReviewHooksState = Field(default_factory=AIReviewHooksState)

    @field_validator("corrective_actions", mode="before")
    @classmethod
    def _default_list(cls, v: Any) -> Any:
        return v if v is not None else []

    model_config = ConfigDict(extra="allow")


def default_workflow_payload() -> Dict[str, Any]:
    """JSON-serializable default for new CAPAs."""
    return CAPAWorkflowPayload().model_dump(mode="json")
