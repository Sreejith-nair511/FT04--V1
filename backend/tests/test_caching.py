"""
Tests for analysis caching
"""

import pytest
import json
import tempfile
from pathlib import Path
from app.services.cache_service import CacheService


class TestCaching:
    """Test content-hash based caching"""
    
    def test_cache_initialization(self, temp_storage):
        """Cache service initializes correctly"""
        cache = CacheService(str(temp_storage / ".cache"))
        assert (temp_storage / ".cache").exists()
    
    def test_compute_hash(self, sample_image_bytes):
        """File hash computation"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(sample_image_bytes)
            f.flush()
            file_path = f.name
        
        try:
            hash1 = CacheService.compute_hash(file_path)
            hash2 = CacheService.compute_hash(file_path)
            
            assert hash1 == hash2  # Consistent hash
            assert len(hash1) == 64  # SHA-256 is 64 hex chars
        finally:
            try:
                Path(file_path).unlink()
            except (PermissionError, FileNotFoundError):
                pass  # Ignore cleanup errors on Windows
    
    def test_cache_hit(self, temp_storage, sample_image_bytes):
        """Cache hit returns stored result"""
        cache = CacheService(str(temp_storage / ".cache"))
        
        # Create test file
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(sample_image_bytes)
            f.flush()
            file_path = f.name
        
        try:
            # First call - cache miss
            result = cache.get_cached_result(file_path)
            assert result is None
            
            # Store result
            test_result = {"findings": [], "risk_score": 50}
            cache.cache_result(file_path, test_result)
            
            # Second call - cache hit
            cached = cache.get_cached_result(file_path)
            assert cached is not None
            assert cached == test_result
        finally:
            try:
                Path(file_path).unlink()
            except (PermissionError, FileNotFoundError):
                pass
    
    def test_cache_different_files(self, temp_storage):
        """Different files get different cache entries"""
        cache = CacheService(str(temp_storage / ".cache"))
        
        # Create two different files
        with tempfile.NamedTemporaryFile(delete=False) as f1:
            f1.write(b"file1 content")
            f1.flush()
            path1 = f1.name
        
        with tempfile.NamedTemporaryFile(delete=False) as f2:
            f2.write(b"file2 content different")
            f2.flush()
            path2 = f2.name
        
        try:
            # Cache different results
            result1 = {"findings": [1], "risk_score": 50}
            result2 = {"findings": [2], "risk_score": 75}
            
            cache.cache_result(path1, result1)
            cache.cache_result(path2, result2)
            
            # Retrieve separately
            cached1 = cache.get_cached_result(path1)
            cached2 = cache.get_cached_result(path2)
            
            assert cached1["risk_score"] == 50
            assert cached2["risk_score"] == 75
        finally:
            try:
                Path(path1).unlink()
            except (PermissionError, FileNotFoundError):
                pass
            try:
                Path(path2).unlink()
            except (PermissionError, FileNotFoundError):
                pass
    
    def test_clear_cache(self, temp_storage, sample_image_bytes):
        """Clear all cache entries"""
        cache = CacheService(str(temp_storage / ".cache"))
        
        # Create and cache files
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(sample_image_bytes)
            f.flush()
            file_path = f.name
        
        try:
            cache.cache_result(file_path, {"test": "data"})
            
            # Cache should have entries
            assert cache.get_cached_result(file_path) is not None
            
            # Clear
            count = cache.clear_cache()
            assert count >= 1
            
            # Cache should be empty
            assert cache.get_cached_result(file_path) is None
        finally:
            try:
                Path(file_path).unlink()
            except (PermissionError, FileNotFoundError):
                pass
    
    def test_error_handling(self, temp_storage):
        """Cache gracefully handles errors"""
        cache = CacheService(str(temp_storage / ".cache"))
        
        # Try to cache with non-existent file
        result = cache.get_cached_result("/non/existent/file.png")
        assert result is None  # Returns None instead of crashing
    
    def test_cache_structure(self, temp_storage, sample_image_bytes):
        """Cache files stored with correct naming"""
        cache = CacheService(str(temp_storage / ".cache"))
        
        with tempfile.NamedTemporaryFile(delete=False) as f:
            f.write(sample_image_bytes)
            f.flush()
            file_path = f.name
        
        try:
            content_hash = CacheService.compute_hash(file_path)
            cache.cache_result(file_path, {"test": "data"})
            
            # Check cache file exists
            cache_file = Path(temp_storage / ".cache" / f"{content_hash}.json")
            assert cache_file.exists()
            
            # Check format
            with open(cache_file) as f:
                cached = json.load(f)
            assert cached["test"] == "data"
        finally:
            try:
                Path(file_path).unlink()
            except (PermissionError, FileNotFoundError):
                pass
