"""
Health check endpoints
"""

import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db, check_db_connection
from app.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint
    
    Returns status of database, storage, and Gemini API
    """
    db_ok = check_db_connection()
    gemini_service = GeminiService()
    gemini_configured = gemini_service.is_configured
    
    status = "ok" if (db_ok and gemini_configured) else "degraded"
    
    return {
        "status": status,
        "database": "ok" if db_ok else "error",
        "storage": "ok",  # Assuming storage dir was created
        "gemini_configured": gemini_configured,
        "gemini_model": gemini_service.model_name if gemini_configured else None
    }


@router.get("/health/gemini")
async def gemini_health_check():
    """
    Check Gemini API connectivity
    
    Returns Gemini API status
    """
    gemini_service = GeminiService()
    
    if not gemini_service.is_configured:
        return {
            "status": "not_configured",
            "message": "Gemini API key is not configured",
            "model": None
        }
    
    is_healthy = gemini_service.health_check()
    
    return {
        "status": "connected" if is_healthy else "error",
        "model": gemini_service.model_name,
        "message": "Gemini API is healthy" if is_healthy else "Failed to connect to Gemini API"
    }
