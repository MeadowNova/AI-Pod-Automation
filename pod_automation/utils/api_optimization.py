"""
Utility functions for API performance optimization.
Handles caching, rate limiting, and other performance enhancements.
"""

import time
import logging
import functools
import json
import os
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class APICache:
    """Cache for API responses to reduce API calls and improve performance."""
    
    def __init__(self, cache_dir="cache", ttl=3600):
        """Initialize API cache.
        
        Args:
            cache_dir (str): Directory to store cache files
            ttl (int): Time to live in seconds for cache entries
        """
        self.cache_dir = cache_dir
        self.ttl = ttl
        
        # Create cache directory if it doesn't exist
        os.makedirs(cache_dir, exist_ok=True)
    
    def get(self, key):
        """Get value from cache.
        
        Args:
            key (str): Cache key
            
        Returns:
            dict: Cached value or None if not found or expired
        """
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        try:
            if not os.path.exists(cache_file):
                return None
            
            # Check if cache entry is expired
            modified_time = os.path.getmtime(cache_file)
            if time.time() - modified_time > self.ttl:
                logger.debug(f"Cache entry expired: {key}")
                return None
            
            # Read cache entry
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Error reading cache entry: {str(e)}")
            return None
    
    def set(self, key, value):
        """Set value in cache.
        
        Args:
            key (str): Cache key
            value (dict): Value to cache
        """
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(value, f)
        except Exception as e:
            logger.warning(f"Error writing cache entry: {str(e)}")
    
    def clear(self, key=None):
        """Clear cache entries.
        
        Args:
            key (str, optional): Specific key to clear, or all entries if None
        """
        if key:
            cache_file = os.path.join(self.cache_dir, f"{key}.json")
            if os.path.exists(cache_file):
                os.remove(cache_file)
        else:
            for file in os.listdir(self.cache_dir):
                if file.endswith(".json"):
                    os.remove(os.path.join(self.cache_dir, file))

def cache_api_response(ttl=3600):
    """Decorator to cache API responses.
    
    Args:
        ttl (int): Time to live in seconds for cache entries
        
    Returns:
        function: Decorated function
    """
    cache = APICache(ttl=ttl)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key = f"{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            # Check cache
            cached_value = cache.get(key)
            if cached_value is not None:
                logger.debug(f"Cache hit: {key}")
                return cached_value
            
            # Call function
            result = func(*args, **kwargs)
            
            # Cache result
            cache.set(key, result)
            
            return result
        return wrapper
    return decorator

class RateLimiter:
    """Rate limiter to prevent API rate limit errors."""
    
    def __init__(self, calls_per_minute=60):
        """Initialize rate limiter.
        
        Args:
            calls_per_minute (int): Maximum number of calls per minute
        """
        self.calls_per_minute = calls_per_minute
        self.call_times = []
    
    def wait_if_needed(self):
        """Wait if rate limit is reached.
        
        Returns:
            float: Time waited in seconds
        """
        now = time.time()
        
        # Remove old call times
        self.call_times = [t for t in self.call_times if now - t < 60]
        
        # Check if rate limit is reached
        if len(self.call_times) >= self.calls_per_minute:
            # Calculate wait time
            oldest_call = min(self.call_times)
            wait_time = 60 - (now - oldest_call)
            
            if wait_time > 0:
                logger.debug(f"Rate limit reached. Waiting {wait_time:.2f} seconds.")
                time.sleep(wait_time)
                return wait_time
        
        # Add current call time
        self.call_times.append(time.time())
        return 0

def rate_limit(calls_per_minute=60):
    """Decorator to rate limit API calls.
    
    Args:
        calls_per_minute (int): Maximum number of calls per minute
        
    Returns:
        function: Decorated function
    """
    limiter = RateLimiter(calls_per_minute)
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait_if_needed()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def retry_on_failure(max_retries=3, retry_delay=1, backoff_factor=2):
    """Decorator to retry function on failure.
    
    Args:
        max_retries (int): Maximum number of retries
        retry_delay (float): Initial delay between retries in seconds
        backoff_factor (float): Factor to increase delay between retries
        
    Returns:
        function: Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        raise
                    
                    delay = retry_delay * (backoff_factor ** (retries - 1))
                    logger.warning(f"Retry {retries}/{max_retries} after error: {str(e)}. Waiting {delay:.2f} seconds.")
                    time.sleep(delay)
        return wrapper
    return decorator

def batch_process(batch_size=10, delay_between_batches=1):
    """Decorator to process items in batches.
    
    Args:
        batch_size (int): Number of items to process in each batch
        delay_between_batches (float): Delay between batches in seconds
        
    Returns:
        function: Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(items, *args, **kwargs):
            results = []
            for i in range(0, len(items), batch_size):
                batch = items[i:i+batch_size]
                batch_results = func(batch, *args, **kwargs)
                results.extend(batch_results)
                
                if i + batch_size < len(items):
                    logger.debug(f"Processed batch {i//batch_size + 1}/{(len(items)-1)//batch_size + 1}. Waiting {delay_between_batches} seconds.")
                    time.sleep(delay_between_batches)
            
            return results
        return wrapper
    return decorator

def optimize_api_client(api_client, cache_ttl=3600, rate_limit_calls=60, max_retries=3):
    """Optimize API client with caching, rate limiting, and retries.
    
    Args:
        api_client: API client instance
        cache_ttl (int): Time to live in seconds for cache entries
        rate_limit_calls (int): Maximum number of calls per minute
        max_retries (int): Maximum number of retries on failure
        
    Returns:
        object: Optimized API client
    """
    # Find all methods that make API requests
    for attr_name in dir(api_client):
        if attr_name.startswith('_') or not callable(getattr(api_client, attr_name)):
            continue
        
        attr = getattr(api_client, attr_name)
        
        # Skip methods that don't make API requests
        if attr_name in ['__init__', 'validate_connection']:
            continue
        
        # Apply decorators
        decorated_attr = retry_on_failure(max_retries=max_retries)(attr)
        decorated_attr = rate_limit(calls_per_minute=rate_limit_calls)(decorated_attr)
        
        # Apply caching only to GET methods
        if attr_name.startswith('get_'):
            decorated_attr = cache_api_response(ttl=cache_ttl)(decorated_attr)
        
        # Replace original method with decorated method
        setattr(api_client, attr_name, decorated_attr)
    
    return api_client
