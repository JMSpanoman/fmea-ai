from sqlalchemy.orm import Session
from models.design_input import DesignInput
from models.design_output import DesignOutput
from schemas.design_control import DesignInputCreate, DesignInputUpdate, DesignOutputCreate, DesignOutputUpdate
from typing import List, Optional
import uuid

# Design Input CRUD
def create_design_input(db: Session, design_input: DesignInputCreate) -> DesignInput:
    """Create a new design input"""
    db_input = DesignInput(
        id=str(uuid.uuid4()),
        project_id=design_input.project_id,
        source=design_input.source,
        text=design_input.text,
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
def create_design_output(db: Session, design_output: DesignOutputCreate) -> DesignOutput:
    """Create a new design output"""
    db_output = DesignOutput(
        id=str(uuid.uuid4()),
        project_id=design_output.project_id,
        source=design_output.source,
        text=design_output.text,
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

