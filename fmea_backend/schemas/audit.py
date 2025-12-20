from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class AuditBase(BaseModel):
    type: str  # internal, supplier, external, regulatory
    scope: Optional[str] = None
    status: str
    ai_metadata: Optional[Dict[str, Any]] = None

class AuditCreate(AuditBase):
    project_id: str  # UUID
    scheduled_date: Optional[datetime] = None

class AuditUpdate(BaseModel):
    type: Optional[str] = None
    scope: Optional[str] = None
    findings: Optional[Dict[str, Any]] = None
    status: Optional[str] = None
    scheduled_date: Optional[datetime] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class AuditOut(AuditBase):
    id: str  # UUID
    project_id: str  # UUID
    findings: Optional[Dict[str, Any]] = None
    scheduled_date: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuditFindingRequest(BaseModel):
    finding: str
    severity: Optional[str] = None
    category: Optional[str] = None

# AI Audit Assistant
class AuditPrepareRequest(BaseModel):
    project_id: str  # UUID
    audit_type: str

class AuditPrepareResponse(BaseModel):
    checklist: List[str]
    gaps: List[str]
    risk_areas: List[str]
    compliance_warnings: List[str]
    ai_metadata: Optional[Dict[str, Any]] = None

