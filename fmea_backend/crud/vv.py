from sqlalchemy.orm import Session
from models.vv_test import VVTest
from schemas.vv import VVTestCreate, VVTestUpdate
from typing import List, Optional
import uuid

def create_vv_test(db: Session, vv_test: VVTestCreate) -> VVTest:
    """Create a new V&V test"""
    db_test = VVTest(
        id=str(uuid.uuid4()),
        project_id=vv_test.project_id,
        design_output_id=vv_test.design_output_id,
        test_method=vv_test.test_method,
        acceptance_criteria=vv_test.acceptance_criteria,
        rationale=vv_test.rationale,
        ai_metadata=vv_test.ai_metadata
    )
    db.add(db_test)
    db.commit()
    db.refresh(db_test)
    return db_test

def get_vv_tests_by_project(db: Session, project_id: str) -> List[VVTest]:
    """Get all V&V tests for a project"""
    return db.query(VVTest).filter(VVTest.project_id == project_id).all()

def get_vv_test(db: Session, test_id: str, project_id: str) -> Optional[VVTest]:
    """Get a specific V&V test"""
    return db.query(VVTest).filter(
        VVTest.id == test_id,
        VVTest.project_id == project_id
    ).first()

def get_vv_tests_by_design_output(db: Session, design_output_id: str, project_id: str) -> List[VVTest]:
    """Get all V&V tests for a design output"""
    return db.query(VVTest).filter(
        VVTest.design_output_id == design_output_id,
        VVTest.project_id == project_id
    ).all()

def update_vv_test(db: Session, test_id: str, vv_test: VVTestUpdate, project_id: str) -> Optional[VVTest]:
    """Update a V&V test"""
    db_test = get_vv_test(db, test_id, project_id)
    if not db_test:
        return None
    
    update_data = vv_test.model_dump(exclude_unset=True) if hasattr(vv_test, 'model_dump') else vv_test.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_test, field, value)
    
    db.commit()
    db.refresh(db_test)
    return db_test

def delete_vv_test(db: Session, test_id: str, project_id: str) -> bool:
    """Delete a V&V test"""
    db_test = get_vv_test(db, test_id, project_id)
    if not db_test:
        return False
    
    db.delete(db_test)
    db.commit()
    return True

