from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, JSON
from sqlalchemy.sql import func
from database import Base

class FMEA(Base):
    __tablename__ = "fmea_entries"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False, index=True)
    user_id = Column(String, nullable=False, index=True)
    component = Column(String(255), nullable=False)
    function_description = Column(Text, nullable=True)
    potential_failure_mode = Column(Text, nullable=True)
    potential_effects = Column(Text, nullable=True)
    severity = Column(Integer, nullable=True)
    potential_causes = Column(Text, nullable=True)
    occurrence = Column(Integer, nullable=True)
    current_controls = Column(Text, nullable=True)
    detection = Column(Integer, nullable=True)
    risk_priority_number = Column(Integer, nullable=True)
    recommended_actions = Column(Text, nullable=True)
    responsible_party = Column(String(255), nullable=True)
    target_completion_date = Column(Date, nullable=True)
    actions_taken = Column(Text, nullable=True)
    final_severity = Column(Integer, nullable=True)
    final_occurrence = Column(Integer, nullable=True)
    final_detection = Column(Integer, nullable=True)
    final_risk_priority_number = Column(Integer, nullable=True)
    
    # Version control fields
    version_number = Column(String(20), nullable=False, default="1.0")
    major_version = Column(Integer, nullable=False, default=1)
    minor_version = Column(Integer, nullable=False, default=0)
    patch_version = Column(Integer, nullable=False, default=0)
    version_status = Column(String(50), nullable=False, default="draft")  # draft, review, approved, published
    version_label = Column(String(100), nullable=True)  # "Draft", "Final", "Review", "Approved"
    change_summary = Column(Text, nullable=True)  # Summary of changes in this version
    change_details = Column(JSON, nullable=True)  # Detailed change log
    content_hash = Column(String(64), nullable=True)  # SHA-256 hash of FMEA content
    approval_required = Column(String(10), default="false")  # true/false as string for SQLite compatibility
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    version_created_at = Column(DateTime(timezone=True), server_default=func.now())
    version_updated_at = Column(DateTime(timezone=True), onupdate=func.now()) 