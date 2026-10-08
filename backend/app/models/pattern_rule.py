"""
Pattern Rule model - stores rule-based dark pattern detection rules
"""

import uuid
from sqlalchemy import Column, String, Float, Integer, Text, Boolean
from app.database import Base


class PatternRule(Base):
    """
    Rule-based dark pattern detection.
    Used for quick, deterministic pattern matching before calling LLM.
    """
    __tablename__ = "pattern_rules"

    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Pattern classification
    category = Column(String(100), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    
    # Detection rules
    trigger_phrases = Column(Text, nullable=False)  # JSON array of phrases to search for
    keyword_patterns = Column(Text, nullable=True)  # JSON array of regex patterns
    visual_indicators = Column(Text, nullable=True)  # JSON array of visual cues
    
    # Confidence & severity
    default_severity = Column(String(20), nullable=False)  # low, medium, high, critical
    confidence_threshold = Column(Float, nullable=False, default=0.8)  # 0.0-1.0
    
    # Metadata
    enabled = Column(Boolean, nullable=False, default=True)
    priority = Column(Integer, nullable=False, default=50)  # Higher = checked first
    
    def __repr__(self) -> str:
        return f"<PatternRule category={self.category} title={self.title}>"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "default_severity": self.default_severity,
            "confidence_threshold": self.confidence_threshold,
            "enabled": self.enabled,
            "priority": self.priority,
        }
