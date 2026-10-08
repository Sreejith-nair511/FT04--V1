"""
Findings endpoints
"""

import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Finding
from app.schemas import FindingResponse, FindingListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/findings", response_model=FindingListResponse)
async def list_findings(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> FindingListResponse:
    """
    List all findings with filtering and pagination
    
    Query Parameters:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        severity: Filter by severity (low, medium, high, critical)
        category: Filter by category
        status: Filter by status (open, reviewed, resolved)
        search: Search in title and evidence_text
    """
    query = db.query(Finding)
    
    # Apply filters
    if severity:
        query = query.filter(Finding.severity == severity.lower())
    if category:
        query = query.filter(Finding.category == category)
    if status:
        query = query.filter(Finding.status == status)
    if search:
        query = query.filter(
            (Finding.title.ilike(f"%{search}%")) |
            (Finding.evidence_text.ilike(f"%{search}%"))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    findings = query.order_by(Finding.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Convert to response
    items = [FindingResponse.from_orm(finding) for finding in findings]
    
    pages = (total + page_size - 1) // page_size
    
    return FindingListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pages=pages
    )


@router.get("/findings/{finding_id}", response_model=FindingResponse)
async def get_finding(
    finding_id: str,
    db: Session = Depends(get_db)
) -> FindingResponse:
    """Get a single finding by ID"""
    finding = db.query(Finding).filter(Finding.id == finding_id).first()
    
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    
    return FindingResponse.from_orm(finding)
