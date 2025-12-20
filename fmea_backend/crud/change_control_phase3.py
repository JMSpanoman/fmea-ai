from sqlalchemy.orm import Session
from models.change_control import ChangeControl
from schemas.change_control import ChangeControlCreate, ChangeControlUpdate
from typing import List, Optional
import uuid

def create_change_control(db: Session, change_control: ChangeControlCreate) -> ChangeControl:
    """Create a new change control"""
    db_change = ChangeControl(
        id=str(uuid.uuid4()),
        project_id=change_control.project_id,
        title=change_control.title,
        description=change_control.description,
        reason=change_control.reason,
        status=change_control.status,
        linked_risk_ids=change_control.linked_risk_ids or [],
        ai_metadata=change_control.ai_metadata
    )
    db.add(db_change)
    db.commit()
    db.refresh(db_change)
    return db_change

def get_change_controls_by_project(db: Session, project_id: str) -> List[ChangeControl]:
    """Get all change controls for a project"""
    return db.query(ChangeControl).filter(ChangeControl.project_id == project_id).all()

def get_change_control(db: Session, change_id: str, project_id: str) -> Optional[ChangeControl]:
    """Get a specific change control"""
    return db.query(ChangeControl).filter(
        ChangeControl.id == change_id,
        ChangeControl.project_id == project_id
    ).first()

def update_change_control(db: Session, change_id: str, change_control: ChangeControlUpdate, project_id: str) -> Optional[ChangeControl]:
    """Update a change control"""
    db_change = get_change_control(db, change_id, project_id)
    if not db_change:
        return None
    
    update_data = change_control.model_dump(exclude_unset=True) if hasattr(change_control, 'model_dump') else change_control.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_change, field, value)
    
    db.commit()
    db.refresh(db_change)
    return db_change

def delete_change_control(db: Session, change_id: str, project_id: str) -> bool:
    """Delete a change control"""
    db_change = get_change_control(db, change_id, project_id)
    if not db_change:
        return False
    
    db.delete(db_change)
    db.commit()
    return True

