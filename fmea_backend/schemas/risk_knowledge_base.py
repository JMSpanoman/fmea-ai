"""Pydantic schemas for Risk Knowledge Base libraries (Hazard, Harm, Risk Control, Verification)."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ----- Hazard Library -----
class HazardLibraryBase(BaseModel):
    code: Optional[str] = None
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    source_standard: Optional[str] = None
    is_active: bool = True


class HazardLibraryCreate(HazardLibraryBase):
    pass


class HazardLibraryUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    source_standard: Optional[str] = None
    is_active: Optional[bool] = None


class HazardLibraryOut(HazardLibraryBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ----- Harm Library -----
class HarmLibraryBase(BaseModel):
    harm_id: Optional[str] = None  # e.g. HR-001
    harm_name: str
    description: Optional[str] = None
    severity_guidance: Optional[str] = None
    clinical_examples: Optional[str] = None


class HarmLibraryCreate(HarmLibraryBase):
    pass


class HarmLibraryUpdate(BaseModel):
    harm_id: Optional[str] = None
    harm_name: Optional[str] = None
    description: Optional[str] = None
    severity_guidance: Optional[str] = None
    clinical_examples: Optional[str] = None


class HarmLibraryOut(HarmLibraryBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ----- Risk Control Library -----
class RiskControlLibraryBase(BaseModel):
    control_id: Optional[str] = None  # e.g. RC-001
    control_name: str
    control_type: str = "protective"  # design | protective | information
    description: Optional[str] = None
    example_application: Optional[str] = None
    typical_verification_method: Optional[str] = None
    related_standards: Optional[str] = None


class RiskControlLibraryCreate(RiskControlLibraryBase):
    pass


class RiskControlLibraryUpdate(BaseModel):
    control_id: Optional[str] = None
    control_name: Optional[str] = None
    control_type: Optional[str] = None
    description: Optional[str] = None
    example_application: Optional[str] = None
    typical_verification_method: Optional[str] = None
    related_standards: Optional[str] = None


class RiskControlLibraryOut(RiskControlLibraryBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ----- Verification Library -----
class VerificationLibraryBase(BaseModel):
    verification_id: Optional[str] = None  # e.g. V-001
    verification_method: str
    description: Optional[str] = None
    applicable_control_types: Optional[str] = None  # e.g. design, protective, information
    standard_reference: Optional[str] = None
    typical_test_output: Optional[str] = None


class VerificationLibraryCreate(VerificationLibraryBase):
    pass


class VerificationLibraryUpdate(BaseModel):
    verification_id: Optional[str] = None
    verification_method: Optional[str] = None
    description: Optional[str] = None
    applicable_control_types: Optional[str] = None
    standard_reference: Optional[str] = None
    typical_test_output: Optional[str] = None


class VerificationLibraryOut(VerificationLibraryBase):
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
