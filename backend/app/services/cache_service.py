"""
Analysis caching service to avoid duplicate Gemini calls.
Uses content hash to identify identical uploads.
"""

import hashlib
import json
import logging
from typing import Optional, Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class CacheService:
    """Cache for analysis results"""
    
    def __init__(self, cache_dir: str = "./storage/.cache"):
        """Initialize cache service"""
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Cache service initialized at {self.cache_dir}")
    
    @staticmethod
    def compute_hash(file_path: str) -> str:
        """
        Compute SHA-256 hash of file content.
        
        Args:
            file_path: Path to file
        
        Returns:
            Hex hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def get_cached_result(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis result if it exists.
        
        Args:
            file_path: Path to uploaded file
        
        Returns:
            Cached result dict, or None if not cached
        """
        try:
            content_hash = self.compute_hash(file_path)
            cache_file = self.cache_dir / f"{content_hash}.json"
            
            if not cache_file.exists():
                logger.debug(f"Cache miss for hash {content_hash}")
                return None
            
            with open(cache_file, "r") as f:
                result = json.load(f)
            
            logger.info(f"Cache hit for hash {content_hash}")
            return result
            
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
            return None
    
    def cache_result(self, file_path: str, result: Dict[str, Any]) -> bool:
        """
        Cache analysis result.
        
        Args:
            file_path: Path to uploaded file
            result: Analysis result to cache
        
        Returns:
            True if cached successfully
        """
        try:
            content_hash = self.compute_hash(file_path)
            cache_file = self.cache_dir / f"{content_hash}.json"
            
            with open(cache_file, "w") as f:
                json.dump(result, f)
            
            logger.info(f"Cached result for hash {content_hash}")
            return True
            
        except Exception as e:
            logger.warning(f"Error caching result: {e}")
            return False
    
    def clear_cache(self) -> int:
        """
        Clear all cached results.
        
        Returns:
            Number of cache files deleted
        """
        try:
            count = 0
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
                count += 1
            logger.info(f"Cleared {count} cache files")
            return count
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return 0
