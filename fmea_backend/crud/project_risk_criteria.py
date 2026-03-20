from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from models.project_risk_criteria import ProjectRiskCriteria
from schemas.project_risk_criteria import ProjectRiskCriteriaCreate, ProjectRiskCriteriaUpdate


def list_criteria_for_project(db: Session, project_id: str) -> List[ProjectRiskCriteria]:
    return (
        db.query(ProjectRiskCriteria)
        .filter(ProjectRiskCriteria.project_id == project_id)
        .order_by(ProjectRiskCriteria.version.desc())
        .all()
    )


def get_criteria(db: Session, criteria_id: str, project_id: str) -> Optional[ProjectRiskCriteria]:
    return (
        db.query(ProjectRiskCriteria)
        .filter(ProjectRiskCriteria.id == criteria_id, ProjectRiskCriteria.project_id == project_id)
        .first()
    )


def get_next_version(db: Session, project_id: str) -> int:
    row = (
        db.query(ProjectRiskCriteria)
        .filter(ProjectRiskCriteria.project_id == project_id)
        .order_by(ProjectRiskCriteria.version.desc())
        .first()
    )
    return (row.version + 1) if row else 1


def create_criteria(db: Session, project_id: str, payload: ProjectRiskCriteriaCreate) -> ProjectRiskCriteria:
    ver = get_next_version(db, project_id)
    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    ent = ProjectRiskCriteria(
        project_id=project_id,
        version=ver,
        status="draft",
        **data,
    )
    db.add(ent)
    db.commit()
    db.refresh(ent)
    return ent


def update_criteria(
    db: Session, criteria_id: str, project_id: str, payload: ProjectRiskCriteriaUpdate
) -> Optional[ProjectRiskCriteria]:
    ent = get_criteria(db, criteria_id, project_id)
    if not ent:
        return None
    data = payload.model_dump(exclude_unset=True) if hasattr(payload, "model_dump") else payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(ent, k, v)
    db.commit()
    db.refresh(ent)
    return ent


def approve_criteria(
    db: Session, criteria_id: str, project_id: str, approval_metadata: Optional[dict]
) -> Optional[ProjectRiskCriteria]:
    ent = get_criteria(db, criteria_id, project_id)
    if not ent:
        return None
    # Archive other approved
    db.query(ProjectRiskCriteria).filter(
        ProjectRiskCriteria.project_id == project_id,
        ProjectRiskCriteria.status == "approved",
        ProjectRiskCriteria.id != criteria_id,
    ).update({"status": "archived"}, synchronize_session=False)
    ent.status = "approved"
    ent.approval_metadata = approval_metadata
    db.commit()
    db.refresh(ent)
    return ent


def get_latest_approved(db: Session, project_id: str) -> Optional[ProjectRiskCriteria]:
    return (
        db.query(ProjectRiskCriteria)
        .filter(ProjectRiskCriteria.project_id == project_id, ProjectRiskCriteria.status == "approved")
        .order_by(ProjectRiskCriteria.version.desc())
        .first()
    )


def get_latest_any(db: Session, project_id: str) -> Optional[ProjectRiskCriteria]:
    return (
        db.query(ProjectRiskCriteria)
        .filter(ProjectRiskCriteria.project_id == project_id)
        .order_by(ProjectRiskCriteria.version.desc())
        .first()
    )
