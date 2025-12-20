from sqlalchemy.orm import Session
from models.training_record import TrainingRecord
from schemas.training import TrainingRecordCreate, TrainingRecordUpdate
from typing import List, Optional
import uuid
from datetime import datetime, timezone

def create_training_record(db: Session, training_record: TrainingRecordCreate) -> TrainingRecord:
    """Create a new training record"""
    db_record = TrainingRecord(
        id=str(uuid.uuid4()),
        user_id=training_record.user_id,
        document_id=training_record.document_id,
        status=training_record.status
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def get_training_records_by_user(db: Session, user_id: str) -> List[TrainingRecord]:
    """Get all training records for a user"""
    return db.query(TrainingRecord).filter(TrainingRecord.user_id == user_id).all()

def get_training_record(db: Session, record_id: str) -> Optional[TrainingRecord]:
    """Get a specific training record"""
    return db.query(TrainingRecord).filter(TrainingRecord.id == record_id).first()

def update_training_record(db: Session, record_id: str, training_record: TrainingRecordUpdate) -> Optional[TrainingRecord]:
    """Update a training record"""
    db_record = get_training_record(db, record_id)
    if not db_record:
        return None
    
    update_data = training_record.model_dump(exclude_unset=True) if hasattr(training_record, 'model_dump') else training_record.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    # If status is complete, set completed_at
    if update_data.get('status') == 'complete' and not db_record.completed_at:
        db_record.completed_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(db_record)
    return db_record

def assign_training(db: Session, user_id: str, document_id: str) -> TrainingRecord:
    """Assign training to a user"""
    training_record = TrainingRecordCreate(
        user_id=user_id,
        document_id=document_id,
        status="assigned"
    )
    return create_training_record(db, training_record)

def complete_training(db: Session, record_id: str) -> Optional[TrainingRecord]:
    """Mark training as complete"""
    update = TrainingRecordUpdate(
        status="complete",
        completed_at=datetime.now(timezone.utc)
    )
    return update_training_record(db, record_id, update)

