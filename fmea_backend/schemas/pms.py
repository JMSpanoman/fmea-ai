from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PMSSignalBase(BaseModel):
    signal_type: str  # complaint, service_data, trending, audit, field_failure
    description: str
    linked_risk_ids: Optional[List[str]] = None  # Array of UUIDs
    ai_metadata: Optional[Dict[str, Any]] = None

class PMSSignalCreate(PMSSignalBase):
    project_id: str  # UUID

class PMSSignalUpdate(BaseModel):
    signal_type: Optional[str] = None
    description: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class PMSSignalOut(PMSSignalBase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

# AI Generation Request/Response
class PMSGenerateRequest(BaseModel):
    signal_type: str
    description: str
    linked_risk_ids: Optional[List[str]] = None

class PMSGenerateResponse(BaseModel):
    updated_risk_scores: Optional[Dict[str, dict]] = None  # risk_id -> {severity, probability, detection}
    recommended_actions: List[str]
    risk_trend_flag: Optional[str] = None  # "increasing", "decreasing", "stable"
    metadata: Optional[Dict[str, Any]] = None

