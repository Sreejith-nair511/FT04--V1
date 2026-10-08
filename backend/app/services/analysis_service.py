"""
Analysis service - orchestrates the audit workflow
"""

import logging
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Audit, Finding, Evidence, AnalysisJob
from app.utils import calculate_risk_score, generate_safe_filename, ensure_directory
from app.config import settings

logger = logging.getLogger(__name__)

# Import services (avoid circular imports by doing here)
_gemini_service = None
_cache_service = None
_rule_engine = None

def get_gemini_service():
    global _gemini_service
    if _gemini_service is None:
        from app.services.gemini_service import GeminiService
        _gemini_service = GeminiService()
    return _gemini_service

def get_cache_service():
    global _cache_service
    if _cache_service is None:
        from app.services.cache_service import CacheService
        _cache_service = CacheService()
    return _cache_service

def get_rule_engine():
    global _rule_engine
    if _rule_engine is None:
        from app.services.rule_engine import RuleEngine
        _rule_engine = RuleEngine()
    return _rule_engine


class AnalysisService:
    """Service for managing analysis workflow"""
    
    @staticmethod
    def create_audit(
        db: Session,
        application_name: str,
        platform: str,
        input_type: str,
        original_filename: str,
        file_path: str
    ) -> Audit:
        """Create a new audit record"""
        audit = Audit(
            application_name=application_name,
            platform=platform,
            input_type=input_type,
            original_filename=original_filename,
            file_path=file_path,
            status="queued"
        )
        db.add(audit)
        db.commit()
        db.refresh(audit)
        logger.info(f"Created audit {audit.id} for {application_name}")
        return audit
    
    @staticmethod
    def create_analysis_job(db: Session, audit_id: str) -> AnalysisJob:
        """Create analysis job for an audit"""
        job = AnalysisJob(
            audit_id=audit_id,
            status="queued",
            current_stage="Initializing"
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        logger.info(f"Created analysis job {job.id} for audit {audit_id}")
        return job
    
    @staticmethod
    def update_job_progress(
        db: Session,
        job_id: str,
        status: str,
        progress: int,
        current_stage: str,
        error_message: Optional[str] = None
    ) -> AnalysisJob:
        """Update analysis job progress"""
        job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = status
        job.progress = progress
        job.current_stage = current_stage
        if error_message:
            job.error_message = error_message
        
        if status == "processing" and not job.started_at:
            job.started_at = datetime.utcnow()
        elif status in ["completed", "failed"]:
            job.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(job)
        return job
    
    @staticmethod
    def create_findings_from_analysis(
        db: Session,
        audit_id: str,
        analysis_result: Dict[str, Any]
    ) -> List[Finding]:
        """
        Create Finding and Evidence records from analysis result.
        Validates results for hallucinations before storing.
        
        Args:
            db: Database session
            audit_id: Audit ID
            analysis_result: Result from Gemini API with findings
        
        Returns:
            List of created Finding objects
        """
        from app.utils import HallucinationGuardrail
        
        # Validate response for hallucinations
        is_valid, valid_findings, issues = HallucinationGuardrail.validate_response(analysis_result)
        
        if issues:
            logger.warning(f"Validation issues: {issues}")
            analysis_result["validation_issues"] = issues
        
        # Use validated findings
        findings_data = valid_findings if valid_findings else analysis_result.get("findings", [])
        created_findings = []
        
        for idx, finding_data in enumerate(findings_data, start=1):
            # Create finding
            finding = Finding(
                audit_id=audit_id,
                finding_number=idx,
                category=finding_data.get("category", "other"),
                title=finding_data.get("title", "Unknown Pattern"),
                severity=finding_data.get("severity", "low").lower(),
                confidence=finding_data.get("confidence", 0),
                evidence_text=finding_data.get("evidence_text", ""),
                why_problematic=finding_data.get("why_problematic", ""),
                user_impact=finding_data.get("user_impact", ""),
                recommended_fix=finding_data.get("recommended_fix", ""),
                status="open"
            )
            db.add(finding)
            db.flush()  # Flush to get the finding ID
            
            # Create evidence if provided
            evidence_data = finding_data.get("evidence", {})
            if evidence_data:
                evidence = Evidence(
                    finding_id=finding.id,
                    audit_id=audit_id,
                    evidence_type="box",
                    x=evidence_data.get("x", 0),
                    y=evidence_data.get("y", 0),
                    width=evidence_data.get("width", 0),
                    height=evidence_data.get("height", 0),
                    timestamp_seconds=finding_data.get("timestamp_seconds"),
                    frame_number=finding_data.get("frame_number"),
                )
                db.add(evidence)
            
            created_findings.append(finding)
            logger.info(f"Created finding: {finding.category} - {finding.title}")
        
        db.commit()
        return created_findings
    
    @staticmethod
    def complete_audit(
        db: Session,
        audit_id: str,
        analysis_result: Dict[str, Any]
    ) -> Audit:
        """
        Complete an audit with analysis results
        
        Args:
            db: Database session
            audit_id: Audit ID
            analysis_result: Result from analysis
        
        Returns:
            Updated Audit object
        """
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise ValueError(f"Audit {audit_id} not found")
        
        # Get all findings for this audit
        findings = db.query(Finding).filter(Finding.audit_id == audit_id).all()
        findings_data = [
            {
                "severity": f.severity,
                "confidence": f.confidence
            }
            for f in findings
        ]
        
        # Calculate risk score
        risk_score, risk_level = calculate_risk_score(findings_data)
        
        # Update audit
        audit.status = "completed"
        audit.risk_score = risk_score
        audit.risk_level = risk_level
        audit.summary = analysis_result.get("summary", "Analysis complete")
        audit.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(audit)
        
        logger.info(f"Completed audit {audit_id}: risk_score={risk_score}, risk_level={risk_level}")
        return audit
    
    @staticmethod
    def get_audit_with_findings(db: Session, audit_id: str) -> Optional[Dict[str, Any]]:
        """Get audit with all associated findings and evidence"""
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            return None
        
        findings = db.query(Finding).filter(Finding.audit_id == audit_id).all()
        
        findings_list = []
        for finding in findings:
            evidence_items = db.query(Evidence).filter(Evidence.finding_id == finding.id).all()
            
            finding_dict = finding.to_dict()
            finding_dict["evidence"] = [e.to_dict() for e in evidence_items]
            findings_list.append(finding_dict)
        
        audit_dict = audit.to_dict()
        audit_dict["findings"] = findings_list
        
        return audit_dict
    
    @staticmethod
    def analyze_with_optimization(
        db: Session,
        file_path: str,
        input_type: str = "image"
    ) -> Dict[str, Any]:
        """
        Analyze file with optimization (cache → rules → Gemini).
        
        Args:
            db: Database session
            file_path: Path to uploaded file
            input_type: "image" or "video"
        
        Returns:
            Analysis result with detection_method field
        """
        cache_svc = get_cache_service()
        
        # Step 1: Check cache
        logger.info(f"[{input_type}] Step 1/4: Checking cache...")
        cached_result = cache_svc.get_cached_result(file_path)
        if cached_result:
            logger.info(f"[{input_type}] Cache hit! Skipping LLM call")
            cached_result["_from_cache"] = True
            return cached_result
        
        # Step 2: Try rule-based detection (image only for MVP)
        if input_type == "image":
            logger.info(f"[{input_type}] Step 2/4: Running rule engine...")
            rule_engine = get_rule_engine()
            
            # Extract text from image (basic OCR simulation)
            # In production: use Tesseract or similar
            rule_findings = []  # For now, empty - would need OCR
            
            if rule_findings:
                logger.info(f"[{input_type}] Rule engine found {len(rule_findings)} patterns")
                result = {
                    "overall_risk_score": 0,
                    "risk_level": "LOW",
                    "summary": "Patterns detected by rule engine",
                    "findings": rule_findings,
                    "analysis_notes": ["Detected via rule engine (no LLM call)"],
                    "_detection_method": "RULE_ENGINE"
                }
                # Calculate risk score
                if rule_findings:
                    risk_score, risk_level = calculate_risk_score([
                        {"severity": f["severity"], "confidence": f["confidence"]}
                        for f in rule_findings
                    ])
                    result["overall_risk_score"] = risk_score
                    result["risk_level"] = risk_level
                
                cache_svc.cache_result(file_path, result)
                return result
        
        # Step 3: Call Gemini
        logger.info(f"[{input_type}] Step 3/4: Calling Gemini API...")
        gemini_svc = get_gemini_service()
        
        if input_type == "image":
            analysis_result = gemini_svc.analyze_image(file_path)
        else:
            analysis_result = gemini_svc.analyze_video(file_path)
        
        analysis_result["_detection_method"] = "LLM_ASSISTED"
        
        # Step 4: Cache result
        logger.info(f"[{input_type}] Step 4/4: Caching result...")
        cache_svc.cache_result(file_path, analysis_result)
        
        return analysis_result
    
    @staticmethod
    def fail_audit(
        db: Session,
        audit_id: str,
        error_message: str
    ) -> Audit:
        """Mark audit as failed"""
        audit = db.query(Audit).filter(Audit.id == audit_id).first()
        if not audit:
            raise ValueError(f"Audit {audit_id} not found")
        
        audit.status = "failed"
        audit.completed_at = datetime.utcnow()
        
        job = db.query(AnalysisJob).filter(AnalysisJob.audit_id == audit_id).first()
        if job:
            job.status = "failed"
            job.error_message = error_message
            job.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(audit)
        logger.error(f"Failed audit {audit_id}: {error_message}")
        return audit
