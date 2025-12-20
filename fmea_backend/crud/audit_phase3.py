from sqlalchemy.orm import Session
from models.audit import Audit
from schemas.audit import AuditCreate, AuditUpdate
from typing import List, Optional, Dict, Any
import uuid

def create_audit(db: Session, audit: AuditCreate) -> Audit:
    """Create a new audit"""
    db_audit = Audit(
        id=str(uuid.uuid4()),
        project_id=audit.project_id,
        type=audit.type,
        scope=audit.scope,
        status=audit.status,
        scheduled_date=audit.scheduled_date,
        ai_metadata=audit.ai_metadata
    )
    db.add(db_audit)
    db.commit()
    db.refresh(db_audit)
    return db_audit

def get_audits_by_project(db: Session, project_id: str) -> List[Audit]:
    """Get all audits for a project"""
    return db.query(Audit).filter(Audit.project_id == project_id).all()

def get_audit(db: Session, audit_id: str, project_id: str) -> Optional[Audit]:
    """Get a specific audit"""
    return db.query(Audit).filter(
        Audit.id == audit_id,
        Audit.project_id == project_id
    ).first()

def update_audit(db: Session, audit_id: str, audit: AuditUpdate, project_id: str) -> Optional[Audit]:
    """Update an audit"""
    db_audit = get_audit(db, audit_id, project_id)
    if not db_audit:
        return None
    
    update_data = audit.model_dump(exclude_unset=True) if hasattr(audit, 'model_dump') else audit.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_audit, field, value)
    
    db.commit()
    db.refresh(db_audit)
    return db_audit

def add_audit_finding(db: Session, audit_id: str, project_id: str, finding: Dict[str, Any]) -> Optional[Audit]:
    """Add a finding to an audit"""
    db_audit = get_audit(db, audit_id, project_id)
    if not db_audit:
        return None
    
    if db_audit.findings is None:
        db_audit.findings = {"findings": []}
    
    if "findings" not in db_audit.findings:
        db_audit.findings["findings"] = []
    
    db_audit.findings["findings"].append(finding)
    db.commit()
    db.refresh(db_audit)
    return db_audit

def close_audit(db: Session, audit_id: str, project_id: str) -> Optional[Audit]:
    """Close an audit"""
    db_audit = get_audit(db, audit_id, project_id)
    if not db_audit:
        return None
    
    db_audit.status = "closed"
    db.commit()
    db.refresh(db_audit)
    return db_audit

