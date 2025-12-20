from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ComponentBase(BaseModel):
    name: str
    description: Optional[str] = None

class ComponentCreate(ComponentBase):
    pass

class ComponentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class ComponentOut(ComponentBase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

