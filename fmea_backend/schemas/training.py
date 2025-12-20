from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TrainingRecordBase(BaseModel):
    status: str  # assigned, in_progress, complete

class TrainingRecordCreate(BaseModel):
    user_id: str  # UUID
    document_id: str  # UUID
    status: str = "assigned"

class TrainingRecordUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None

class TrainingRecordOut(TrainingRecordBase):
    id: str  # UUID
    user_id: str  # UUID
    document_id: str  # UUID
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TrainingAssignRequest(BaseModel):
    user_id: str  # UUID
    document_id: str  # UUID

class TrainingCompleteRequest(BaseModel):
    training_record_id: str  # UUID

