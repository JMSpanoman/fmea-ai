from sqlalchemy.orm import Session
from models.complaint import Complaint
from schemas.complaint import ComplaintCreate, ComplaintUpdate
from typing import List, Optional
import uuid

def create_complaint(db: Session, complaint: ComplaintCreate) -> Complaint:
    """Create a new complaint"""
    db_complaint = Complaint(
        id=str(uuid.uuid4()),
        project_id=complaint.project_id,
        description=complaint.description,
        reportability=complaint.reportability,
        investigation=complaint.investigation,
        linked_risk_ids=complaint.linked_risk_ids or [],
        ai_metadata=complaint.ai_metadata
    )
    db.add(db_complaint)
    db.commit()
    db.refresh(db_complaint)
    return db_complaint

def get_complaints_by_project(db: Session, project_id: str) -> List[Complaint]:
    """Get all complaints for a project"""
    return db.query(Complaint).filter(Complaint.project_id == project_id).all()

def get_complaint(db: Session, complaint_id: str, project_id: str) -> Optional[Complaint]:
    """Get a specific complaint"""
    return db.query(Complaint).filter(
        Complaint.id == complaint_id,
        Complaint.project_id == project_id
    ).first()

def update_complaint(db: Session, complaint_id: str, complaint: ComplaintUpdate, project_id: str) -> Optional[Complaint]:
    """Update a complaint"""
    db_complaint = get_complaint(db, complaint_id, project_id)
    if not db_complaint:
        return None
    
    update_data = complaint.model_dump(exclude_unset=True) if hasattr(complaint, 'model_dump') else complaint.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_complaint, field, value)
    
    db.commit()
    db.refresh(db_complaint)
    return db_complaint

