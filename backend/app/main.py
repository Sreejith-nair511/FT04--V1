"""
CogniShield Backend - Main FastAPI application
"""

import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db, check_db_connection
from app.utils.security import ensure_directory
from app.api import health, audits, findings, evidence, reports

# Configure logging
logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting CogniShield backend...")
    
    # Initialize storage directories
    ensure_directory(settings.storage_dir)
    ensure_directory(f"{settings.storage_dir}/uploads")
    ensure_directory(f"{settings.storage_dir}/frames")
    ensure_directory(settings.report_dir)
    
    # Initialize database
    if not init_db():
        logger.warning("Database initialization failed, but continuing...")
    
    # Initialize pattern rules
    from app.services.rule_engine import RuleEngine
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        RuleEngine.initialize_rules(db)
    finally:
        db.close()
    
    logger.info("CogniShield backend startup complete")
    yield
    # Shutdown
    logger.info("Shutting down CogniShield backend...")


# Create FastAPI app
app = FastAPI(
    title="CogniShield AI",
    description="Dark-Pattern Auditor for FinTech Applications",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
origins = settings.cors_origins_list
logger.info(f"Configuring CORS for origins: {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(audits.router, prefix="/api", tags=["audits"])
app.include_router(findings.router, prefix="/api", tags=["findings"])
app.include_router(evidence.router, prefix="/api", tags=["evidence"])
app.include_router(reports.router, prefix="/api", tags=["reports"])


# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle unhandled exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": str(exc) if settings.environment == "development" else None
            }
        }
    )


# Root endpoint
@app.get("/", tags=["root"])
async def root():
    """Root endpoint"""
    return {
        "name": "CogniShield AI",
        "version": "0.1.0",
        "status": "running",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development"
    )
