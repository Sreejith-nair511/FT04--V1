"""
Tests for file validators
"""

import pytest
from app.utils.validators import validate_image_file, validate_video_file


class TestImageValidation:
    """Test image file validation"""
    
    def test_valid_png(self):
        """Valid PNG passes validation"""
        is_valid, msg = validate_image_file(
            "screenshot.png",
            "image/png",
            5000000,  # 5MB
            20  # 20MB limit
        )
        assert is_valid
        assert msg == ""
    
    def test_valid_jpg(self):
        """Valid JPG passes validation"""
        is_valid, msg = validate_image_file(
            "photo.jpg",
            "image/jpeg",
            3000000,
            20
        )
        assert is_valid
    
    def test_valid_webp(self):
        """Valid WEBP passes validation"""
        is_valid, msg = validate_image_file(
            "image.webp",
            "image/webp",
            2000000,
            20
        )
        assert is_valid
    
    def test_invalid_extension(self):
        """Invalid extension fails"""
        is_valid, msg = validate_image_file(
            "file.gif",
            "image/gif",
            1000000,
            20
        )
        assert not is_valid
        assert "Invalid image format" in msg
    
    def test_invalid_mime_type(self):
        """Invalid MIME type fails"""
        is_valid, msg = validate_image_file(
            "file.png",
            "image/gif",
            1000000,
            20
        )
        assert not is_valid
        assert "Invalid MIME type" in msg
    
    def test_file_too_large(self):
        """File exceeding size limit fails"""
        is_valid, msg = validate_image_file(
            "large.png",
            "image/png",
            25 * 1024 * 1024,  # 25MB
            20  # 20MB limit
        )
        assert not is_valid
        assert "too large" in msg
    
    def test_empty_file(self):
        """Empty file fails"""
        is_valid, msg = validate_image_file(
            "empty.png",
            "image/png",
            0,
            20
        )
        assert not is_valid
        assert "empty" in msg


class TestVideoValidation:
    """Test video file validation"""
    
    def test_valid_mp4(self):
        """Valid MP4 passes validation"""
        is_valid, msg = validate_video_file(
            "recording.mp4",
            "video/mp4",
            50000000,  # 50MB
            200,  # 200MB limit
            60,  # 60 seconds
            120  # 120 second limit
        )
        assert is_valid
        assert msg == ""
    
    def test_valid_mov(self):
        """Valid MOV passes validation"""
        is_valid, msg = validate_video_file(
            "video.mov",
            "video/quicktime",
            40000000,
            200,
            45,
            120
        )
        assert is_valid
    
    def test_valid_webm(self):
        """Valid WEBM passes validation"""
        is_valid, msg = validate_video_file(
            "screen.webm",
            "video/webm",
            30000000,
            200,
            30,
            120
        )
        assert is_valid
    
    def test_invalid_extension(self):
        """Invalid video extension fails"""
        is_valid, msg = validate_video_file(
            "video.avi",
            "video/x-msvideo",
            50000000,
            200,
            60,
            120
        )
        assert not is_valid
        assert "Invalid video format" in msg
    
    def test_video_too_long(self):
        """Video exceeding duration limit fails"""
        is_valid, msg = validate_video_file(
            "long.mp4",
            "video/mp4",
            50000000,
            200,
            150,  # 150 seconds
            120  # 120 second limit
        )
        assert not is_valid
        assert "too long" in msg
        assert "2 minute" in msg
    
    def test_video_file_too_large(self):
        """Video file exceeding size limit fails"""
        is_valid, msg = validate_video_file(
            "huge.mp4",
            "video/mp4",
            250 * 1024 * 1024,  # 250MB
            200,  # 200MB limit
            60,
            120
        )
        assert not is_valid
        assert "too large" in msg
    
    def test_video_empty_file(self):
        """Empty video file fails"""
        is_valid, msg = validate_video_file(
            "empty.mp4",
            "video/mp4",
            0,
            200,
            0,
            120
        )
        assert not is_valid
        assert "empty" in msg
    
    def test_no_duration_check(self):
        """Video without duration still validates size"""
        is_valid, msg = validate_video_file(
            "video.mp4",
            "video/mp4",
            50000000,
            200,
            None,  # No duration info
            120
        )
        assert is_valid
    
    def test_duration_boundary(self):
        """Video exactly at duration limit"""
        is_valid, msg = validate_video_file(
            "video.mp4",
            "video/mp4",
            50000000,
            200,
            120,  # Exactly at limit
            120
        )
        assert is_valid
