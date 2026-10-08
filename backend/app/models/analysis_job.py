"""
AnalysisJob model - tracks the progress of an ongoing analysis
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class AnalysisJob(Base):
    """
    Represents the status and progress of an analysis job
    """
    __tablename__ = "analysis_jobs"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key
    audit_id = Column(String(36), ForeignKey("audits.id"), nullable=False, index=True, unique=True)
    
    # Status tracking
    status = Column(String(50), nullable=False, default="queued")  # queued, processing, completed, failed
    progress = Column(Integer, nullable=False, default=0)  # 0-100
    current_stage = Column(String(255), nullable=False, default="Queued")
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    audit = relationship("Audit", back_populates="analysis_job")
    
    def __repr__(self) -> str:
        return f"<AnalysisJob id={self.id} audit={self.audit_id} status={self.status} progress={self.progress}%>"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "audit_id": self.audit_id,
            "status": self.status,
            "progress": self.progress,
            "current_stage": self.current_stage,
            "error_message": self.error_message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
