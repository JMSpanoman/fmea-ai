from sqlalchemy.orm import Session
from models.equipment import Equipment, CalibrationRecord
from schemas.equipment import EquipmentCreate, EquipmentUpdate, CalibrationRecordCreate
from typing import List, Optional
import uuid
from datetime import timedelta

def create_equipment(db: Session, equipment: EquipmentCreate) -> Equipment:
    """Create new equipment"""
    db_equipment = Equipment(
        id=str(uuid.uuid4()),
        project_id=equipment.project_id,
        name=equipment.name,
        serial_number=equipment.serial_number,
        calibration_due=equipment.calibration_due,
        status=equipment.status
    )
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def get_equipment_by_project(db: Session, project_id: str) -> List[Equipment]:
    """Get all equipment for a project"""
    return db.query(Equipment).filter(Equipment.project_id == project_id).all()

def get_equipment(db: Session, equipment_id: str, project_id: str) -> Optional[Equipment]:
    """Get specific equipment"""
    return db.query(Equipment).filter(
        Equipment.id == equipment_id,
        Equipment.project_id == project_id
    ).first()

def update_equipment(db: Session, equipment_id: str, equipment: EquipmentUpdate, project_id: str) -> Optional[Equipment]:
    """Update equipment"""
    db_equipment = get_equipment(db, equipment_id, project_id)
    if not db_equipment:
        return None
    
    update_data = equipment.model_dump(exclude_unset=True) if hasattr(equipment, 'model_dump') else equipment.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_equipment, field, value)
    
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

def create_calibration_record(db: Session, calibration: CalibrationRecordCreate) -> CalibrationRecord:
    """Create a calibration record and update equipment calibration_due"""
    db_cal = CalibrationRecord(
        id=str(uuid.uuid4()),
        equipment_id=calibration.equipment_id,
        performed_at=calibration.performed_at,
        result=calibration.result,
        ai_metadata=calibration.ai_metadata
    )
    db.add(db_cal)
    
    # Update equipment calibration_due (typically 1 year from calibration)
    equipment = db.query(Equipment).filter(Equipment.id == calibration.equipment_id).first()
    if equipment:
        from datetime import datetime, timezone
        equipment.calibration_due = calibration.performed_at + timedelta(days=365)
    
    db.commit()
    db.refresh(db_cal)
    return db_cal

def get_calibration_records(db: Session, equipment_id: str) -> List[CalibrationRecord]:
    """Get all calibration records for equipment"""
    return db.query(CalibrationRecord).filter(
        CalibrationRecord.equipment_id == equipment_id
    ).order_by(CalibrationRecord.performed_at.desc()).all()

