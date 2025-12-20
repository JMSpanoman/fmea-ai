from sqlalchemy.orm import Session
from models.idempotency_request import IdempotencyRequest
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

def get_idempotent_response(
    db: Session,
    idempotency_key: str,
    user_id: str,
    endpoint: str
) -> Optional[Dict[str, Any]]:
    """Check if a request with this idempotency key was already processed"""
    existing = db.query(IdempotencyRequest).filter(
        IdempotencyRequest.idempotency_key == idempotency_key,
        IdempotencyRequest.user_id == user_id,
        IdempotencyRequest.endpoint == endpoint
    ).first()
    
    if existing:
        # Check expiration (if set)
        if existing.expires_at and existing.expires_at < datetime.utcnow():
            # Expired, delete it
            db.delete(existing)
            db.commit()
            return None
        
        return existing.response_json
    
    return None

def store_idempotent_response(
    db: Session,
    idempotency_key: str,
    user_id: str,
    project_id: str,
    endpoint: str,
    response_json: Dict[str, Any],
    request_hash: Optional[str] = None,
    ttl_hours: int = 24
) -> IdempotencyRequest:
    """Store the response for an idempotent request"""
    expires_at = datetime.utcnow() + timedelta(hours=ttl_hours)
    
    db_request = IdempotencyRequest(
        id=str(uuid.uuid4()),
        idempotency_key=idempotency_key,
        user_id=user_id,
        project_id=project_id,
        endpoint=endpoint,
        request_hash=request_hash,
        response_json=response_json,
        expires_at=expires_at
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request

