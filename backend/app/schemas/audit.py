"""
Pydantic schemas for Audit model
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class AuditResponse(BaseModel):
    """Response schema for a single audit"""
    id: str
    application_name: str
    platform: str
    input_type: str
    status: str
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    summary: Optional[str] = None
    model_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AuditListResponse(BaseModel):
    """Response schema for audit listing with pagination"""
    items: List[AuditResponse]
    page: int
    page_size: int
    total: int
    pages: int
