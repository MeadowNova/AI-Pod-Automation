"""
Cache manager for pod_automation.
This module provides caching functionality for the system.
"""

import logging
import os
import json
import time
import hashlib
from typing import Dict, Any, Optional, Union, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar('T')

class CacheManager:
    """Cache manager for storing and retrieving cached data."""
    
    def __init__(self, cache_dir: str = None, max_age: int = 3600):
        """Initialize cache manager.
        
        Args:
            cache_dir (str, optional): Directory to store cache files
            max_age (int, optional): Maximum age of cache entries in seconds
        """
        self.cache_dir = cache_dir or os.path.join(os.path.dirname(__file__), "..", "..", "cache")
        self.max_age = max_age
        self.memory_cache = {}
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.debug(f"Initialized cache manager with cache directory: {self.cache_dir}")
    
    def _get_cache_key(self, key: str) -> str:
        """Get cache key.
        
        Args:
            key (str): Cache key
            
        Returns:
            str: Hashed cache key
        """
        return hashlib.md5(key.encode()).hexdigest()
    
    def _get_cache_path(self, key: str) -> str:
        """Get cache file path.
        
        Args:
            key (str): Cache key
            
        Returns:
            str: Cache file path
        """
        cache_key = self._get_cache_key(key)
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache.
        
        Args:
            key (str): Cache key
            default (Any, optional): Default value if key not found
            
        Returns:
            Any: Cached value or default
        """
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if time.time() - entry["timestamp"] <= self.max_age:
                logger.debug(f"Memory cache hit for key: {key}")
                return entry["value"]
            else:
                # Remove expired entry
                del self.memory_cache[key]
        
        # Check file cache
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                with open(cache_path, "r") as f:
                    entry = json.load(f)
                
                if time.time() - entry["timestamp"] <= self.max_age:
                    # Add to memory cache
                    self.memory_cache[key] = entry
                    logger.debug(f"File cache hit for key: {key}")
                    return entry["value"]
                else:
                    # Remove expired file
                    os.remove(cache_path)
            except Exception as e:
                logger.error(f"Error reading cache file: {str(e)}")
        
        return default
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache.
        
        Args:
            key (str): Cache key
            value (Any): Value to cache
        """
        entry = {
            "timestamp": time.time(),
            "value": value
        }
        
        # Add to memory cache
        self.memory_cache[key] = entry
        
        # Add to file cache
        cache_path = self._get_cache_path(key)
        try:
            with open(cache_path, "w") as f:
                json.dump(entry, f)
            logger.debug(f"Cached value for key: {key}")
        except Exception as e:
            logger.error(f"Error writing cache file: {str(e)}")
    
    def delete(self, key: str) -> None:
        """Delete value from cache.
        
        Args:
            key (str): Cache key
        """
        # Remove from memory cache
        if key in self.memory_cache:
            del self.memory_cache[key]
        
        # Remove from file cache
        cache_path = self._get_cache_path(key)
        if os.path.exists(cache_path):
            try:
                os.remove(cache_path)
                logger.debug(f"Deleted cache for key: {key}")
            except Exception as e:
                logger.error(f"Error deleting cache file: {str(e)}")
    
    def clear(self) -> None:
        """Clear all cache entries."""
        # Clear memory cache
        self.memory_cache = {}
        
        # Clear file cache
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith(".json"):
                    os.remove(os.path.join(self.cache_dir, filename))
            logger.info("Cache cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
    
    def cached(self, func: Callable[..., T]) -> Callable[..., T]:
        """Decorator to cache function results.
        
        Args:
            func: Function to cache
            
        Returns:
            Cached function
        """
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            key = f"{func.__module__}.{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached_result = self.get(key)
            if cached_result is not None:
                return cached_result
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            self.set(key, result)
            return result
        
        return wrapper