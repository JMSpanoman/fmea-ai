from sqlalchemy.orm import Session
from models.risk_control import RiskControl
from models.trace_link import TraceLink
from schemas.risk_item import RiskControlCreate, RiskControlUpdate
from typing import List, Optional
import uuid


def _ensure_vv_activity_for_control(db: Session, control: RiskControl) -> None:
    """
    Ensure a draft V&V activity exists for this risk control's verification_method.

    - Creates a draft DesignOutput placeholder if trace_to_design_output is missing (required by VVTest model).
    - Creates a draft VVTest with test_method derived from verification_method (structured text).
    - Creates a TraceLink risk_control -> vv_test (link_type='verified_by') for traceability.
    - Sets control.trace_to_verification_test, but does NOT mark verification as complete.
    """
    vm = (getattr(control, "verification_method", None) or "").strip()
    if not vm:
        return

    # If we already have a linked VV test, do nothing.
    if getattr(control, "trace_to_verification_test", None):
        return

    # Ensure there is a DesignOutput to attach the VVTest to (VVTest requires design_output_id).
    design_output_id = (getattr(control, "trace_to_design_output", None) or "").strip()
    if not design_output_id:
        from crud import design_control as design_crud
        from schemas.design_control import DesignOutputCreate

        do = design_crud.create_design_output(
            db,
            DesignOutputCreate(
                project_id=control.project_id,
                source="ai",
                title=f"[DRAFT] Design Output placeholder for {control.control_name}",
                text=f"[DRAFT] Placeholder design output used to anchor verification activity for risk control {control.control_key or control.id}.",
                description=None,
                document_ref=None,
                status="draft",
                linked_input_id=None,
            ),
            created_by=getattr(control, "created_by", None),
        )
        design_output_id = do.id
        control.trace_to_design_output = design_output_id
        db.commit()
        db.refresh(control)

    # Create VV test
    from crud import vv as vv_crud
    from schemas.vv import VVTestCreate

    vv_test = vv_crud.create_vv_test(
        db,
        VVTestCreate(
            project_id=control.project_id,
            design_output_id=design_output_id,
            test_method=vm,
            acceptance_criteria="TBD (define pass/fail criteria for this risk control verification).",
            rationale=f"[DRAFT] Auto-created from RiskControl {control.control_key or control.id} verification_method.",
            ai_metadata={"source": "risk_control_verification_method", "risk_control_id": control.id},
        ),
        created_by=getattr(control, "created_by", None),
    )

    # Create trace link if missing
    existing_link = (
        db.query(TraceLink)
        .filter(
            TraceLink.project_id == control.project_id,
            TraceLink.from_type == "risk_control",
            TraceLink.from_id == control.id,
            TraceLink.to_type == "vv_test",
            TraceLink.to_id == vv_test.id,
        )
        .first()
    )
    if not existing_link:
        db.add(
            TraceLink(
                id=str(uuid.uuid4()),
                project_id=control.project_id,
                from_type="risk_control",
                from_id=control.id,
                to_type="vv_test",
                to_id=vv_test.id,
                link_type="verified_by",
                rationale="Auto-created from RiskControl.verification_method; requires human review and execution.",
            )
        )
        db.commit()

    # Link back from control (do not set verified_date; keep draft)
    control.trace_to_verification_test = vv_test.id
    db.commit()
    db.refresh(control)

def _generate_control_key(db: Session, risk_item_id: str) -> str:
    """Generate a unique control_key for a risk item (e.g., RC-001, RC-002)"""
    # Get the highest existing control_key number for this risk item
    existing_keys = db.query(RiskControl.control_key).filter(
        RiskControl.risk_item_id == risk_item_id,
        RiskControl.control_key.isnot(None)
    ).all()
    
    max_num = 0
    for (key,) in existing_keys:
        if key and key.startswith('RC-'):
            try:
                num = int(key[3:])
                max_num = max(max_num, num)
            except ValueError:
                pass
    
    # Generate next key
    next_num = max_num + 1
    return f"RC-{next_num:03d}"

def create_risk_control(db: Session, risk_control: RiskControlCreate, created_by: Optional[str] = None) -> RiskControl:
    """Create a new risk control"""
    # Generate control_key if not provided
    control_key = getattr(risk_control, 'control_key', None)
    if not control_key:
        control_key = _generate_control_key(db, risk_control.risk_item_id)
    
    db_control = RiskControl(
        id=str(uuid.uuid4()),
        risk_item_id=risk_control.risk_item_id,
        project_id=risk_control.project_id,
        control_key=control_key,
        created_by=created_by,
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
    _ensure_vv_activity_for_control(db, db_control)
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
    _ensure_vv_activity_for_control(db, db_control)
    return db_control

def delete_risk_control(db: Session, control_id: str, risk_item_id: str) -> bool:
    """Delete a risk control"""
    db_control = get_risk_control(db, control_id, risk_item_id)
    if not db_control:
        return False
    
    db.delete(db_control)
    db.commit()
    return True

