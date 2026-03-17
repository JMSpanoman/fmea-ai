from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas import change_control as cc_schemas
from crud import change_control_phase3 as cc_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["Change Control Phase 3"], dependencies=[Depends(require_pro)])

@router.get("/changes", response_model=List[cc_schemas.ChangeControlOut])
def get_change_controls(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all change controls for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return cc_crud.get_change_controls_by_project(db, project_id)

@router.get("/changes/{change_id}", response_model=cc_schemas.ChangeControlOut)
def get_change_control(
    project_id: str,
    change_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific change control"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    change_control = cc_crud.get_change_control(db, change_id, project_id)
    if not change_control:
        raise HTTPException(status_code=404, detail="Change control not found")
    
    return change_control

@router.post("/changes", response_model=cc_schemas.ChangeControlOut, status_code=status.HTTP_201_CREATED)
def create_change_control(
    project_id: str,
    change_control: cc_schemas.ChangeControlCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new change control"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches
    if hasattr(change_control, 'model_copy'):
        change_control = change_control.model_copy(update={'project_id': project_id})
    else:
        cc_dict = change_control.dict() if hasattr(change_control, 'dict') else change_control.model_dump()
        cc_dict['project_id'] = project_id
        change_control = cc_schemas.ChangeControlCreate(**cc_dict)
    
    return cc_crud.create_change_control(db, change_control)

@router.put("/changes/{change_id}", response_model=cc_schemas.ChangeControlOut)
def update_change_control(
    project_id: str,
    change_id: str,
    change_control: cc_schemas.ChangeControlUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a change control"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated = cc_crud.update_change_control(db, change_id, change_control, project_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Change control not found")
    
    return updated

@router.post("/changes/{change_id}/approve", response_model=cc_schemas.ChangeControlOut)
def approve_change_control(
    project_id: str,
    change_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Approve a change control with status validation"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get current change control
    current_change = cc_crud.get_change_control(db, change_id, project_id)
    if not current_change:
        raise HTTPException(status_code=404, detail="Change control not found")
    
    # Validate status transition
    from business_logic.approval_workflow import validate_change_control_status_transition
    if not validate_change_control_status_transition(current_change.status, "approved"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status transition from {current_change.status} to approved"
        )
    
    # Use business logic for approval
    from business_logic.approval_workflow import process_change_control_approval
    result = process_change_control_approval(db, change_id, project_id, current_user)
    if not result:
        raise HTTPException(status_code=404, detail="Change control not found")
    
    return result["change_control"]

