from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas import component as component_schemas
from crud import component as component_crud
from crud import project as project_crud
from typing import Union, List

router = APIRouter(prefix="/projects/{project_id}/components", tags=["components"], dependencies=[Depends(require_pro)])

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

@router.post(
    "",
    response_model=Union[component_schemas.ComponentOut, List[component_schemas.ComponentOut]],
    status_code=status.HTTP_201_CREATED,
)
def create_component(
    project_id: str,
    component: Union[component_schemas.ComponentCreate, List[component_schemas.ComponentBulkItem]] = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create components for a project.

    Backward compatible:
    - If body is an object => create a single component (legacy behavior).
    - If body is a list => bulk create/update + best-effort replace cleanup.
    """
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if isinstance(component, list):
        final_components, _stats = component_crud.bulk_create_replace_components(
            db, project_id=project_id, items=component
        )
        return final_components

    return component_crud.create_component(db, component, project_id)


@router.patch("/{component_id}", response_model=component_schemas.ComponentOut)
def patch_component(
    project_id: str,
    component_id: str,
    body: component_schemas.ComponentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a component (optional convenience endpoint)."""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    updated = component_crud.update_component(db, component_id, body, project_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Component not found")
    return updated

