"""
Security utilities for file handling and path validation
"""

import os
import uuid
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def generate_safe_filename(audit_id: str, original_filename: str, file_extension: str) -> str:
    """
    Generate a safe filename that prevents path traversal attacks
    
    Args:
        audit_id: The audit UUID
        original_filename: The original filename from user
        file_extension: The file extension (e.g., 'png', 'jpg')
    
    Returns:
        Safe filename in format: {audit_id}_original.{ext}
    """
    # Extract extension from original filename if available
    if file_extension:
        return f"{audit_id}_original.{file_extension.lower()}"
    
    # Fallback: try to extract from original filename
    _, ext = os.path.splitext(original_filename)
    if ext:
        ext = ext.lstrip('.').lower()
    else:
        ext = "bin"
    
    return f"{audit_id}_original.{ext}"


def validate_file_path(base_dir: str, file_path: str) -> bool:
    """
    Validate that a file path is within the base directory (prevent path traversal)
    
    Args:
        base_dir: The base directory where files should be stored
        file_path: The file path to validate
    
    Returns:
        True if the path is safe, False otherwise
    """
    try:
        base = Path(base_dir).resolve()
        full_path = (base / file_path).resolve()
        
        # Check if the resolved path is within the base directory
        if not str(full_path).startswith(str(base)):
            logger.warning(f"Path traversal attempt detected: {file_path}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating file path: {e}")
        return False


def ensure_directory(directory: str) -> bool:
    """
    Ensure a directory exists, create it if needed
    
    Args:
        directory: Path to directory
    
    Returns:
        True if directory exists or was created, False otherwise
    """
    try:
        Path(directory).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False
