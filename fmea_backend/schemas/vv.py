from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class VVTestBase(BaseModel):
    test_method: str
    acceptance_criteria: str
    rationale: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class VVTestCreate(VVTestBase):
    project_id: str  # UUID
    design_output_id: str  # UUID

class VVTestUpdate(BaseModel):
    test_method: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    rationale: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class VVTestOut(VVTestBase):
    id: str  # UUID
    project_id: str  # UUID
    design_output_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

# AI Generation Request/Response
class VVGenerateRequest(BaseModel):
    design_output_id: str  # UUID

class VVGenerateResponse(BaseModel):
    test_method: str
    acceptance_criteria: str
    rationale: str
    ai_metadata: Optional[Dict[str, Any]] = None

