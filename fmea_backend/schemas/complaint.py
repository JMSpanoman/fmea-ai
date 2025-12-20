from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ComplaintBase(BaseModel):
    description: str
    reportability: Optional[str] = None  # reportable, non_reportable
    investigation: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class ComplaintCreate(ComplaintBase):
    project_id: str  # UUID

class ComplaintUpdate(BaseModel):
    description: Optional[str] = None
    reportability: Optional[str] = None
    investigation: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class ComplaintOut(ComplaintBase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

# AI Complaint Assistant
class ComplaintInvestigateRequest(BaseModel):
    complaint_id: str  # UUID

class ComplaintInvestigateResponse(BaseModel):
    investigation: str
    affected_risks: List[str]  # Array of risk IDs
    reportability_decision: str  # reportable, non_reportable
    ai_metadata: Optional[Dict[str, Any]] = None

