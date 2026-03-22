"""CRUD for persisted PMS generated plans."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session

from models.pms_generated_plan import PmsGeneratedPlan


def next_plan_version(db: Session, project_id: str) -> int:
    last = (
        db.query(PmsGeneratedPlan)
        .filter(PmsGeneratedPlan.project_id == project_id)
        .order_by(desc(PmsGeneratedPlan.version))
        .first()
    )
    if last is None:
        return 1
    return int(getattr(last, "version", 1) or 1) + 1


def create_pms_generated_plan(
    db: Session,
    *,
    generation_id: str,
    project_id: str,
    user_id: str,
    device_name: str,
    intended_use: str,
    summary: Optional[str],
    status: str,
    version: int,
    payload_json: Dict[str, Any],
) -> PmsGeneratedPlan:
    row = PmsGeneratedPlan(
        id=generation_id,
        project_id=project_id,
        user_id=user_id,
        device_name=device_name,
        intended_use=intended_use,
        summary=summary,
        status=status,
        version=version,
        payload_json=payload_json,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


def get_pms_generated_plan(db: Session, generation_id: str) -> Optional[PmsGeneratedPlan]:
    return db.query(PmsGeneratedPlan).filter(PmsGeneratedPlan.id == generation_id).first()


def list_pms_generated_plans_by_project(db: Session, project_id: str) -> List[PmsGeneratedPlan]:
    return (
        db.query(PmsGeneratedPlan)
        .filter(PmsGeneratedPlan.project_id == project_id)
        .order_by(desc(PmsGeneratedPlan.created_at))
        .all()
    )
