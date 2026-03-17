"""CRUD for Risk Knowledge Base libraries (Hazard, Harm, Risk Control, Verification)."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models.hazard_library import HazardLibrary
from models.harm_library import HarmLibrary
from models.risk_control_library import RiskControlLibrary
from models.verification_library import VerificationLibrary
from schemas.risk_knowledge_base import (
    HazardLibraryCreate,
    HazardLibraryUpdate,
    HarmLibraryCreate,
    HarmLibraryUpdate,
    RiskControlLibraryCreate,
    RiskControlLibraryUpdate,
    VerificationLibraryCreate,
    VerificationLibraryUpdate,
)


def _update_from_schema(obj, schema):
    if hasattr(schema, "model_dump"):
        data = schema.model_dump(exclude_unset=True)
    else:
        data = schema.dict(exclude_unset=True)
    for field, value in data.items():
        if hasattr(obj, field):
            setattr(obj, field, value)


# ----- Hazard Library -----
def create_hazard_library(db: Session, item: HazardLibraryCreate) -> HazardLibrary:
    data = item.model_dump() if hasattr(item, "model_dump") else item.dict()
    row = HazardLibrary(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_hazard_library(db: Session, item_id: str) -> Optional[HazardLibrary]:
    return db.query(HazardLibrary).filter(HazardLibrary.id == item_id).first()


def get_hazard_libraries(
    db: Session,
    skip: int = 0,
    limit: int = 500,
    is_active: Optional[bool] = None,
    category: Optional[str] = None,
    search: Optional[str] = None,
) -> List[HazardLibrary]:
    q = db.query(HazardLibrary)
    if is_active is not None:
        q = q.filter(HazardLibrary.is_active == is_active)
    if category:
        q = q.filter(HazardLibrary.category == category)
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                HazardLibrary.name.ilike(term),
                HazardLibrary.code.ilike(term),
                HazardLibrary.description.ilike(term),
            )
        )
    return q.order_by(HazardLibrary.name).offset(skip).limit(limit).all()


def update_hazard_library(
    db: Session, item_id: str, item: HazardLibraryUpdate
) -> Optional[HazardLibrary]:
    row = get_hazard_library(db, item_id)
    if not row:
        return None
    _update_from_schema(row, item)
    db.commit()
    db.refresh(row)
    return row


def delete_hazard_library(db: Session, item_id: str) -> bool:
    row = get_hazard_library(db, item_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


# ----- Harm Library -----
def create_harm_library(db: Session, item: HarmLibraryCreate) -> HarmLibrary:
    data = item.model_dump() if hasattr(item, "model_dump") else item.dict()
    row = HarmLibrary(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_harm_library(db: Session, item_id: str) -> Optional[HarmLibrary]:
    return db.query(HarmLibrary).filter(HarmLibrary.id == item_id).first()


def get_harm_libraries(
    db: Session,
    skip: int = 0,
    limit: int = 500,
    search: Optional[str] = None,
) -> List[HarmLibrary]:
    q = db.query(HarmLibrary)
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                HarmLibrary.harm_name.ilike(term),
                HarmLibrary.harm_id.ilike(term),
                HarmLibrary.description.ilike(term),
                HarmLibrary.clinical_examples.ilike(term),
            )
        )
    return q.order_by(HarmLibrary.harm_name).offset(skip).limit(limit).all()


def update_harm_library(
    db: Session, item_id: str, item: HarmLibraryUpdate
) -> Optional[HarmLibrary]:
    row = get_harm_library(db, item_id)
    if not row:
        return None
    _update_from_schema(row, item)
    db.commit()
    db.refresh(row)
    return row


def delete_harm_library(db: Session, item_id: str) -> bool:
    row = get_harm_library(db, item_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


# ----- Risk Control Library -----
def create_risk_control_library(
    db: Session, item: RiskControlLibraryCreate
) -> RiskControlLibrary:
    data = item.model_dump() if hasattr(item, "model_dump") else item.dict()
    row = RiskControlLibrary(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_risk_control_library(db: Session, item_id: str) -> Optional[RiskControlLibrary]:
    return db.query(RiskControlLibrary).filter(RiskControlLibrary.id == item_id).first()


def get_risk_control_libraries(
    db: Session,
    skip: int = 0,
    limit: int = 500,
    control_type: Optional[str] = None,
    search: Optional[str] = None,
) -> List[RiskControlLibrary]:
    q = db.query(RiskControlLibrary)
    if control_type:
        q = q.filter(RiskControlLibrary.control_type == control_type)
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                RiskControlLibrary.control_name.ilike(term),
                RiskControlLibrary.control_id.ilike(term),
                RiskControlLibrary.description.ilike(term),
                RiskControlLibrary.example_application.ilike(term),
                RiskControlLibrary.typical_verification_method.ilike(term),
                RiskControlLibrary.related_standards.ilike(term),
            )
        )
    return q.order_by(RiskControlLibrary.control_name).offset(skip).limit(limit).all()


def update_risk_control_library(
    db: Session, item_id: str, item: RiskControlLibraryUpdate
) -> Optional[RiskControlLibrary]:
    row = get_risk_control_library(db, item_id)
    if not row:
        return None
    _update_from_schema(row, item)
    db.commit()
    db.refresh(row)
    return row


def delete_risk_control_library(db: Session, item_id: str) -> bool:
    row = get_risk_control_library(db, item_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


# ----- Verification Library -----
def create_verification_library(
    db: Session, item: VerificationLibraryCreate
) -> VerificationLibrary:
    data = item.model_dump() if hasattr(item, "model_dump") else item.dict()
    row = VerificationLibrary(**data)
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_verification_library(db: Session, item_id: str) -> Optional[VerificationLibrary]:
    return db.query(VerificationLibrary).filter(VerificationLibrary.id == item_id).first()


def get_verification_libraries(
    db: Session,
    skip: int = 0,
    limit: int = 500,
    search: Optional[str] = None,
) -> List[VerificationLibrary]:
    q = db.query(VerificationLibrary)
    if search:
        term = f"%{search}%"
        q = q.filter(
            or_(
                VerificationLibrary.verification_method.ilike(term),
                VerificationLibrary.verification_id.ilike(term),
                VerificationLibrary.description.ilike(term),
                VerificationLibrary.applicable_control_types.ilike(term),
                VerificationLibrary.standard_reference.ilike(term),
                VerificationLibrary.typical_test_output.ilike(term),
            )
        )
    return q.order_by(VerificationLibrary.verification_method).offset(skip).limit(limit).all()


def update_verification_library(
    db: Session, item_id: str, item: VerificationLibraryUpdate
) -> Optional[VerificationLibrary]:
    row = get_verification_library(db, item_id)
    if not row:
        return None
    _update_from_schema(row, item)
    db.commit()
    db.refresh(row)
    return row


def delete_verification_library(db: Session, item_id: str) -> bool:
    row = get_verification_library(db, item_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True
