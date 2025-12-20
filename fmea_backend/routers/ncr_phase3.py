from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import ncr as ncr_schemas
from crud import ncr_phase3 as ncr_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["NCR Phase 3"])

@router.get("/ncrs", response_model=List[ncr_schemas.NCROut])
def get_ncrs(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all NCRs for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return ncr_crud.get_ncrs_by_project(db, project_id)

@router.post("/ncrs", response_model=ncr_schemas.NCROut, status_code=status.HTTP_201_CREATED)
def create_ncr(
    project_id: str,
    ncr: ncr_schemas.NCRCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new NCR"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches
    if hasattr(ncr, 'model_copy'):
        ncr = ncr.model_copy(update={'project_id': project_id})
    else:
        ncr_dict = ncr.dict() if hasattr(ncr, 'dict') else ncr.model_dump()
        ncr_dict['project_id'] = project_id
        ncr = ncr_schemas.NCRCreate(**ncr_dict)
    
    return ncr_crud.create_ncr(db, ncr)

@router.post("/ncrs/{ncr_id}/close", response_model=ncr_schemas.NCROut)
def close_ncr(
    project_id: str,
    ncr_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close an NCR"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    closed = ncr_crud.close_ncr(db, ncr_id, project_id)
    if not closed:
        raise HTTPException(status_code=404, detail="NCR not found")
    
    return closed

