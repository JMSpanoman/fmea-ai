from sqlalchemy.orm import Session
from typing import Optional
import uuid

from models.project_profile import ProjectProfile
from schemas.project_profile import ProjectProfileUpsert


def get_project_profile(db: Session, project_id: str) -> Optional[ProjectProfile]:
    return db.query(ProjectProfile).filter(ProjectProfile.project_id == project_id).first()


def upsert_project_profile(
    db: Session,
    *,
    project_id: str,
    data: ProjectProfileUpsert,
) -> ProjectProfile:
    existing = get_project_profile(db, project_id)

    # Pydantic v2 compatibility
    if hasattr(data, "model_dump"):
        payload = data.model_dump(exclude_unset=True)
    else:
        payload = data.dict(exclude_unset=True)

    if existing:
        for k, v in payload.items():
            setattr(existing, k, v)
        db.commit()
        db.refresh(existing)
        return existing

    rec = ProjectProfile(id=str(uuid.uuid4()), project_id=project_id, **payload)
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec

