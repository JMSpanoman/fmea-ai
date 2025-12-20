from sqlalchemy.orm import Session
from models.pms_signal import PMSSignal
from schemas.pms import PMSSignalCreate, PMSSignalUpdate
from typing import List, Optional
import uuid

def create_pms_signal(db: Session, pms_signal: PMSSignalCreate) -> PMSSignal:
    """Create a new PMS signal"""
    db_signal = PMSSignal(
        id=str(uuid.uuid4()),
        project_id=pms_signal.project_id,
        signal_type=pms_signal.signal_type,
        description=pms_signal.description,
        linked_risk_ids=pms_signal.linked_risk_ids or [],
        ai_metadata=pms_signal.ai_metadata
    )
    db.add(db_signal)
    db.commit()
    db.refresh(db_signal)
    return db_signal

def get_pms_signals_by_project(db: Session, project_id: str) -> List[PMSSignal]:
    """Get all PMS signals for a project"""
    return db.query(PMSSignal).filter(PMSSignal.project_id == project_id).all()

def get_pms_signal(db: Session, signal_id: str, project_id: str) -> Optional[PMSSignal]:
    """Get a specific PMS signal"""
    return db.query(PMSSignal).filter(
        PMSSignal.id == signal_id,
        PMSSignal.project_id == project_id
    ).first()

def update_pms_signal(db: Session, signal_id: str, pms_signal: PMSSignalUpdate, project_id: str) -> Optional[PMSSignal]:
    """Update a PMS signal"""
    db_signal = get_pms_signal(db, signal_id, project_id)
    if not db_signal:
        return None
    
    update_data = pms_signal.model_dump(exclude_unset=True) if hasattr(pms_signal, 'model_dump') else pms_signal.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_signal, field, value)
    
    db.commit()
    db.refresh(db_signal)
    return db_signal

def delete_pms_signal(db: Session, signal_id: str, project_id: str) -> bool:
    """Delete a PMS signal"""
    db_signal = get_pms_signal(db, signal_id, project_id)
    if not db_signal:
        return False
    
    db.delete(db_signal)
    db.commit()
    return True

