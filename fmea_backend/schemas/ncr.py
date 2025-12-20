from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class NCRBase(BaseModel):
    description: str
    root_cause: Optional[str] = None
    containment_action: Optional[str] = None
    corrective_action: Optional[str] = None
    status: str
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class NCRCreate(NCRBase):
    project_id: str  # UUID

class NCRUpdate(BaseModel):
    description: Optional[str] = None
    root_cause: Optional[str] = None
    containment_action: Optional[str] = None
    corrective_action: Optional[str] = None
    status: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class NCROut(NCRBase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

# AI NCR Assistant
class NCRAnalyzeRequest(BaseModel):
    ncr_id: str  # UUID

class NCRAnalyzeResponse(BaseModel):
    root_cause: str
    corrective_action: str
    verification_steps: List[str]
    ai_metadata: Optional[Dict[str, Any]] = None

