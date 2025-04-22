"""
Base API client for POD Automation System.
Provides common functionality for all API clients.
"""

import requests
import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class BaseAPIClient:
    """Base class for API clients."""
    
    BASE_URL = ""
    
    def __init__(self, api_key: str = None):
        """Initialize base API client.
        
        Args:
            api_key (str, optional): API key for authentication
        """
        self.api_key = api_key
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests.
        
        Returns:
            dict: Headers for API requests
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, 
                     data: Optional[Dict[str, Any]] = None, retry_count: int = 0) -> Dict[str, Any]:
        """Make a request to the API.
        
        Args:
            method (str): HTTP method (GET, POST, PUT, DELETE)
            endpoint (str): API endpoint
            params (dict, optional): Query parameters
            data (dict, optional): Request body
            retry_count (int, optional): Number of retries attempted
            
        Returns:
            dict: Response data
            
        Raises:
            Exception: If API request fails after retries
        """
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data
            )
            
            # Handle rate limiting
            if response.status_code == 429 and retry_count < 3:
                retry_after = int(response.headers.get("Retry-After", 5))
                logger.warning(f"Rate limited. Retrying after {retry_after} seconds.")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, params, data, retry_count + 1)
            
            # Raise for other error status codes
            response.raise_for_status()
            
            # Return JSON response if available
            if response.text:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to API: {str(e)}")
            if retry_count < 3:
                logger.info(f"Retrying request ({retry_count + 1}/3)...")
                time.sleep(2 ** retry_count)  # Exponential backoff
                return self._make_request(method, endpoint, params, data, retry_count + 1)
            raise Exception(f"Failed to make request to API after retries: {str(e)}")
    
    def validate_connection(self) -> bool:
        """Validate API connection.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        raise NotImplementedError("Subclasses must implement validate_connection method")
