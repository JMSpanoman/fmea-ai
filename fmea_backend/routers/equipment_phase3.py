from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import equipment as equipment_schemas
from crud import equipment_phase3 as equipment_crud
from crud import project as project_crud
from typing import List

router = APIRouter(prefix="/projects/{project_id}", tags=["Equipment Phase 3"])

@router.get("/equipment", response_model=List[equipment_schemas.EquipmentOut])
def get_equipment(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all equipment for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return equipment_crud.get_equipment_by_project(db, project_id)

@router.post("/equipment", response_model=equipment_schemas.EquipmentOut, status_code=status.HTTP_201_CREATED)
def create_equipment(
    project_id: str,
    equipment: equipment_schemas.EquipmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create new equipment"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches
    if hasattr(equipment, 'model_copy'):
        equipment = equipment.model_copy(update={'project_id': project_id})
    else:
        equipment_dict = equipment.dict() if hasattr(equipment, 'dict') else equipment.model_dump()
        equipment_dict['project_id'] = project_id
        equipment = equipment_schemas.EquipmentCreate(**equipment_dict)
    
    return equipment_crud.create_equipment(db, equipment)

@router.post("/equipment/{equipment_id}/calibrate", response_model=equipment_schemas.CalibrationRecordOut, status_code=status.HTTP_201_CREATED)
def calibrate_equipment(
    project_id: str,
    equipment_id: str,
    calibration: equipment_schemas.CalibrationRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a calibration record"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    equipment = equipment_crud.get_equipment(db, equipment_id, project_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    # Ensure equipment_id matches
    if hasattr(calibration, 'model_copy'):
        calibration = calibration.model_copy(update={'equipment_id': equipment_id})
    else:
        cal_dict = calibration.dict() if hasattr(calibration, 'dict') else calibration.model_dump()
        cal_dict['equipment_id'] = equipment_id
        calibration = equipment_schemas.CalibrationRecordCreate(**cal_dict)
    
    return equipment_crud.create_calibration_record(db, calibration)

@router.get("/equipment/{equipment_id}/calibration", response_model=List[equipment_schemas.CalibrationRecordOut])
def get_calibration_records(
    project_id: str,
    equipment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get calibration records for equipment"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    equipment = equipment_crud.get_equipment(db, equipment_id, project_id)
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    
    return equipment_crud.get_calibration_records(db, equipment_id)

