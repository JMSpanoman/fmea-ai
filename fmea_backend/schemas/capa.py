from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
from datetime import datetime

from schemas.capa_workflow import CAPAWorkflowPayload


class CAPAEvidenceOut(BaseModel):
    id: str
    capa_id: str
    category: str
    title: str
    reference_uri: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class CAPAEvidenceCreate(BaseModel):
    category: str = Field(..., description="rca | containment | effectiveness | general")
    title: str
    reference_uri: Optional[str] = None
    notes: Optional[str] = None


class CAPABase(BaseModel):
    root_cause: str = ""
    capa_plan: str = ""
    effectiveness_check: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    workflow_state: str = "draft"
    payload: Optional[Dict[str, Any]] = None


class CAPACreate(CAPABase):
    project_id: str


class CAPAUpdate(BaseModel):
    root_cause: Optional[str] = None
    capa_plan: Optional[str] = None
    effectiveness_check: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    workflow_state: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class CAPAOut(CAPABase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CAPAFullOut(BaseModel):
    """CAPA with workflow payload, evidence records, and AI hook metadata."""
    id: str
    project_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    workflow_state: str
    root_cause: str
    capa_plan: str
    effectiveness_check: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    payload: CAPAWorkflowPayload
    evidences: List[CAPAEvidenceOut] = Field(default_factory=list)
    workflow_errors: Optional[List[str]] = None  # soft validation warnings

    class Config:
        from_attributes = True


# AI Generation Request/Response (legacy)
class CAPAGenerateRequest(BaseModel):
    risk_ids: List[str]
    failure_mode: Optional[str] = None
    effect: Optional[str] = None
    cause: Optional[str] = None


class CAPAGenerateResponse(BaseModel):
    root_cause: str
    capa_plan: str
    effectiveness_check: str
    linked_risk_ids: List[str]
    ai_metadata: Optional[Dict[str, Any]] = None
