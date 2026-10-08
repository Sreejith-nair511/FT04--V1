"""
Pydantic schemas for Evidence model
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class EvidenceResponse(BaseModel):
    """Response schema for a single evidence item"""
    id: str
    finding_id: Optional[str] = None
    audit_id: str
    evidence_type: str
    frame_number: Optional[int] = None
    timestamp_seconds: Optional[float] = None
    x: float
    y: float
    width: float
    height: float
    image_path: Optional[str] = None
    text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
