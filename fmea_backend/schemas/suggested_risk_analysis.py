"""Pydantic schemas for suggested risk analysis (API responses)."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class SuggestedFailureModeOut(BaseModel):
    id: str
    suggestion_set_id: str
    text: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SuggestedHazardOut(BaseModel):
    id: str
    suggestion_set_id: str
    text: str
    hazard_library_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SuggestedHazardousSituationOut(BaseModel):
    id: str
    suggestion_set_id: str
    text: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SuggestedHarmOut(BaseModel):
    id: str
    suggestion_set_id: str
    text: str
    harm_library_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SuggestedControlOut(BaseModel):
    id: str
    suggestion_set_id: str
    text: str
    risk_control_library_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SuggestedVerificationMethodOut(BaseModel):
    id: str
    suggestion_set_id: str
    text: str
    verification_library_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SuggestionSetOut(BaseModel):
    id: str
    source_type: str
    source_id: str
    architecture_id: Optional[str] = None
    project_id: Optional[str] = None
    rule_id: str
    created_at: Optional[datetime] = None
    failure_modes: List[SuggestedFailureModeOut] = []
    hazards: List[SuggestedHazardOut] = []
    hazardous_situations: List[SuggestedHazardousSituationOut] = []
    harms: List[SuggestedHarmOut] = []
    controls: List[SuggestedControlOut] = []
    verification_methods: List[SuggestedVerificationMethodOut] = []

    class Config:
        from_attributes = True


class GenerateSuggestionsResponse(BaseModel):
    created: int
