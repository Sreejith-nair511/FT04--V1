"""
Evidence model - represents visual or textual evidence of a dark pattern
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Evidence(Base):
    """
    Represents visual or textual evidence associated with a finding or audit
    """
    __tablename__ = "evidence"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys
    finding_id = Column(String(36), ForeignKey("findings.id"), nullable=True, index=True)
    audit_id = Column(String(36), ForeignKey("audits.id"), nullable=False, index=True)
    
    # Evidence metadata
    evidence_type = Column(String(50), nullable=False)  # box, text, interactive
    frame_number = Column(Integer, nullable=True)  # For video evidence
    timestamp_seconds = Column(Float, nullable=True)  # For video evidence
    
    # Bounding box coordinates (normalized 0.0 - 1.0)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    
    # File path to evidence image or frame
    image_path = Column(String(500), nullable=True)
    
    # Optional text content
    text = Column(Text, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    finding = relationship("Finding", back_populates="evidence_items")
    audit = relationship("Audit", back_populates="evidence_items")
    
    def __repr__(self) -> str:
        return f"<Evidence id={self.id} type={self.evidence_type} finding={self.finding_id}>"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "finding_id": self.finding_id,
            "audit_id": self.audit_id,
            "evidence_type": self.evidence_type,
            "frame_number": self.frame_number,
            "timestamp_seconds": self.timestamp_seconds,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "image_path": self.image_path,
            "text": self.text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
