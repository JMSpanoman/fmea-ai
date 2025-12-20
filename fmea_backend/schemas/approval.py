from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ApprovalBase(BaseModel):
    artifact_type: str  # document, change_control, ncr, capa, audit, complaint
    artifact_id: str  # UUID
    status: str  # pending, approved, rejected
    comment: Optional[str] = None

class ApprovalCreate(ApprovalBase):
    approver_id: str  # UUID

class ApprovalUpdate(BaseModel):
    status: Optional[str] = None
    comment: Optional[str] = None

class ApprovalOut(ApprovalBase):
    id: str  # UUID
    approver_id: str  # UUID
    timestamp: datetime

    class Config:
        from_attributes = True

