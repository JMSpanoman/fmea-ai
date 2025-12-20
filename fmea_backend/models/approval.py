from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Approval(Base):
    __tablename__ = "approvals"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    artifact_type = Column(String, nullable=False)  # document, change_control, ncr, capa, audit, complaint
    artifact_id = Column(String, nullable=False, index=True)
    approver_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String, nullable=False)  # pending, approved, rejected
    comment = Column(Text, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    approver = relationship("User", back_populates="approvals")

