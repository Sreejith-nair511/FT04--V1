"""
Pydantic schemas for analysis operations
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class AnalysisStatusResponse(BaseModel):
    """Response schema for analysis status"""
    audit_id: str
    status: str
    progress: int
    current_stage: str
    error_message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


class AnalysisResultResponse(BaseModel):
    """Response schema after image/video analysis completes"""
    audit_id: str
    status: str
    progress: int
    current_stage: str
    result: Optional[dict] = None
