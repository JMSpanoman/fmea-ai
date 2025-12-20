from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import approval as approval_schemas
from crud import approval_phase3 as approval_crud
from typing import List

router = APIRouter(prefix="/approvals", tags=["Approvals Phase 3"])

@router.post("", response_model=approval_schemas.ApprovalOut, status_code=status.HTTP_201_CREATED)
def create_approval(
    approval: approval_schemas.ApprovalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new approval"""
    # Set approver to current user if not specified
    if hasattr(approval, 'model_copy'):
        approval = approval.model_copy(update={'approver_id': current_user.id})
    else:
        approval_dict = approval.dict() if hasattr(approval, 'dict') else approval.model_dump()
        approval_dict['approver_id'] = current_user.id
        approval = approval_schemas.ApprovalCreate(**approval_dict)
    
    return approval_crud.create_approval(db, approval)

@router.get("/{artifact_type}/{artifact_id}", response_model=List[approval_schemas.ApprovalOut])
def get_approvals(
    artifact_type: str,
    artifact_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all approvals for an artifact"""
    return approval_crud.get_approvals_by_artifact(db, artifact_type, artifact_id)

