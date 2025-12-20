from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class TraceLink(Base):
    __tablename__ = "trace_links"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    from_type = Column(String, nullable=False)  # Canonical: risk_item, risk_item_version, risk_control, design_input, etc.
    from_id = Column(String, nullable=False, index=True)
    to_type = Column(String, nullable=False)  # Canonical: design_input, design_output, vv_test, capa, etc.
    to_id = Column(String, nullable=False, index=True)
    link_type = Column(String, nullable=True, default="traces_to")  # traces_to, verified_by, generated_from, impacts, mitigates
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="trace_links")

