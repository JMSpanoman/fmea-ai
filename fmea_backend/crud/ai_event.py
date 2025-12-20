from sqlalchemy.orm import Session
from models.ai_event import AIEvent
from schemas.ai_event import AIEventCreate, AIEventUpdate
from typing import List, Optional
import uuid
from datetime import datetime

def create_ai_event(db: Session, ai_event: AIEventCreate, user_id: str) -> AIEvent:
    """Create a new AI event log"""
    db_event = AIEvent(
        id=str(uuid.uuid4()),
        project_id=ai_event.project_id,
        user_id=user_id,
        context_type=ai_event.context_type,
        context_id=ai_event.context_id,
        prompt_name=ai_event.prompt_name,
        input_summary=ai_event.input_summary,
        output_json=ai_event.output_json,
        disposition="pending"
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_ai_event(db: Session, event_id: str) -> Optional[AIEvent]:
    """Get a specific AI event"""
    return db.query(AIEvent).filter(AIEvent.id == event_id).first()

def get_ai_events_by_context(
    db: Session,
    project_id: str,
    context_type: str,
    context_id: Optional[str] = None
) -> List[AIEvent]:
    """Get AI events for a specific context"""
    query = db.query(AIEvent).filter(
        AIEvent.project_id == project_id,
        AIEvent.context_type == context_type
    )
    
    if context_id:
        query = query.filter(AIEvent.context_id == context_id)
    
    return query.order_by(AIEvent.created_at.desc()).all()

def update_ai_event_disposition(
    db: Session,
    event_id: str,
    update_data: AIEventUpdate,
    user_id: str
) -> Optional[AIEvent]:
    """Update AI event disposition"""
    db_event = get_ai_event(db, event_id)
    if not db_event:
        return None
    
    if hasattr(update_data, 'model_dump'):
        update_dict = update_data.model_dump(exclude_unset=True)
    else:
        update_dict = update_data.dict(exclude_unset=True)
    
    for field, value in update_dict.items():
        setattr(db_event, field, value)
    
    # Set disposition metadata
    if 'disposition' in update_dict and update_dict['disposition']:
        db_event.disposition_user_id = user_id
        db_event.disposed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_event)
    return db_event

