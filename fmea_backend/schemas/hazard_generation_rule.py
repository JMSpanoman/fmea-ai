"""Pydantic schemas for Hazard Generation Rules (SmartRisk Phase 2)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class HazardGenerationRuleBase(BaseModel):
    name: Optional[str] = None
    trigger_type: str = Field(..., description="component | interface")
    component_type: Optional[str] = None
    interface_type: Optional[str] = None
    node_type: Optional[str] = None
    hazard_library_id: str
    harm_library_id: Optional[str] = None
    risk_control_library_id: Optional[str] = None
    verification_library_id: Optional[str] = None
    failure_mode_template: Optional[str] = None
    hazardous_situation_template: Optional[str] = None
    priority: Optional[int] = 0
    is_active: bool = True
    condition_json: Optional[str] = None


class HazardGenerationRuleCreate(HazardGenerationRuleBase):
    pass


class HazardGenerationRuleUpdate(BaseModel):
    name: Optional[str] = None
    trigger_type: Optional[str] = None
    component_type: Optional[str] = None
    interface_type: Optional[str] = None
    node_type: Optional[str] = None
    hazard_library_id: Optional[str] = None
    harm_library_id: Optional[str] = None
    risk_control_library_id: Optional[str] = None
    verification_library_id: Optional[str] = None
    failure_mode_template: Optional[str] = None
    hazardous_situation_template: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    condition_json: Optional[str] = None


class HazardGenerationRuleOut(HazardGenerationRuleBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
