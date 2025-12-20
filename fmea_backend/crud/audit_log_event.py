from sqlalchemy.orm import Session
from models.audit_log_event import AuditLogEvent
from schemas.audit_log_event import AuditLogEventCreate
from typing import List, Optional
import uuid

def create_audit_log_event(
    db: Session,
    audit_event: AuditLogEventCreate
) -> AuditLogEvent:
    """Create an audit log event"""
    db_event = AuditLogEvent(
        id=str(uuid.uuid4()),
        project_id=audit_event.project_id,
        user_id=audit_event.user_id,
        event_type=audit_event.event_type,
        details_json=audit_event.details_json
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def get_audit_log_events_by_project(
    db: Session,
    project_id: str,
    event_type: Optional[str] = None,
    limit: int = 100
) -> List[AuditLogEvent]:
    """Get audit log events for a project, optionally filtered by type"""
    query = db.query(AuditLogEvent).filter(
        AuditLogEvent.project_id == project_id
    )
    
    if event_type:
        query = query.filter(AuditLogEvent.event_type == event_type)
    
    return query.order_by(AuditLogEvent.created_at.desc()).limit(limit).all()

def get_audit_log_events_by_context(
    db: Session,
    project_id: str,
    event_type_pattern: str,  # e.g., "handoff.%"
    limit: int = 50
) -> List[AuditLogEvent]:
    """Get audit log events matching a pattern (e.g., all handoffs)"""
    return db.query(AuditLogEvent).filter(
        AuditLogEvent.project_id == project_id,
        AuditLogEvent.event_type.like(event_type_pattern)
    ).order_by(AuditLogEvent.created_at.desc()).limit(limit).all()

