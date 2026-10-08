"""
Finding model - represents a detected dark pattern
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Finding(Base):
    """
    Represents a detected dark pattern in an audit
    """
    __tablename__ = "findings"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    audit_id = Column(String(36), ForeignKey("audits.id"), nullable=False, index=True)
    
    # Finding metadata
    finding_number = Column(Integer, nullable=False)  # Sequential number within audit
    category = Column(String(100), nullable=False, index=True)  # subscription_trap, forced_action, etc.
    title = Column(String(255), nullable=False)
    
    # Severity and confidence
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    confidence = Column(Float, nullable=False)  # 0-100
    
    # Analysis details
    evidence_text = Column(Text, nullable=False)  # The actual text/UI element found
    why_problematic = Column(Text, nullable=False)  # Why it's a dark pattern
    user_impact = Column(Text, nullable=False)  # How it impacts users
    recommended_fix = Column(Text, nullable=False)  # How to fix it
    
    # Status
    status = Column(String(50), nullable=False, default="open")  # open, reviewed, resolved
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    audit = relationship("Audit", back_populates="findings")
    evidence_items = relationship("Evidence", back_populates="finding", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Finding id={self.id} category={self.category} severity={self.severity}>"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "audit_id": self.audit_id,
            "finding_number": self.finding_number,
            "category": self.category,
            "title": self.title,
            "severity": self.severity,
            "confidence": self.confidence,
            "evidence_text": self.evidence_text,
            "why_problematic": self.why_problematic,
            "user_impact": self.user_impact,
            "recommended_fix": self.recommended_fix,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
