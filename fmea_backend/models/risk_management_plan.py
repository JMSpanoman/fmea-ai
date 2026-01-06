from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class RiskManagementPlan(Base):
    __tablename__ = "risk_management_plans"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    title = Column(Text, nullable=False)
    scope = Column(Text, nullable=False)
    intended_use = Column(Text, nullable=False)
    components_json = Column(Text, nullable=False)  # JSON string of components list
    acceptability_criteria_json = Column(Text, nullable=False)  # JSON string of criteria
    risk_methodology = Column(Text, nullable=False)
    review_roles_json = Column(Text, nullable=False)  # JSON string of roles
    risk_control_categories_json = Column(Text, nullable=False)  # JSON string of categories
    benefit_risk_criteria = Column(Text, nullable=False)
    lifecycle_linkage = Column(Text, nullable=False)
    governance_rules = Column(Text, nullable=False)
    rendered_html = Column(Text, nullable=False)
    status = Column(String, nullable=False, default='draft')  # draft, approved, superseded
    current_version_no = Column(Integer, nullable=False, default=1)
    created_by = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="risk_management_plans")

    # Indexes
    __table_args__ = (
        Index('idx_rmp_project_id', 'project_id'),
        Index('idx_rmp_project_status', 'project_id', 'status'),
        Index('idx_rmp_project_created', 'project_id', 'created_at'),
    )

