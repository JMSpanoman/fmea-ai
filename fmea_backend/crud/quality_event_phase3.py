from sqlalchemy.orm import Session
from models.quality_event import QualityEvent
from schemas.quality_event import QualityEventCreate, QualityEventUpdate
from typing import List, Optional
import uuid

def create_quality_event(db: Session, event: QualityEventCreate) -> QualityEvent:
    """Create a new quality event"""
    db_event = QualityEvent(
        id=str(uuid.uuid4()),
        project_id=event.project_id,
        event_type=event.event_type,
        description=event.description,
        status=event.status,
        linked_risk_ids=event.linked_risk_ids or [],
        ai_metadata=event.ai_metadata
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_quality_events_by_project(db: Session, project_id: str) -> List[QualityEvent]:
    """Get all quality events for a project"""
    return db.query(QualityEvent).filter(QualityEvent.project_id == project_id).all()

def get_quality_event(db: Session, event_id: str, project_id: str) -> Optional[QualityEvent]:
    """Get a specific quality event"""
    return db.query(QualityEvent).filter(
        QualityEvent.id == event_id,
        QualityEvent.project_id == project_id
    ).first()

def update_quality_event(db: Session, event_id: str, event: QualityEventUpdate, project_id: str) -> Optional[QualityEvent]:
    """Update a quality event"""
    db_event = get_quality_event(db, event_id, project_id)
    if not db_event:
        return None
    
    update_data = event.model_dump(exclude_unset=True) if hasattr(event, 'model_dump') else event.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_event, field, value)
    
    db.commit()
    db.refresh(db_event)
    return db_event

def link_risks_to_event(db: Session, event_id: str, project_id: str, risk_ids: List[str]) -> Optional[QualityEvent]:
    """Link risks to a quality event"""
    db_event = get_quality_event(db, event_id, project_id)
    if not db_event:
        return None
    
    existing_risks = db_event.linked_risk_ids or []
    # Merge and deduplicate
    all_risks = list(set(existing_risks + risk_ids))
    db_event.linked_risk_ids = all_risks
    
    db.commit()
    db.refresh(db_event)
    return db_event

