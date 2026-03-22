"""Objective evidence records attached to a CAPA (audit trail)."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid


class CAPAEvidence(Base):
    __tablename__ = "capa_evidences"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    capa_id = Column(String, ForeignKey("capas.id", ondelete="CASCADE"), nullable=False, index=True)
    category = Column(String, nullable=False)  # rca | containment | effectiveness | general
    title = Column(String, nullable=False)
    reference_uri = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    capa = relationship("CAPA", back_populates="evidences")
