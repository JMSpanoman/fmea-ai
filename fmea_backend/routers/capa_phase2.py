from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import capa as capa_schemas
from crud import capa as capa_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["CAPA Phase 2"])

@router.get("/capas", response_model=List[capa_schemas.CAPAOut])
def get_capas(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all CAPAs for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return capa_crud.get_capas_by_project(db, project_id)

@router.post("/capas", response_model=capa_schemas.CAPAOut, status_code=status.HTTP_201_CREATED)
def create_capa(
    project_id: str,
    capa: capa_schemas.CAPACreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new CAPA"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches path parameter (Pydantic v2 compatible)
    if hasattr(capa, 'model_copy'):
        capa = capa.model_copy(update={'project_id': project_id})
    else:
        # Pydantic v1 fallback
        capa_dict = capa.dict() if hasattr(capa, 'dict') else capa.model_dump()
        capa_dict['project_id'] = project_id
        capa = capa_schemas.CAPACreate(**capa_dict)
    
    return capa_crud.create_capa(db, capa)

@router.get("/capas/{capa_id}", response_model=capa_schemas.CAPAOut)
def get_capa(
    project_id: str,
    capa_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific CAPA"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    capa = capa_crud.get_capa(db, capa_id, project_id)
    if not capa:
        raise HTTPException(status_code=404, detail="CAPA not found")
    
    return capa

