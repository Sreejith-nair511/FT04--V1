"""
Audit analysis endpoints
"""

import logging
import os
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, BackgroundTasks, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models import Audit, AnalysisJob
from app.services.analysis_service import AnalysisService
from app.utils import validate_image_file, validate_video_file, generate_safe_filename, ensure_directory
from app.schemas import AuditResponse, AuditListResponse

logger = logging.getLogger(__name__)
router = APIRouter()


def save_upload_file(upload_file: UploadFile, audit_id: str, subfolder: str) -> str:
    """Save uploaded file to storage directory"""
    ensure_directory(f"{settings.storage_dir}/{subfolder}")
    
    # Generate safe filename
    file_ext = Path(upload_file.filename).suffix.lstrip('.')
    safe_filename = generate_safe_filename(audit_id, upload_file.filename, file_ext)
    file_path = f"{settings.storage_dir}/{subfolder}/{safe_filename}"
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(upload_file.file.read())
    
    logger.info(f"Saved file: {file_path}")
    return file_path


async def process_image_analysis(
    db: Session,
    audit: Audit,
    job: AnalysisJob,
    file_path: str
) -> None:
    """Background task for image analysis"""
    try:
        # Update job: uploading
        AnalysisService.update_job_progress(
            db, job.id, "processing", 20, "Uploading evidence"
        )
        
        # Update job: checking optimization layers
        AnalysisService.update_job_progress(
            db, job.id, "processing", 35, "Checking cache and rules"
        )
        
        # Optimized analysis (cache → rules → Gemini)
        analysis_result = AnalysisService.analyze_with_optimization(
            db, file_path, input_type="image"
        )
        
        # Update job: processing results
        AnalysisService.update_job_progress(
            db, job.id, "processing", 60, "Processing analysis results"
        )
        
        # Create findings
        AnalysisService.create_findings_from_analysis(db, audit.id, analysis_result)
        
        # Update job: calculating risk
        AnalysisService.update_job_progress(
            db, job.id, "processing", 85, "Calculating risk score"
        )
        
        # Complete audit
        AnalysisService.complete_audit(db, audit.id, analysis_result)
        
        # Update job: done
        AnalysisService.update_job_progress(
            db, job.id, "completed", 100, "Analysis complete"
        )
        
        detection_method = analysis_result.get("_detection_method", "unknown")
        logger.info(f"Image analysis completed for audit {audit.id} (method: {detection_method})")
        
    except Exception as e:
        logger.error(f"Error processing image analysis: {e}")
        AnalysisService.fail_audit(db, audit.id, str(e))
        AnalysisService.update_job_progress(
            db, job.id, "failed", 0, "Failed", error_message=str(e)
        )


async def process_video_analysis(
    db: Session,
    audit: Audit,
    job: AnalysisJob,
    file_path: str
) -> None:
    """Background task for video analysis"""
    try:
        # Update job: uploading
        AnalysisService.update_job_progress(
            db, job.id, "processing", 15, "Uploading video file"
        )
        
        # Update job: checking cache
        AnalysisService.update_job_progress(
            db, job.id, "processing", 35, "Checking cache"
        )
        
        # Optimized analysis (cache → Gemini for video)
        analysis_result = AnalysisService.analyze_with_optimization(
            db, file_path, input_type="video"
        )
        
        # Update job: processing results
        AnalysisService.update_job_progress(
            db, job.id, "processing", 60, "Processing video results"
        )
        
        # Create findings with timestamps
        AnalysisService.create_findings_from_analysis(db, audit.id, analysis_result)
        
        # Update job: calculating risk
        AnalysisService.update_job_progress(
            db, job.id, "processing", 85, "Calculating risk score"
        )
        
        # Complete audit
        AnalysisService.complete_audit(db, audit.id, analysis_result)
        
        # Update job: done
        AnalysisService.update_job_progress(
            db, job.id, "completed", 100, "Analysis complete"
        )
        
        detection_method = analysis_result.get("_detection_method", "unknown")
        logger.info(f"Video analysis completed for audit {audit.id} (method: {detection_method})")
        
    except Exception as e:
        logger.error(f"Error processing video analysis: {e}")
        AnalysisService.fail_audit(db, audit.id, str(e))
        AnalysisService.update_job_progress(
            db, job.id, "failed", 0, "Failed", error_message=str(e)
        )


