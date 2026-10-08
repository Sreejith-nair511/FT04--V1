"""
File validation utilities
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Allowed file types
ALLOWED_IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.webp'}
ALLOWED_IMAGE_MIMETYPES = {'image/png', 'image/jpeg', 'image/webp'}

ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.mov', '.webm'}
ALLOWED_VIDEO_MIMETYPES = {'video/mp4', 'video/quicktime', 'video/webm'}


def validate_image_file(filename: str, content_type: str, file_size_bytes: int, max_size_mb: int) -> tuple[bool, str]:
    """
    Validate image file for upload
    
    Args:
        filename: The filename
        content_type: The MIME type
        file_size_bytes: The file size in bytes
        max_size_mb: Maximum allowed size in MB
    
    Returns:
        (is_valid, error_message)
    """
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        return False, f"Invalid image format. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
    
    # Check MIME type
    if content_type and content_type not in ALLOWED_IMAGE_MIMETYPES:
        return False, f"Invalid MIME type: {content_type}"
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        return False, f"File too large. Maximum: {max_size_mb}MB"
    
    if file_size_bytes == 0:
        return False, "File is empty"
    
    return True, ""


def validate_video_file(
    filename: str, 
    content_type: str, 
    file_size_bytes: int, 
    max_size_mb: int,
    duration_seconds: int = None,
    max_duration_seconds: int = 120
) -> tuple[bool, str]:
    """
    Validate video file for upload
    
    Args:
        filename: The filename
        content_type: The MIME type
        file_size_bytes: The file size in bytes
        max_size_mb: Maximum allowed size in MB
        duration_seconds: Video duration in seconds (if available)
        max_duration_seconds: Maximum allowed duration
    
    Returns:
        (is_valid, error_message)
    """
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        return False, f"Invalid video format. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
    
    # Check MIME type
    if content_type and content_type not in ALLOWED_VIDEO_MIMETYPES:
        return False, f"Invalid MIME type: {content_type}"
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size_bytes > max_size_bytes:
        return False, f"File too large. Maximum: {max_size_mb}MB"
    
    if file_size_bytes == 0:
        return False, "File is empty"
    
    # Check duration if available
    if duration_seconds is not None and duration_seconds > max_duration_seconds:
        minutes = max_duration_seconds // 60
        return False, f"Video too long. Maximum: {minutes} minute(s) ({max_duration_seconds}s)"
    
    return True, ""
