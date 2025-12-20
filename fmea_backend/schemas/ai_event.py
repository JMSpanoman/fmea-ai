from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AIEventCreate(BaseModel):
    project_id: str
    context_type: str
    context_id: Optional[str] = None
    prompt_name: str
    input_summary: Optional[str] = None
    output_json: Optional[Dict[str, Any]] = None

class AIEventUpdate(BaseModel):
    disposition: Optional[str] = None  # "accepted", "edited", "rejected"
    disposition_notes: Optional[str] = None

class AIEventOut(BaseModel):
    id: str
    project_id: str
    user_id: str
    context_type: str
    context_id: Optional[str] = None
    prompt_name: str
    input_summary: Optional[str] = None
    output_json: Optional[Dict[str, Any]] = None
    disposition: Optional[str] = None
    disposition_notes: Optional[str] = None
    disposition_user_id: Optional[str] = None
    created_at: datetime
    disposed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

