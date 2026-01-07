from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import project as project_schemas
from crud import project as project_crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("", response_model=list[project_schemas.ProjectOut])
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all projects for the current user"""
    projects = project_crud.get_projects_by_user(db, current_user.id)
    return projects

@router.post("", response_model=project_schemas.ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project: project_schemas.ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new project"""
    try:
        logger.info(f"Creating project '{project.name}' for user {current_user.id}")
        created_project = project_crud.create_project(db, project, current_user.id)
        logger.info(f"Successfully created project {created_project.id}")
        return created_project
    except Exception as e:
        logger.error(f"Error creating project: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )

@router.get("/{project_id}", response_model=project_schemas.ProjectOut)
def get_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a project"""
    success = project_crud.delete_project(db, project_id, current_user.id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return None
