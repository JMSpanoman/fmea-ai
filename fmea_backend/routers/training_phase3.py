from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from schemas import training as training_schemas
from crud import training as training_crud
from typing import List

router = APIRouter(prefix="/users/{user_id}", tags=["Training"])

@router.get("/training", response_model=List[training_schemas.TrainingRecordOut])
def get_user_training(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all training records for a user"""
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return training_crud.get_training_records_by_user(db, user_id)

@router.post("/training/assign", response_model=training_schemas.TrainingRecordOut, status_code=status.HTTP_201_CREATED)
def assign_training(
    user_id: str,
    request: training_schemas.TrainingAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Assign training to a user"""
    if user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return training_crud.assign_training(db, request.user_id, request.document_id)

@router.post("/training/complete", response_model=training_schemas.TrainingRecordOut)
def complete_training(
    user_id: str,
    request: training_schemas.TrainingCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark training as complete"""
    if user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    training_record = training_crud.complete_training(db, request.training_record_id)
    if not training_record:
        raise HTTPException(status_code=404, detail="Training record not found")
    
    return training_record

