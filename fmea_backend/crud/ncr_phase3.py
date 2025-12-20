from sqlalchemy.orm import Session
from models.ncr import NCR
from schemas.ncr import NCRCreate, NCRUpdate
from typing import List, Optional
import uuid

def create_ncr(db: Session, ncr: NCRCreate) -> NCR:
    """Create a new NCR"""
    db_ncr = NCR(
        id=str(uuid.uuid4()),
        project_id=ncr.project_id,
        description=ncr.description,
        root_cause=ncr.root_cause,
        containment_action=ncr.containment_action,
        corrective_action=ncr.corrective_action,
        status=ncr.status,
        linked_risk_ids=ncr.linked_risk_ids or [],
        ai_metadata=ncr.ai_metadata
    )
    db.add(db_ncr)
    db.commit()
    db.refresh(db_ncr)
    return db_ncr

def get_ncrs_by_project(db: Session, project_id: str) -> List[NCR]:
    """Get all NCRs for a project"""
    return db.query(NCR).filter(NCR.project_id == project_id).all()

def get_ncr(db: Session, ncr_id: str, project_id: str) -> Optional[NCR]:
    """Get a specific NCR"""
    return db.query(NCR).filter(
        NCR.id == ncr_id,
        NCR.project_id == project_id
    ).first()

def update_ncr(db: Session, ncr_id: str, ncr: NCRUpdate, project_id: str) -> Optional[NCR]:
    """Update an NCR"""
    db_ncr = get_ncr(db, ncr_id, project_id)
    if not db_ncr:
        return None
    
    update_data = ncr.model_dump(exclude_unset=True) if hasattr(ncr, 'model_dump') else ncr.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ncr, field, value)
    
    db.commit()
    db.refresh(db_ncr)
    return db_ncr

def close_ncr(db: Session, ncr_id: str, project_id: str) -> Optional[NCR]:
    """Close an NCR"""
    db_ncr = get_ncr(db, ncr_id, project_id)
    if not db_ncr:
        return None
    
    db_ncr.status = "closed"
    db.commit()
    db.refresh(db_ncr)
    return db_ncr

