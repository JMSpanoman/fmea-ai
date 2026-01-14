from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class ComponentBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[str] = None
    tags: Optional[Any] = None  # JSON-compatible (e.g., list[str] or dict)

class ComponentCreate(ComponentBase):
    pass

class ComponentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    tags: Optional[Any] = None

class ComponentBulkItem(ComponentBase):
    """
    Used by bulk create/replace.
    If id is provided, it will be used as the stable component identifier.
    """
    id: Optional[str] = None

class ComponentOut(ComponentBase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

