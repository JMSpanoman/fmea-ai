from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from decimal import Decimal

class FMEARowBase(BaseModel):
    failure_mode: Optional[str] = None
    effect: Optional[str] = None
    cause: Optional[str] = None
    severity: Optional[int] = None
    probability: Optional[int] = None
    detection: Optional[int] = None
    mitigation: Optional[str] = None
    residual_severity: Optional[int] = None
    residual_probability: Optional[int] = None
    residual_detection: Optional[int] = None
    financial_impact: Optional[Decimal] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class FMEARowCreate(FMEARowBase):
    project_id: Optional[str] = None  # UUID - will be set from path parameter
    component_id: Optional[str] = None  # UUID

class FMEARowUpdate(BaseModel):
    failure_mode: Optional[str] = None
    effect: Optional[str] = None
    cause: Optional[str] = None
    severity: Optional[int] = None
    probability: Optional[int] = None
    detection: Optional[int] = None
    mitigation: Optional[str] = None
    residual_severity: Optional[int] = None
    residual_probability: Optional[int] = None
    residual_detection: Optional[int] = None
    financial_impact: Optional[Decimal] = None
    ai_metadata: Optional[Dict[str, Any]] = None
    component_id: Optional[str] = None

class FMEARowOut(FMEARowBase):
    id: str  # UUID
    project_id: str  # UUID
    component_id: Optional[str] = None  # UUID
    rpn: Optional[int] = None
    residual_rpn: Optional[int] = None
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# AI Request/Response schemas
class AIFMEASuggestRequest(BaseModel):
    component: str
    failure_mode: str
    effect: str
    cause: str

class AIFMEASuggestResponse(BaseModel):
    severity: int
    probability: int
    detection: int
    rpn: int
    mitigation: str
    financial_impact: Decimal
    residual_severity: int
    residual_probability: int
    residual_detection: int
    residual_rpn: int

class AIConsistencyCheckRequest(BaseModel):
    fmea_row: FMEARowOut

class AIConsistencyCheckResponse(BaseModel):
    issues: list[str]
    recommendations: list[str]
