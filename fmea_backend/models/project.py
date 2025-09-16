from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="draft")  # draft, final, exported
    
    # Version control fields
    version_number = Column(String(20), nullable=False, default="1.0")
    major_version = Column(Integer, nullable=False, default=1)
    minor_version = Column(Integer, nullable=False, default=0)
    patch_version = Column(Integer, nullable=False, default=0)
    version_status = Column(String(50), nullable=False, default="draft")  # draft, review, approved, published
    version_label = Column(String(100), nullable=True)  # "Draft", "Final", "Review", "Approved"
    change_summary = Column(Text, nullable=True)  # Summary of changes in this version
    change_details = Column(JSON, nullable=True)  # Detailed change log
    content_hash = Column(String(64), nullable=True)  # SHA-256 hash of project content
    approval_required = Column(String(10), default="false")  # true/false as string for SQLite compatibility
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    version_created_at = Column(DateTime(timezone=True), server_default=func.now())
    version_updated_at = Column(DateTime(timezone=True), onupdate=func.now())
