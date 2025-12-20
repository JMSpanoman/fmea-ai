from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Index, UniqueConstraint
from sqlalchemy.sql import func
from database import Base
import uuid

class IdempotencyRequest(Base):
    """Track idempotency keys to prevent duplicate requests"""
    __tablename__ = "idempotency_requests"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    idempotency_key = Column(String, nullable=False, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    
    # Request fingerprint
    endpoint = Column(String, nullable=False)  # e.g., "/risk-items/{id}/handoff/design"
    request_hash = Column(String, nullable=True)  # Hash of request body for additional validation
    
    # Response data
    response_json = Column(JSON, nullable=True)  # Store created artifact/link IDs
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True)  # Optional expiration
    
    # Unique constraint: same key + user + endpoint = same result
    __table_args__ = (
        UniqueConstraint('idempotency_key', 'user_id', 'endpoint', name='uq_idempotency_key_user_endpoint'),
        Index('idx_idempotency_lookup', 'idempotency_key', 'user_id', 'endpoint'),
    )

