"""
Report generation endpoints
"""

import json
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Audit
from app.config import settings
from app.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/reports/{audit_id}/pdf")
async def generate_pdf_report(
    audit_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate a PDF report for an audit
    
    Returns: PDF file for download
    """
    audit_data = AnalysisService.get_audit_with_findings(db, audit_id)
    
    if not audit_data:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    try:
        # For MVP: Generate a simple text report
        # In production: Use ReportLab to generate professional PDF
        
        report_filename = f"{audit_id}_report.pdf"
        report_path = Path(settings.report_dir) / report_filename
        
        # Create a simple text-based report (placeholder)
        report_content = f"""
CogniShield AI - Dark Pattern Audit Report
Application: {audit_data['application_name']}
Audit ID: {audit_data['id']}
Date: {audit_data['created_at']}
Platform: {audit_data['platform']}

Overall Risk: {audit_data['risk_level']} ({audit_data['risk_score']}/100)

Summary: {audit_data['summary']}

Findings: {len(audit_data['findings'])}

{chr(10).join(f"- {f['title']} ({f['severity'].upper()})" for f in audit_data['findings'])}
"""
        
        # For now, return JSON instead of PDF
        # In production, would use ReportLab to generate actual PDF
        logger.warning("PDF generation is placeholder - returning JSON report instead")
        return {
            "message": "PDF generation not yet implemented",
            "fallback": "Use /api/reports/{audit_id}/json instead"
        }
        
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}")
        raise HTTPException(status_code=500, detail="Report generation failed")


@router.post("/reports/{audit_id}/json")
async def generate_json_report(
    audit_id: str,
    db: Session = Depends(get_db)
):
    """
    Generate a JSON report for an audit
    
    Returns: JSON structure with all audit data
    """
    audit_data = AnalysisService.get_audit_with_findings(db, audit_id)
    
    if not audit_data:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return {
        "report_type": "json",
        "generated_at": audit_data['updated_at'],
        "audit": audit_data
    }


@router.get("/reports/{audit_id}")
async def get_report(
    audit_id: str,
    db: Session = Depends(get_db)
):
    """Get report metadata for an audit"""
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return {
        "audit_id": audit_id,
        "status": audit.status,
        "available_formats": ["json", "pdf"],
        "json_url": f"/api/reports/{audit_id}/json",
        "pdf_url": f"/api/reports/{audit_id}/pdf"
    }
