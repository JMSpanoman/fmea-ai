from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class GeneratedArtifact(Base):
    """
    Tracks generated/exported artifacts that are stored on the filesystem (temp/, templates/, etc.)
    so we can authorize downloads/deletes across restarts.
    """
    __tablename__ = "generated_artifacts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True, index=True)

    filename = Column(String, nullable=False, index=True)
    artifact_type = Column(String, nullable=False, index=True)  # e.g. "word_report", "template"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)

    # Relationships
    user = relationship("User")
    project = relationship("Project")

