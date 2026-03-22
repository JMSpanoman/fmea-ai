"""
Single structured CAPA document record (stored as JSON in Document.content for type=capa).
Separate from API CAPAWorkflowPayload; this is the controlled-document representation.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class CapaDocStatus(str, Enum):
    DRAFT = "draft"
    IN_PROGRESS = "in_progress"
    UNDER_INVESTIGATION = "under_investigation"
    ACTION_PLANNING = "action_planning"
    PENDING_EFFECTIVENESS = "pending_effectiveness"
    CLOSED = "closed"


class TriggerBlock(BaseModel):
    model_config = ConfigDict(extra="allow")
    type: Optional[str] = None
    reference: Optional[str] = None
    date_detected: Optional[str] = None  # ISO date string


class ProblemDefinitionBlock(BaseModel):
    model_config = ConfigDict(extra="allow")
    statement: Optional[str] = None
    scope: Optional[str] = None
    impact: Optional[str] = None


class ContainmentBlock(BaseModel):
    model_config = ConfigDict(extra="allow")
    actions: List[str] = Field(default_factory=list)
    implemented: bool = False
    verified: bool = False


class RootCauseBlock(BaseModel):
    model_config = ConfigDict(extra="allow")
    method: Optional[str] = None
    description: Optional[str] = None
    evidence: List[str] = Field(default_factory=list)
    status: str = "hypothesis"  # hypothesis | confirmed


class ActionItemDoc(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = ""
    description: Optional[str] = None
    owner: Optional[str] = None
    due_date: Optional[str] = None
    status: str = "planned"
    action_type: Optional[str] = None
    linked_root_cause_id: Optional[str] = None


class EffectivenessPlanBlock(BaseModel):
    model_config = ConfigDict(extra="allow")
    criteria: Optional[str] = None
    method: Optional[str] = None
    due_date: Optional[str] = None


class EffectivenessResultBlock(BaseModel):
    model_config = ConfigDict(extra="allow")
    evidence_summary: Optional[str] = None
    result: Optional[str] = None
    conclusion: Optional[str] = None
    referenced_evidence_ids: List[str] = Field(default_factory=list)
    reviewer: Optional[str] = None
    date_reviewed: Optional[str] = None


class RiskLinkageBlock(BaseModel):
    model_config = ConfigDict(extra="allow")
    hazards: List[str] = Field(default_factory=list)
    fmea_rows: List[str] = Field(default_factory=list)
    risk_controls: List[str] = Field(default_factory=list)


class ApprovalItemDoc(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str = ""
    kind: Optional[str] = None
    status: str = "pending"
    approver_name: Optional[str] = None


class DatesBlock(BaseModel):
    model_config = ConfigDict(extra="allow")
    opened: Optional[str] = None
    target: Optional[str] = None
    closed: Optional[str] = None


class GatesBlock(BaseModel):
    """Computed workflow gates (not user-edited truth)."""
    model_config = ConfigDict(extra="allow")
    can_start_rca: bool = False
    can_approve_root_cause: bool = False
    can_close: bool = False


class AIAssistBlock(BaseModel):
    """AI reviewer output only — never duplicates system structure."""
    model_config = ConfigDict(extra="allow")
    problem_review: Optional[str] = None
    root_cause_challenges: List[str] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)


class CapaDocumentRecord(BaseModel):
    """
    One structured CAPA document body. Serialized to JSON in Document.content.
    """
    model_config = ConfigDict(extra="allow")

    schema_version: str = Field(default="1.0", description="CAPA document JSON schema version")
    project_id: str
    capa_id: str = "CAPA-001"
    status: CapaDocStatus = CapaDocStatus.DRAFT
    legacy_format: bool = False
    # When migrating from plain-text CAPA bodies, preserved for audit (optional).
    legacy_text: Optional[str] = None

    trigger: TriggerBlock = Field(default_factory=TriggerBlock)
    problem_definition: ProblemDefinitionBlock = Field(default_factory=ProblemDefinitionBlock)
    containment: ContainmentBlock = Field(default_factory=ContainmentBlock)
    root_cause: RootCauseBlock = Field(default_factory=RootCauseBlock)
    corrective_actions: List[ActionItemDoc] = Field(default_factory=list)
    preventive_actions: List[ActionItemDoc] = Field(default_factory=list)
    effectiveness_plan: EffectivenessPlanBlock = Field(default_factory=EffectivenessPlanBlock)
    effectiveness_result: Optional[EffectivenessResultBlock] = None
    risk_linkage: RiskLinkageBlock = Field(default_factory=RiskLinkageBlock)
    approvals: List[ApprovalItemDoc] = Field(default_factory=list)
    dates: DatesBlock = Field(default_factory=DatesBlock)

    ai_assist: Optional[AIAssistBlock] = None
    gates: GatesBlock = Field(default_factory=GatesBlock)
