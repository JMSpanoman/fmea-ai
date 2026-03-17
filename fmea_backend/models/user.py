from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

# SaaS plan tiers: "lite" | "pro"
# Extensible for future: "starter", "enterprise", etc.
PLAN_LITE = "lite"
PLAN_PRO = "pro"
PLAN_CHOICES = (PLAN_LITE, PLAN_PRO)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    auth0_id = Column(String, unique=True, index=True, nullable=True)
    email = Column(String, nullable=False, index=True)
    plan = Column(String, nullable=False, default=PLAN_LITE, index=True)  # "lite" | "pro"
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Phase 3 relationships
    training_records = relationship("TrainingRecord", back_populates="user", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="approver", cascade="all, delete-orphan")