@router.post("/analyze/image", response_model=dict)
async def analyze_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    application_name: str = Form(...),
    platform: str = Form(...),
    analysis_depth: str = Form("Deep analysis"),
    db: Session = Depends(get_db)
) -> dict:
    """
    Upload and analyze a screenshot
    
    Args:
        file: Image file (PNG, JPG, WEBP, max 20MB)
        application_name: Name of the fintech app (e.g., "FinFlow")
        platform: Platform (iOS, Android, Web)
        analysis_depth: Analysis depth (Deep analysis or Quick scan)
    
    Returns:
        Audit creation response with status
    """
    try:
        # Validate file
        is_valid, error_msg = validate_image_file(
            file.filename,
            file.content_type,
            len(file.file.read()),
            settings.max_image_size_mb
        )
        file.file.seek(0)  # Reset file pointer
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Create audit
        file_path = save_upload_file(file, "", "uploads")
        audit = AnalysisService.create_audit(
            db,
            application_name=application_name,
            platform=platform,
            input_type="image",
            original_filename=file.filename,
            file_path=file_path
        )
        
        # Create analysis job
        job = AnalysisService.create_analysis_job(db, audit.id)
        
        # Start background analysis
        background_tasks.add_task(process_image_analysis, db, audit, job, file_path)
        
        return {
            "audit_id": audit.id,
            "status": "processing",
            "progress": 5,
            "current_stage": "Queued for analysis",
            "message": "Image uploaded successfully, analysis starting..."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        raise HTTPException(status_code=500, detail="Image upload failed")


@router.post("/analyze/video", response_model=dict)
async def analyze_video(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    application_name: str = Form(...),
    platform: str = Form(...),
    db: Session = Depends(get_db)
) -> dict:
    """
    Upload and analyze a screen recording
    
    Args:
        file: Video file (MP4, MOV, WEBM, max 200MB)
        application_name: Name of the fintech app
        platform: Platform (iOS, Android, Web)
    
    Returns:
        Audit creation response with status
    """
    try:
        # Validate file
        is_valid, error_msg = validate_video_file(
            file.filename,
            file.content_type,
            len(file.file.read()),
            settings.max_video_size_mb
        )
        file.file.seek(0)  # Reset file pointer
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Create audit
        file_path = save_upload_file(file, "", "uploads")
        audit = AnalysisService.create_audit(
            db,
            application_name=application_name,
            platform=platform,
            input_type="video",
            original_filename=file.filename,
            file_path=file_path
        )
        
        # Create analysis job
        job = AnalysisService.create_analysis_job(db, audit.id)
        
        # Start background analysis
        background_tasks.add_task(process_video_analysis, db, audit, job, file_path)
        
        return {
            "audit_id": audit.id,
            "status": "processing",
            "progress": 5,
            "current_stage": "Queued for video analysis",
            "message": "Video uploaded successfully, analysis starting..."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading video: {e}")
        raise HTTPException(status_code=500, detail="Video upload failed")


@router.get("/analysis/{audit_id}", response_model=dict)
async def get_audit_analysis(
    audit_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """Get audit details with all findings and evidence"""
    audit_data = AnalysisService.get_audit_with_findings(db, audit_id)
    
    if not audit_data:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    return {
        "audit": audit_data,
        "status": audit_data["status"],
        "risk_score": audit_data["risk_score"],
        "risk_level": audit_data["risk_level"]
    }


@router.get("/analysis/{audit_id}/status", response_model=dict)
async def get_analysis_status(
    audit_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """Get analysis job status"""
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    job = db.query(AnalysisJob).filter(AnalysisJob.audit_id == audit_id).first()
    
    if not job:
        return {
            "audit_id": audit_id,
            "status": audit.status,
            "progress": 100 if audit.status == "completed" else 0,
            "current_stage": audit.status
        }
    
    return job.to_dict()


@router.get("/analyses", response_model=AuditListResponse)
async def list_audits(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    severity: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db)
) -> AuditListResponse:
    """
    List all audits with pagination and filtering
    
    Query Parameters:
        page: Page number (default: 1)
        page_size: Items per page (default: 20, max: 100)
        severity: Filter by severity (low, medium, high, critical)
        status: Filter by status (queued, processing, completed, failed)
        search: Search in application name and summary
    """
    query = db.query(Audit)
    
    # Apply filters
    if status:
        query = query.filter(Audit.status == status)
    if severity:
        query = query.filter(Audit.risk_level == severity.upper())
    if search:
        query = query.filter(
            (Audit.application_name.ilike(f"%{search}%")) |
            (Audit.summary.ilike(f"%{search}%"))
        )
    
    # Get total count
    total = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    audits = query.order_by(Audit.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Convert to response
    items = [AuditResponse.from_orm(audit) for audit in audits]
    
    pages = (total + page_size - 1) // page_size
    
    return AuditListResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pages=pages
    )


@router.delete("/audits/{audit_id}", response_model=dict)
async def delete_audit(
    audit_id: str,
    db: Session = Depends(get_db)
) -> dict:
    """Delete an audit and all associated data"""
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    
    # Delete the audit (cascades to findings and evidence)
    db.delete(audit)
    db.commit()
    
    logger.info(f"Deleted audit {audit_id}")
    
    return {"message": f"Audit {audit_id} deleted"}
