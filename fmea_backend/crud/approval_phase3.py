from sqlalchemy.orm import Session
from models.approval import Approval
from schemas.approval import ApprovalCreate, ApprovalUpdate
from typing import List, Optional
import uuid

def create_approval(db: Session, approval: ApprovalCreate) -> Approval:
    """Create a new approval"""
    db_approval = Approval(
        id=str(uuid.uuid4()),
        project_id=getattr(approval, 'project_id', None),  # SmartQS Risk schema
        artifact_type=approval.artifact_type,
        artifact_id=approval.artifact_id,
        approver_id=approval.approver_id,
        status=approval.status,
        comment=approval.comment
    )
    db.add(db_approval)
    db.commit()
    db.refresh(db_approval)
    return db_approval

def get_approvals_by_artifact(db: Session, artifact_type: str, artifact_id: str) -> List[Approval]:
    """Get all approvals for an artifact"""
    return db.query(Approval).filter(
        Approval.artifact_type == artifact_type,
        Approval.artifact_id == artifact_id
    ).all()

def get_approval(db: Session, approval_id: str) -> Optional[Approval]:
    """Get a specific approval"""
    return db.query(Approval).filter(Approval.id == approval_id).first()

def update_approval(db: Session, approval_id: str, approval: ApprovalUpdate) -> Optional[Approval]:
    """Update an approval"""
    db_approval = get_approval(db, approval_id)
    if not db_approval:
        return None
    
    update_data = approval.model_dump(exclude_unset=True) if hasattr(approval, 'model_dump') else approval.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_approval, field, value)
    
    db.commit()
    db.refresh(db_approval)
    return db_approval

def check_artifact_approved(db: Session, artifact_type: str, artifact_id: str) -> bool:
    """Check if an artifact has been approved"""
    approvals = get_approvals_by_artifact(db, artifact_type, artifact_id)
    return any(approval.status == "approved" for approval in approvals)

