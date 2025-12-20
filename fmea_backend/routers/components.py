from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import component as component_schemas
from crud import component as component_crud
from crud import project as project_crud

router = APIRouter(prefix="/projects/{project_id}/components", tags=["components"])

@router.get("", response_model=list[component_schemas.ComponentOut])
def get_components(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all components for a project"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    components = component_crud.get_components_by_project(db, project_id)
    return components

@router.post("", response_model=component_schemas.ComponentOut, status_code=status.HTTP_201_CREATED)
def create_component(
    project_id: str,
    component: component_schemas.ComponentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new component"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return component_crud.create_component(db, component, project_id)

