"""CRUD for Hazard Generation Rules (SmartRisk Phase 2)."""
from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from models.hazard_generation_rule import HazardGenerationRule
from schemas.hazard_generation_rule import (
    HazardGenerationRuleCreate,
    HazardGenerationRuleUpdate,
)


def _update_from_schema(obj, schema):
    data = schema.model_dump(exclude_unset=True)
    for field, value in data.items():
        if hasattr(obj, field):
            setattr(obj, field, value)


def create_rule(db: Session, data: HazardGenerationRuleCreate) -> HazardGenerationRule:
    row = HazardGenerationRule(**data.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_rule(db: Session, rule_id: str) -> Optional[HazardGenerationRule]:
    return db.query(HazardGenerationRule).filter(HazardGenerationRule.id == rule_id).first()


def list_rules(
    db: Session,
    trigger_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = 0,
    limit: int = 500,
) -> List[HazardGenerationRule]:
    q = db.query(HazardGenerationRule)
    if trigger_type:
        q = q.filter(HazardGenerationRule.trigger_type == trigger_type)
    if is_active is not None:
        q = q.filter(HazardGenerationRule.is_active == is_active)
    return (
        q.order_by(HazardGenerationRule.priority.desc(), HazardGenerationRule.created_at)
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_rule(
    db: Session, rule_id: str, data: HazardGenerationRuleUpdate
) -> Optional[HazardGenerationRule]:
    row = get_rule(db, rule_id)
    if not row:
        return None
    _update_from_schema(row, data)
    db.commit()
    db.refresh(row)
    return row


def delete_rule(db: Session, rule_id: str) -> bool:
    row = get_rule(db, rule_id)
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True
