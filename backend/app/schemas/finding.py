"""
Pydantic schemas for Finding model
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class FindingResponse(BaseModel):
    """Response schema for a single finding"""
    id: str
    audit_id: str
    finding_number: int
    category: str
    title: str
    severity: str
    confidence: float
    evidence_text: str
    why_problematic: str
    user_impact: str
    recommended_fix: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class FindingListResponse(BaseModel):
    """Response schema for finding listing with pagination"""
    items: List[FindingResponse]
    page: int
    page_size: int
    total: int
    pages: int
