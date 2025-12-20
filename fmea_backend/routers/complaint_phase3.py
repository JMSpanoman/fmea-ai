from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import complaint as complaint_schemas
from crud import complaint_phase3 as complaint_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["Complaint Handling Phase 3"])

@router.get("/complaints", response_model=List[complaint_schemas.ComplaintOut])
def get_complaints(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all complaints for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return complaint_crud.get_complaints_by_project(db, project_id)

@router.post("/complaints", response_model=complaint_schemas.ComplaintOut, status_code=status.HTTP_201_CREATED)
def create_complaint(
    project_id: str,
    complaint: complaint_schemas.ComplaintCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new complaint"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches
    if hasattr(complaint, 'model_copy'):
        complaint = complaint.model_copy(update={'project_id': project_id})
    else:
        complaint_dict = complaint.dict() if hasattr(complaint, 'dict') else complaint.model_dump()
        complaint_dict['project_id'] = project_id
        complaint = complaint_schemas.ComplaintCreate(**complaint_dict)
    
    return complaint_crud.create_complaint(db, complaint)

@router.post("/complaints/{complaint_id}/investigate", response_model=complaint_schemas.ComplaintOut)
def investigate_complaint(
    project_id: str,
    complaint_id: str,
    investigation: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add investigation to a complaint"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    update = complaint_schemas.ComplaintUpdate(investigation=investigation)
    updated = complaint_crud.update_complaint(db, complaint_id, update, project_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    return updated

