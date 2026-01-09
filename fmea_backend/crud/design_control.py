from sqlalchemy.orm import Session
from models.design_input import DesignInput
from models.design_output import DesignOutput
from schemas.design_control import DesignInputCreate, DesignInputUpdate, DesignOutputCreate, DesignOutputUpdate
from typing import List, Optional
import uuid

def _generate_di_key(db: Session, project_id: str) -> str:
    """Generate a unique di_key for a project (e.g., DI-001, DI-002)"""
    existing_keys = db.query(DesignInput.di_key).filter(
        DesignInput.project_id == project_id,
        DesignInput.di_key.isnot(None)
    ).all()
    
    max_num = 0
    for (key,) in existing_keys:
        if key and key.startswith('DI-'):
            try:
                num = int(key[3:])
                max_num = max(max_num, num)
            except ValueError:
                pass
    
    next_num = max_num + 1
    return f"DI-{next_num:03d}"

def _generate_do_key(db: Session, project_id: str) -> str:
    """Generate a unique do_key for a project (e.g., DO-001, DO-002)"""
    existing_keys = db.query(DesignOutput.do_key).filter(
        DesignOutput.project_id == project_id,
        DesignOutput.do_key.isnot(None)
    ).all()
    
    max_num = 0
    for (key,) in existing_keys:
        if key and key.startswith('DO-'):
            try:
                num = int(key[3:])
                max_num = max(max_num, num)
            except ValueError:
                pass
    
    next_num = max_num + 1
    return f"DO-{next_num:03d}"

# Design Input CRUD
def create_design_input(db: Session, design_input: DesignInputCreate, created_by: Optional[str] = None) -> DesignInput:
    """Create a new design input"""
    # Generate di_key if not provided
    di_key = getattr(design_input, 'di_key', None)
    if not di_key:
        di_key = _generate_di_key(db, design_input.project_id)
    
    # Normalize fields from schema (support both legacy and new names)
    title = getattr(design_input, 'title', None)
    requirement_text = getattr(design_input, 'requirement_text', None)
    requirement = getattr(design_input, 'requirement', None) or requirement_text or design_input.text
    status = getattr(design_input, 'status', 'draft')

    # Ensure legacy text is populated so older UIs still work
    text = design_input.text or requirement_text or requirement or ""
    
    db_input = DesignInput(
        id=str(uuid.uuid4()),
        project_id=design_input.project_id,
        di_key=di_key,
        title=title,
        source=design_input.source,
        text=text,
        requirement=requirement,
        status=status,
        created_by=created_by,
        linked_risk_ids=design_input.linked_risk_ids or []
    )
    db.add(db_input)
    db.commit()
    db.refresh(db_input)
    return db_input

def get_design_inputs_by_project(db: Session, project_id: str) -> List[DesignInput]:
    """Get all design inputs for a project"""
    return db.query(DesignInput).filter(DesignInput.project_id == project_id).all()

def get_design_input(db: Session, input_id: str, project_id: str) -> Optional[DesignInput]:
    """Get a specific design input"""
    return db.query(DesignInput).filter(
        DesignInput.id == input_id,
        DesignInput.project_id == project_id
    ).first()

def update_design_input(db: Session, input_id: str, design_input: DesignInputUpdate, project_id: str) -> Optional[DesignInput]:
    """Update a design input"""
    db_input = get_design_input(db, input_id, project_id)
    if not db_input:
        return None
    
    update_data = design_input.model_dump(exclude_unset=True) if hasattr(design_input, 'model_dump') else design_input.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_input, field, value)
    
    db.commit()
    db.refresh(db_input)
    return db_input

def delete_design_input(db: Session, input_id: str, project_id: str) -> bool:
    """Delete a design input"""
    db_input = get_design_input(db, input_id, project_id)
    if not db_input:
        return False
    
    db.delete(db_input)
    db.commit()
    return True

# Design Output CRUD
def create_design_output(db: Session, design_output: DesignOutputCreate, created_by: Optional[str] = None) -> DesignOutput:
    """Create a new design output"""
    # Generate do_key if not provided
    do_key = getattr(design_output, 'do_key', None)
    if not do_key:
        do_key = _generate_do_key(db, design_output.project_id)
    
    # Get title and description from schema (support both text and description fields)
    title = getattr(design_output, 'title', None)
    description = getattr(design_output, 'description', None) or design_output.text
    document_ref = getattr(design_output, 'document_ref', None)
    status = getattr(design_output, 'status', 'draft')
    
    db_output = DesignOutput(
        id=str(uuid.uuid4()),
        project_id=design_output.project_id,
        do_key=do_key,
        title=title,
        source=design_output.source,
        text=design_output.text,
        description=description,
        document_ref=document_ref,
        status=status,
        created_by=created_by,
        linked_input_id=design_output.linked_input_id
    )
    db.add(db_output)
    db.commit()
    db.refresh(db_output)
    return db_output

def get_design_outputs_by_project(db: Session, project_id: str) -> List[DesignOutput]:
    """Get all design outputs for a project"""
    return db.query(DesignOutput).filter(DesignOutput.project_id == project_id).all()

def get_design_output(db: Session, output_id: str, project_id: str) -> Optional[DesignOutput]:
    """Get a specific design output"""
    return db.query(DesignOutput).filter(
        DesignOutput.id == output_id,
        DesignOutput.project_id == project_id
    ).first()

def update_design_output(db: Session, output_id: str, design_output: DesignOutputUpdate, project_id: str) -> Optional[DesignOutput]:
    """Update a design output"""
    db_output = get_design_output(db, output_id, project_id)
    if not db_output:
        return None
    
    update_data = design_output.model_dump(exclude_unset=True) if hasattr(design_output, 'model_dump') else design_output.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_output, field, value)
    
    db.commit()
    db.refresh(db_output)
    return db_output

def delete_design_output(db: Session, output_id: str, project_id: str) -> bool:
    """Delete a design output"""
    db_output = get_design_output(db, output_id, project_id)
    if not db_output:
        return False
    
    db.delete(db_output)
    db.commit()
    return True

