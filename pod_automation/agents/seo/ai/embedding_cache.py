"""
Embedding cache for efficient vector operations.

This module provides a caching system for embeddings to avoid regenerating them
for the same text, improving performance for the RAG system.
"""

import os
import json
import time
import hashlib
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import threading

logger = logging.getLogger(__name__)

class EmbeddingCache:
    """Cache for embeddings to avoid regenerating them for the same text."""

    def __init__(self, cache_dir=None, max_size=1000, ttl_seconds=86400):
        """Initialize embedding cache.

        Args:
            cache_dir (str, optional): Directory to store cache files
            max_size (int): Maximum number of embeddings to cache in memory
            ttl_seconds (int): Time-to-live for cache entries in seconds (default: 24 hours)
        """
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = {}  # In-memory cache
        self.access_times = {}  # Track when each key was last accessed
        self.stats = {
            "hits": 0,
            "misses": 0,
            "size": 0,
            "evictions": 0
        }
        self.lock = threading.RLock()  # Thread-safe operations

        # Set up cache directory
        if cache_dir:
            self.cache_dir = cache_dir
        else:
            # Default to a directory in the user's home directory
            home_dir = os.path.expanduser("~")
            self.cache_dir = os.path.join(home_dir, ".pod_automation", "embedding_cache")
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        logger.info(f"Embedding cache initialized at {self.cache_dir}")

        # Load existing cache from disk
        self._load_cache()

    def _hash_text(self, text: str, model_name: str) -> str:
        """Generate a hash for the text and model name.

        Args:
            text (str): Text to hash
            model_name (str): Model name used for embedding

        Returns:
            str: Hash string
        """
        # Combine text and model name to create a unique hash
        combined = f"{text}:{model_name}"
        return hashlib.md5(combined.encode()).hexdigest()

    def _load_cache(self):
        """Load cache from disk."""
        try:
            cache_file = os.path.join(self.cache_dir, "cache_index.json")
            if os.path.exists(cache_file):
                with open(cache_file, "r") as f:
                    cache_index = json.load(f)
                
                # Load only the most recently used entries up to max_size
                entries = sorted(cache_index.items(), key=lambda x: x[1]["last_access"], reverse=True)
                count = 0
                
                for key, metadata in entries:
                    if count >= self.max_size:
                        break
                    
                    # Check if entry is expired
                    last_access = metadata["last_access"]
                    if time.time() - last_access > self.ttl_seconds:
                        continue
                    
                    # Load embedding from file
                    embedding_file = os.path.join(self.cache_dir, f"{key}.json")
                    if os.path.exists(embedding_file):
                        with open(embedding_file, "r") as f:
                            embedding_data = json.load(f)
                            self.cache[key] = embedding_data["embedding"]
                            self.access_times[key] = last_access
                            count += 1
                
                self.stats["size"] = len(self.cache)
                logger.info(f"Loaded {len(self.cache)} embeddings from cache")
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")

    def _save_cache_index(self):
        """Save cache index to disk."""
        try:
            cache_index = {}
            for key in self.cache:
                cache_index[key] = {
                    "last_access": self.access_times.get(key, time.time()),
                    "created": self.access_times.get(key, time.time())
                }
            
            cache_file = os.path.join(self.cache_dir, "cache_index.json")
            with open(cache_file, "w") as f:
                json.dump(cache_index, f)
        except Exception as e:
            logger.error(f"Error saving cache index: {str(e)}")

    def _save_embedding(self, key: str, embedding: List[float], text: str, model_name: str):
        """Save embedding to disk.

        Args:
            key (str): Cache key
            embedding (list): Embedding vector
            text (str): Original text
            model_name (str): Model name used for embedding
        """
        try:
            embedding_file = os.path.join(self.cache_dir, f"{key}.json")
            embedding_data = {
                "embedding": embedding,
                "text": text,
                "model_name": model_name,
                "created": time.time()
            }
            
            with open(embedding_file, "w") as f:
                json.dump(embedding_data, f)
        except Exception as e:
            logger.error(f"Error saving embedding: {str(e)}")

    def _evict_if_needed(self):
        """Evict least recently used items if cache is full."""
        with self.lock:
            if len(self.cache) >= self.max_size:
                # Find least recently used item
                lru_key = min(self.access_times.items(), key=lambda x: x[1])[0]
                
                # Remove from cache
                del self.cache[lru_key]
                del self.access_times[lru_key]
                
                self.stats["evictions"] += 1
                self.stats["size"] = len(self.cache)

    def get(self, text: str, model_name: str) -> Optional[List[float]]:
        """Get embedding from cache.

        Args:
            text (str): Text to get embedding for
            model_name (str): Model name used for embedding

        Returns:
            list: Embedding vector or None if not in cache
        """
        with self.lock:
            key = self._hash_text(text, model_name)
            
            if key in self.cache:
                # Update access time
                self.access_times[key] = time.time()
                self.stats["hits"] += 1
                return self.cache[key]
            
            self.stats["misses"] += 1
            return None

    def put(self, text: str, model_name: str, embedding: List[float]):
        """Put embedding in cache.

        Args:
            text (str): Text that was embedded
            model_name (str): Model name used for embedding
            embedding (list): Embedding vector
        """
        with self.lock:
            # Evict if needed
            self._evict_if_needed()
            
            # Add to cache
            key = self._hash_text(text, model_name)
            self.cache[key] = embedding
            self.access_times[key] = time.time()
            self.stats["size"] = len(self.cache)
            
            # Save to disk
            self._save_embedding(key, embedding, text, model_name)
            
            # Periodically save cache index
            if self.stats["size"] % 10 == 0:
                self._save_cache_index()

    def clear(self):
        """Clear the cache."""
        with self.lock:
            self.cache = {}
            self.access_times = {}
            self.stats = {
                "hits": 0,
                "misses": 0,
                "size": 0,
                "evictions": 0
            }
            
            # Save empty cache index
            self._save_cache_index()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            dict: Cache statistics
        """
        with self.lock:
            stats = self.stats.copy()
            stats["hit_ratio"] = stats["hits"] / (stats["hits"] + stats["misses"]) if (stats["hits"] + stats["misses"]) > 0 else 0
            return stats

# Create a singleton instance
embedding_cache = EmbeddingCache()
