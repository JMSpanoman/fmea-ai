from sqlalchemy.orm import Session
from models.nonconformance import NonConformance
from schemas.nonconformance import NonConformanceCreate, NonConformanceUpdate
from typing import List, Optional

def create_nonconformance(db: Session, project_id: int, nonconformance_data: NonConformanceCreate, user_id: str) -> NonConformance:
    """Create a new Non-Conformance entry"""
    db_nonconformance = NonConformance(
        project_id=project_id,
        user_id=user_id,
        issue_description=nonconformance_data.issue_description,
        source=nonconformance_data.source,
        detection_date=nonconformance_data.detection_date,
        severity=nonconformance_data.severity,
        root_cause=nonconformance_data.root_cause,
        corrective_action=nonconformance_data.corrective_action,
        preventive_action=nonconformance_data.preventive_action,
        action_owner=nonconformance_data.action_owner,
        due_date=nonconformance_data.due_date,
        status=nonconformance_data.status,
        investigation_details=nonconformance_data.investigation_details,
        regulatory_impact=nonconformance_data.regulatory_impact,
        closure_summary=nonconformance_data.closure_summary,
        analysis_timestamp=nonconformance_data.analysis_timestamp,
        version=nonconformance_data.version
    )
    db.add(db_nonconformance)
    db.commit()
    db.refresh(db_nonconformance)
    return db_nonconformance

def get_nonconformances_for_project(db: Session, project_id: int, user_id: str) -> List[NonConformance]:
    """Get all Non-Conformance entries for a project"""
    return db.query(NonConformance).filter(NonConformance.project_id == project_id, NonConformance.user_id == user_id).all()

def get_nonconformance(db: Session, nonconformance_id: int, user_id: str) -> Optional[NonConformance]:
    """Get a specific Non-Conformance entry"""
    return db.query(NonConformance).filter(NonConformance.id == nonconformance_id, NonConformance.user_id == user_id).first()

def update_nonconformance(db: Session, nonconformance_id: int, nonconformance_data: NonConformanceUpdate, user_id: str) -> Optional[NonConformance]:
    """Update a Non-Conformance entry"""
    db_nonconformance = db.query(NonConformance).filter(NonConformance.id == nonconformance_id, NonConformance.user_id == user_id).first()
    if db_nonconformance:
        for field, value in nonconformance_data.dict(exclude_unset=True).items():
            setattr(db_nonconformance, field, value)
        db.commit()
        db.refresh(db_nonconformance)
    return db_nonconformance

def delete_nonconformance(db: Session, nonconformance_id: int, user_id: str) -> bool:
    """Delete a Non-Conformance entry"""
    db_nonconformance = db.query(NonConformance).filter(NonConformance.id == nonconformance_id, NonConformance.user_id == user_id).first()
    if db_nonconformance:
        db.delete(db_nonconformance)
        db.commit()
        return True
    return False 