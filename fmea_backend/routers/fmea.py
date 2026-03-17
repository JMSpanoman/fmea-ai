from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas import fmea as fmea_schemas
from crud import fmea as fmea_crud
from crud import project as project_crud

router = APIRouter(prefix="/projects/{project_id}/fmea", tags=["fmea"], dependencies=[Depends(require_pro)])

@router.get("", response_model=list[fmea_schemas.FMEARowOut])
def get_fmea_rows(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all FMEA rows for a project"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    rows = fmea_crud.get_fmea_rows_by_project(db, project_id)
    return rows

@router.post("", response_model=fmea_schemas.FMEARowOut, status_code=status.HTTP_201_CREATED)
def create_fmea_row(
    project_id: str,
    fmea_row: fmea_schemas.FMEARowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new FMEA row"""
    # Verify project belongs to user and matches path parameter
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches path parameter (Pydantic v2 compatible)
    if hasattr(fmea_row, 'model_copy'):
        fmea_row = fmea_row.model_copy(update={'project_id': project_id})
    else:
        # Pydantic v1 fallback
        fmea_row_dict = fmea_row.dict() if hasattr(fmea_row, 'dict') else fmea_row.model_dump()
        fmea_row_dict['project_id'] = project_id
        fmea_row = fmea_schemas.FMEARowCreate(**fmea_row_dict)
    
    return fmea_crud.create_fmea_row(db, fmea_row)

@router.get("/{fmea_row_id}", response_model=fmea_schemas.FMEARowOut)
def get_fmea_row(
    project_id: str,
    fmea_row_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific FMEA row"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    row = fmea_crud.get_fmea_row(db, fmea_row_id, project_id)
    if not row:
        raise HTTPException(status_code=404, detail="FMEA row not found")
    return row

@router.put("/{fmea_row_id}", response_model=fmea_schemas.FMEARowOut)
def update_fmea_row(
    project_id: str,
    fmea_row_id: str,
    fmea_row: fmea_schemas.FMEARowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an FMEA row"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    updated_row = fmea_crud.update_fmea_row(db, fmea_row_id, fmea_row, project_id)
    if not updated_row:
        raise HTTPException(status_code=404, detail="FMEA row not found")
    return updated_row

@router.delete("/{fmea_row_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_fmea_row(
    project_id: str,
    fmea_row_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an FMEA row"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    success = fmea_crud.delete_fmea_row(db, fmea_row_id, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="FMEA row not found")
    return None

@router.get("/{fmea_row_id}/history")
def get_fmea_history(
    project_id: str,
    fmea_row_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get version history for an FMEA row"""
    # Verify project belongs to user
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    versions = fmea_crud.get_fmea_version_history(db, fmea_row_id, project_id)
    return {"versions": versions}

