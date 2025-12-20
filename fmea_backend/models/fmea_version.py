from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import uuid

class FMEAVersion(Base):
    __tablename__ = "fmea_versions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    fmea_row_id = Column(String, ForeignKey("fmea_rows.id"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    diff = Column(JSON, nullable=True)  # Stores the diff between versions
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    fmea_row = relationship("FMEARow", back_populates="versions")

