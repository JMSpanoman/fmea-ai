from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class SupplierBase(BaseModel):
    name: str
    category: Optional[str] = None
    risk_rating: Optional[int] = None
    status: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class SupplierCreate(SupplierBase):
    project_id: str  # UUID

class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    risk_rating: Optional[int] = None
    status: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class SupplierOut(SupplierBase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

class SupplierEvaluationBase(BaseModel):
    evaluation_text: Optional[str] = None
    score: Optional[int] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class SupplierEvaluationCreate(SupplierEvaluationBase):
    supplier_id: str  # UUID

class SupplierEvaluationOut(SupplierEvaluationBase):
    id: str  # UUID
    supplier_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

# AI Supplier Risk
class SupplierRiskRequest(BaseModel):
    supplier_id: str  # UUID

class SupplierRiskResponse(BaseModel):
    risk_rating: int
    concerns: List[str]
    recommended_actions: List[str]
    ai_metadata: Optional[Dict[str, Any]] = None

