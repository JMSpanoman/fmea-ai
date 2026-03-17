from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas import quality_event as qe_schemas
from crud import quality_event_phase3 as qe_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["Quality Events Phase 3"], dependencies=[Depends(require_pro)])

@router.get("/events", response_model=List[qe_schemas.QualityEventOut])
def get_quality_events(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all quality events for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return qe_crud.get_quality_events_by_project(db, project_id)

@router.post("/events", response_model=qe_schemas.QualityEventOut, status_code=status.HTTP_201_CREATED)
def create_quality_event(
    project_id: str,
    event: qe_schemas.QualityEventCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new quality event"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches
    if hasattr(event, 'model_copy'):
        event = event.model_copy(update={'project_id': project_id})
    else:
        event_dict = event.dict() if hasattr(event, 'dict') else event.model_dump()
        event_dict['project_id'] = project_id
        event = qe_schemas.QualityEventCreate(**event_dict)
    
    return qe_crud.create_quality_event(db, event)

@router.post("/events/{event_id}/link-risks", response_model=qe_schemas.QualityEventOut)
def link_risks_to_event(
    project_id: str,
    event_id: str,
    request: qe_schemas.QualityEventLinkRisksRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Link risks to a quality event"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated = qe_crud.link_risks_to_event(db, event_id, project_id, request.risk_ids)
    if not updated:
        raise HTTPException(status_code=404, detail="Quality event not found")
    
    return updated

