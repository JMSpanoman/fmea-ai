from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ProjectProfileBase(BaseModel):
    intended_use: Optional[str] = None
    device_description: Optional[str] = None
    user_population: Optional[str] = None
    use_environment: Optional[str] = None
    key_safety_characteristics: Optional[List[str]] = None


class ProjectProfileUpsert(ProjectProfileBase):
    """
    Used for PUT upsert. All fields optional so clients can send partial updates,
    but the server will store a single 1:1 record per project.
    """

    pass


class ProjectProfileOut(ProjectProfileBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

