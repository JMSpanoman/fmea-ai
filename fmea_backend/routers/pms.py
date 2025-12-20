from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import pms as pms_schemas
from crud import pms as pms_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["PMS"])

@router.get("/pms", response_model=List[pms_schemas.PMSSignalOut])
def get_pms_signals(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all PMS signals for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return pms_crud.get_pms_signals_by_project(db, project_id)

@router.post("/pms", response_model=pms_schemas.PMSSignalOut, status_code=status.HTTP_201_CREATED)
def create_pms_signal(
    project_id: str,
    pms_signal: pms_schemas.PMSSignalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new PMS signal"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches path parameter (Pydantic v2 compatible)
    if hasattr(pms_signal, 'model_copy'):
        pms_signal = pms_signal.model_copy(update={'project_id': project_id})
    else:
        # Pydantic v1 fallback
        pms_signal_dict = pms_signal.dict() if hasattr(pms_signal, 'dict') else pms_signal.model_dump()
        pms_signal_dict['project_id'] = project_id
        pms_signal = pms_schemas.PMSSignalCreate(**pms_signal_dict)
    
    return pms_crud.create_pms_signal(db, pms_signal)

