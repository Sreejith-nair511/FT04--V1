"""
Evidence endpoints
"""

import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Evidence
from app.schemas import EvidenceResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/evidence/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: str,
    db: Session = Depends(get_db)
) -> EvidenceResponse:
    """Get a single evidence item by ID"""
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    return EvidenceResponse.from_orm(evidence)
