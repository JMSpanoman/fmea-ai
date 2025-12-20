from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AuditLogEventBase(BaseModel):
    event_type: str
    details_json: Optional[Dict[str, Any]] = None

class AuditLogEventCreate(AuditLogEventBase):
    project_id: str
    user_id: str

class AuditLogEventOut(AuditLogEventBase):
    id: str
    project_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

