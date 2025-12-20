from sqlalchemy.orm import Session
from models.risk_control import RiskControl
from schemas.risk_item import RiskControlCreate, RiskControlUpdate
from typing import List, Optional
import uuid

def create_risk_control(db: Session, risk_control: RiskControlCreate) -> RiskControl:
    """Create a new risk control"""
    db_control = RiskControl(
        id=str(uuid.uuid4()),
        risk_item_id=risk_control.risk_item_id,
        project_id=risk_control.project_id,
        control_name=risk_control.control_name,
        control_description=risk_control.control_description,
        control_type=risk_control.control_type,
        implementation_details=risk_control.implementation_details,
        verification_method=risk_control.verification_method,
        trace_to_design_input=risk_control.trace_to_design_input,
        trace_to_design_output=risk_control.trace_to_design_output,
        trace_to_verification_test=risk_control.trace_to_verification_test,
        status=risk_control.status or "proposed",
        owner=risk_control.owner,
        assigned_to=risk_control.assigned_to,
        proposed_date=risk_control.proposed_date,
        implemented_date=risk_control.implemented_date,
        verified_date=risk_control.verified_date,
        effectiveness_notes=risk_control.effectiveness_notes,
        ai_metadata=risk_control.ai_metadata
    )
    
    db.add(db_control)
    db.commit()
    db.refresh(db_control)
    return db_control

def get_risk_controls_by_risk_item(db: Session, risk_item_id: str) -> List[RiskControl]:
    """Get all risk controls for a risk item"""
    return db.query(RiskControl).filter(
        RiskControl.risk_item_id == risk_item_id
    ).all()

def get_risk_control(db: Session, control_id: str, risk_item_id: str) -> Optional[RiskControl]:
    """Get a specific risk control"""
    return db.query(RiskControl).filter(
        RiskControl.id == control_id,
        RiskControl.risk_item_id == risk_item_id
    ).first()

def update_risk_control(
    db: Session,
    control_id: str,
    risk_control: RiskControlUpdate,
    risk_item_id: str
) -> Optional[RiskControl]:
    """Update a risk control"""
    db_control = get_risk_control(db, control_id, risk_item_id)
    if not db_control:
        return None
    
    # Pydantic v2 compatibility
    if hasattr(risk_control, 'model_dump'):
        update_data = risk_control.model_dump(exclude_unset=True)
    else:
        update_data = risk_control.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_control, field, value)
    
    db.commit()
    db.refresh(db_control)
    return db_control

def delete_risk_control(db: Session, control_id: str, risk_item_id: str) -> bool:
    """Delete a risk control"""
    db_control = get_risk_control(db, control_id, risk_item_id)
    if not db_control:
        return False
    
    db.delete(db_control)
    db.commit()
    return True

