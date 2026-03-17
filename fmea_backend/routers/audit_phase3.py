from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from auth.plan import require_pro
from models.user import User
from schemas import audit as audit_schemas
from crud import audit_phase3 as audit_crud
from crud import project as project_crud
from typing import List, Dict, Any
from datetime import datetime, timezone

router = APIRouter(prefix="/projects/{project_id}", tags=["Audit Phase 3"], dependencies=[Depends(require_pro)])

@router.get("/audits", response_model=List[audit_schemas.AuditOut])
def get_audits(
    project_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all audits for a project"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return audit_crud.get_audits_by_project(db, project_id)

@router.post("/audits", response_model=audit_schemas.AuditOut, status_code=status.HTTP_201_CREATED)
def create_audit(
    project_id: str,
    audit: audit_schemas.AuditCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new audit"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Ensure project_id matches
    if hasattr(audit, 'model_copy'):
        audit = audit.model_copy(update={'project_id': project_id})
    else:
        audit_dict = audit.dict() if hasattr(audit, 'dict') else audit.model_dump()
        audit_dict['project_id'] = project_id
        audit = audit_schemas.AuditCreate(**audit_dict)
    
    return audit_crud.create_audit(db, audit)

@router.post("/audits/{audit_id}/finding", response_model=audit_schemas.AuditOut)
def add_audit_finding(
    project_id: str,
    audit_id: str,
    finding: audit_schemas.AuditFindingRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add a finding to an audit"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    finding_data = {
        "finding": finding.finding,
        "severity": finding.severity,
        "category": finding.category,
        "added_by": current_user.id,
        "added_at": str(datetime.now(timezone.utc))
    }
    
    updated = audit_crud.add_audit_finding(db, audit_id, project_id, finding_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return updated

@router.post("/audits/{audit_id}/close", response_model=audit_schemas.AuditOut)
def close_audit(
    project_id: str,
    audit_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Close an audit"""
    project = project_crud.get_project(db, project_id, current_user.id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    closed = audit_crud.close_audit(db, audit_id, project_id)
    if not closed:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return closed

