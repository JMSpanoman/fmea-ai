from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class Component(Base):
    __tablename__ = "components"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    parent_id = Column(String, ForeignKey("components.id"), nullable=True, index=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="components")
    parent = relationship("Component", remote_side=[id], back_populates="children", uselist=False)
    children = relationship("Component", back_populates="parent")
    fmea_rows = relationship("FMEARow", back_populates="component", cascade="all, delete-orphan")

