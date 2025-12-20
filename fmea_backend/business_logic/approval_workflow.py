"""
Business Logic for Approval Workflow
Handles approval status transitions and automatic actions
"""
from sqlalchemy.orm import Session
from typing import Optional
from crud import approval_phase3 as approval_crud
from crud import document as doc_crud
from crud import training as training_crud
from crud import change_control_phase3 as cc_crud
from models.user import User

def approve_document_with_workflow(db: Session, document_id: str, project_id: str, approver: User) -> Optional[dict]:
    """
    Approve a document with full workflow:
    1. Create approval record
    2. Update document status to approved
    3. Auto-assign training to relevant users
    """
    # Create approval
    from schemas.approval import ApprovalCreate
    approval = ApprovalCreate(
        artifact_type="document",
        artifact_id=document_id,
        approver_id=approver.id,
        status="approved"
    )
    approval_crud.create_approval(db, approval)
    
    # Update document status
    document = doc_crud.approve_document(db, document_id, project_id)
    if not document:
        return None
    
    # Auto-assign training to project team
    # In production, get from project team members
    # For now, assign to approver
    training_crud.assign_training(db, approver.id, document_id)
    
    return {
        "document": document,
        "approval": approval,
        "training_assigned": True
    }

def validate_change_control_status_transition(current_status: str, new_status: str) -> bool:
    """
    Validate change control status transitions
    Flow: open -> in_review -> approved -> implemented -> verified -> closed
    """
    valid_transitions = {
        "open": ["in_review"],
        "in_review": ["approved", "open"],  # Can go back to open if rejected
        "approved": ["implemented"],
        "implemented": ["verified"],
        "verified": ["closed"],
        "closed": []  # Terminal state
    }
    
    return new_status in valid_transitions.get(current_status, [])

def process_change_control_approval(db: Session, change_id: str, project_id: str, approver: User) -> Optional[dict]:
    """
    Approve a change control with workflow
    """
    from schemas.approval import ApprovalCreate
    from schemas.change_control import ChangeControlUpdate
    
    # Create approval
    approval = ApprovalCreate(
        artifact_type="change_control",
        artifact_id=change_id,
        approver_id=approver.id,
        status="approved"
    )
    approval_crud.create_approval(db, approval)
    
    # Update status
    update = ChangeControlUpdate(status="approved")
    change_control = cc_crud.update_change_control(db, change_id, update, project_id)
    
    return {
        "change_control": change_control,
        "approval": approval
    }

