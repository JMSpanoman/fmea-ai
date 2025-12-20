from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    auth0_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Phase 3 relationships
    training_records = relationship("TrainingRecord", back_populates="user", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="approver", cascade="all, delete-orphan")
