"""Generated documents: device-scoped documents with versioned content (JSON and markdown)."""
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class GeneratedDocument(Base):
    """
    Generated document tied to a device (e.g. risk report, FMEA export).
    Stores both structured content (content_json) and markdown (content_markdown) with versioning.
    """
    __tablename__ = "generated_documents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    device_id = Column(String, ForeignKey("devices.id"), nullable=False, index=True)
    document_type = Column(String(128), nullable=True, index=True)
    title = Column(String(512), nullable=True)
    content_json = Column(Text, nullable=True)
    content_markdown = Column(Text, nullable=True)
    version = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    device = relationship("Device", back_populates="generated_documents", foreign_keys=[device_id])
