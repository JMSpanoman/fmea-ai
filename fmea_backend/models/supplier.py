from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    risk_rating = Column(Integer, nullable=True)
    status = Column(String, nullable=True)
    ai_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="suppliers")
    evaluations = relationship("SupplierEvaluation", back_populates="supplier", cascade="all, delete-orphan")

class SupplierEvaluation(Base):
    __tablename__ = "supplier_evaluations"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    supplier_id = Column(String, ForeignKey("suppliers.id"), nullable=False, index=True)
    evaluation_text = Column(Text, nullable=True)
    score = Column(Integer, nullable=True)
    ai_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    supplier = relationship("Supplier", back_populates="evaluations")

