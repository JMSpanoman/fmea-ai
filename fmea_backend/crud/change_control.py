from sqlalchemy.orm import Session
from models.change_control import ChangeControl
from schemas.change_control import ChangeControlCreate, ChangeControlUpdate
from typing import List, Optional

def create_change_control(db: Session, project_id: int, change_control: ChangeControlCreate, user_id: str) -> ChangeControl:
    """Create a new change control entry"""
    db_change_control = ChangeControl(
        project_id=project_id,
        user_id=user_id,
        change_description=change_control.change_description,
        initiator=change_control.initiator,
        date_initiated=change_control.date_initiated,
        status=change_control.status,
        impact_assessment=change_control.impact_assessment,
        actions_required=change_control.actions_required,
        action_owner=change_control.action_owner,
        due_date=change_control.due_date,
        closure_summary=change_control.closure_summary,
        analysis_timestamp=change_control.analysis_timestamp,
        version=change_control.version
    )
    db.add(db_change_control)
    db.commit()
    db.refresh(db_change_control)
    return db_change_control

def get_change_controls_for_project(db: Session, project_id: int, user_id: str) -> List[ChangeControl]:
    """Get all change control entries for a project"""
    return db.query(ChangeControl).filter(
        ChangeControl.project_id == project_id,
        ChangeControl.user_id == user_id
    ).all()

def get_change_control(db: Session, change_control_id: int, user_id: str) -> Optional[ChangeControl]:
    """Get a specific change control entry by ID"""
    return db.query(ChangeControl).filter(
        ChangeControl.id == change_control_id,
        ChangeControl.user_id == user_id
    ).first()

def update_change_control(db: Session, change_control_id: int, change_control: ChangeControlUpdate, user_id: str) -> Optional[ChangeControl]:
    """Update a change control entry"""
    db_change_control = get_change_control(db, change_control_id, user_id)
    if not db_change_control:
        return None
    
    update_data = change_control.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_change_control, field, value)
    
    db.commit()
    db.refresh(db_change_control)
    return db_change_control

def delete_change_control(db: Session, change_control_id: int, user_id: str) -> bool:
    """Delete a change control entry"""
    db_change_control = get_change_control(db, change_control_id, user_id)
    if not db_change_control:
        return False
    
    db.delete(db_change_control)
    db.commit()
    return True 