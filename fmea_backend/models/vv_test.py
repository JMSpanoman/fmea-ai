from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class VVTest(Base):
    __tablename__ = "vv_tests"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    design_output_id = Column(String, ForeignKey("design_outputs.id"), nullable=False, index=True)
    test_method = Column(Text, nullable=False)
    acceptance_criteria = Column(Text, nullable=False)
    rationale = Column(Text, nullable=True)
    ai_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="vv_tests")
    design_output = relationship("DesignOutput", back_populates="vv_tests")

