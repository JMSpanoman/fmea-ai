from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class EquipmentBase(BaseModel):
    name: str
    serial_number: Optional[str] = None
    calibration_due: Optional[datetime] = None
    status: Optional[str] = None

class EquipmentCreate(EquipmentBase):
    project_id: str  # UUID

class EquipmentUpdate(BaseModel):
    name: Optional[str] = None
    serial_number: Optional[str] = None
    calibration_due: Optional[datetime] = None
    status: Optional[str] = None

class EquipmentOut(EquipmentBase):
    id: str  # UUID
    project_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

class CalibrationRecordBase(BaseModel):
    performed_at: datetime
    result: Optional[str] = None
    ai_metadata: Optional[Dict[str, Any]] = None

class CalibrationRecordCreate(CalibrationRecordBase):
    equipment_id: str  # UUID

class CalibrationRecordOut(CalibrationRecordBase):
    id: str  # UUID
    equipment_id: str  # UUID
    created_at: datetime

    class Config:
        from_attributes = True

