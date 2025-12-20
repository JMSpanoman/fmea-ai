from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CAPABase(BaseModel):
    root_cause: str
    capa_plan: str
    effectiveness_check: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None  # Array of UUIDs
    ai_metadata: Optional[Dict[str, Any]] = None

class CAPACreate(CAPABase):
    project_id: str  # UUID

class CAPAUpdate(BaseModel):
    root_cause: Optional[str] = None
    capa_plan: Optional[str] = None
    effectiveness_check: Optional[str] = None
    linked_risk_ids: Optional[List[str]] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class CAPAOut(CAPABase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

# AI Generation Request/Response
class CAPAGenerateRequest(BaseModel):
    risk_ids: List[str]  # Array of FMEA row UUIDs
    failure_mode: Optional[str] = None
    effect: Optional[str] = None
    cause: Optional[str] = None

class CAPAGenerateResponse(BaseModel):
    root_cause: str
    capa_plan: str
    effectiveness_check: str
    linked_risk_ids: List[str]
    ai_metadata: Optional[Dict[str, Any]] = None
