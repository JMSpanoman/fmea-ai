from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from crud import project as project_crud
from crud import project_profile as profile_crud
from schemas.project_profile import ProjectProfileOut, ProjectProfileUpsert


router = APIRouter(prefix="/projects/{project_id}/profile", tags=["Project Profile"])


@router.get("", response_model=ProjectProfileOut)
def get_project_profile(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ownership enforcement
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    rec = profile_crud.get_project_profile(db, project_id)
    if not rec:
        raise HTTPException(status_code=404, detail="Project profile not found")
    return rec


@router.put("", response_model=ProjectProfileOut, status_code=status.HTTP_200_OK)
def upsert_project_profile(
    project_id: str,
    body: ProjectProfileUpsert,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Ownership enforcement
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    rec = profile_crud.upsert_project_profile(db, project_id=project_id, data=body)
    return rec

