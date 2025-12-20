from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class QualityEventBase(BaseModel):
    event_type: str
    description: str
    status: str
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class QualityEventCreate(QualityEventBase):
    project_id: str  # UUID

class QualityEventUpdate(BaseModel):
    event_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class QualityEventOut(QualityEventBase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

class QualityEventLinkRisksRequest(BaseModel):
    risk_ids: List[str]  # Array of risk IDs

