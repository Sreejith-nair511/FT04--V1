"""
Audit model - represents an audit of a fintech application
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database import Base


class Audit(Base):
    """
    Represents a single audit of a fintech application
    """
    __tablename__ = "audits"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Audit metadata
    application_name = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False)  # iOS, Android, Web
    input_type = Column(String(50), nullable=False)  # image, video
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    
    # Analysis status
    status = Column(String(50), nullable=False, default="queued")  # queued, processing, completed, failed
    
    # Risk scoring
    risk_score = Column(Float, nullable=True)  # 0-100
    risk_level = Column(String(20), nullable=True)  # LOW, MEDIUM, HIGH, CRITICAL
    
    # Summary and metadata
    summary = Column(String(1000), nullable=True)
    model_name = Column(String(100), nullable=True, default="gemini-2.0-flash-exp")
    model_version = Column(String(50), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationships
    findings = relationship("Finding", back_populates="audit", cascade="all, delete-orphan")
    evidence_items = relationship("Evidence", back_populates="audit", cascade="all, delete-orphan")
    analysis_job = relationship("AnalysisJob", back_populates="audit", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Audit id={self.id} app={self.application_name} status={self.status}>"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "application_name": self.application_name,
            "platform": self.platform,
            "input_type": self.input_type,
            "status": self.status,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "summary": self.summary,
            "model_name": self.model_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }
