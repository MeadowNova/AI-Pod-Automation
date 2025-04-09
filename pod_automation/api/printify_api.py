"""
Printify API client for POD Automation System.
Handles authentication and API calls to Printify.
"""

import requests
import logging
import time
from pod_automation.config import get_config

logger = logging.getLogger(__name__)

class PrintifyAPI:
    """Client for interacting with the Printify API."""
    
    BASE_URL = "https://api.printify.com/v1"
    
    def __init__(self, api_key=None, shop_id=None):
        """Initialize Printify API client.
        
        Args:
            api_key (str, optional): Printify API key. If not provided, will be loaded from config.
            shop_id (str, optional): Printify shop ID. If not provided, will be loaded from config.
        """
        config = get_config()
        self.api_key = api_key or config.get("api.printify.api_key")
        self.shop_id = shop_id or config.get("api.printify.shop_id")
        
        if not self.api_key:
            logger.warning("Printify API key not set. Please set it in the configuration.")
        
        if not self.shop_id:
            logger.warning("Printify shop ID not set. Please set it in the configuration.")
    
    def _get_headers(self):
        """Get headers for API requests.
        
        Returns:
            dict: Headers for API requests
        """
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def _make_request(self, method, endpoint, params=None, data=None, retry_count=0):
        """Make a request to the Printify API.
        
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
            logger.error(f"Error making request to Printify API: {str(e)}")
            if retry_count < 3:
                logger.info(f"Retrying request ({retry_count + 1}/3)...")
                time.sleep(2 ** retry_count)  # Exponential backoff
                return self._make_request(method, endpoint, params, data, retry_count + 1)
            raise Exception(f"Failed to make request to Printify API after retries: {str(e)}")
    
    def validate_connection(self):
        """Validate API connection by fetching shop information.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            self.get_shop()
            return True
        except Exception as e:
            logger.error(f"Failed to validate Printify API connection: {str(e)}")
            return False
    
    def get_shop(self):
        """Get shop information.
        
        Returns:
            dict: Shop information
        """
        return self._make_request("GET", f"/shops/{self.shop_id}")
    
    def get_catalog(self, page=1, limit=100):
        """Get catalog of available products.
        
        Args:
            page (int, optional): Page number
            limit (int, optional): Number of items per page
            
        Returns:
            dict: Catalog information
        """
        params = {
            "page": page,
            "limit": limit
        }
        return self._make_request("GET", "/catalog/blueprints", params=params)
    
    def get_blueprint(self, blueprint_id):
        """Get blueprint information.
        
        Args:
            blueprint_id (str): Blueprint ID
            
        Returns:
            dict: Blueprint information
        """
        return self._make_request("GET", f"/catalog/blueprints/{blueprint_id}")
    
    def get_blueprint_variants(self, blueprint_id, provider_id):
        """Get blueprint variants.
        
        Args:
            blueprint_id (str): Blueprint ID
            provider_id (int): Provider ID
            
        Returns:
            dict: Blueprint variants
        """
        return self._make_request(
            "GET", 
            f"/catalog/blueprints/{blueprint_id}/providers/{provider_id}/variants"
        )
    
    def get_print_providers(self, blueprint_id):
        """Get print providers for a blueprint.
        
        Args:
            blueprint_id (str): Blueprint ID
            
        Returns:
            dict: Print providers
        """
        return self._make_request("GET", f"/catalog/blueprints/{blueprint_id}/print_providers")
    
    def get_products(self, page=1, limit=100):
        """Get products in the shop.
        
        Args:
            page (int, optional): Page number
            limit (int, optional): Number of items per page
            
        Returns:
            dict: Products information
        """
        params = {
            "page": page,
            "limit": limit
        }
        return self._make_request("GET", f"/shops/{self.shop_id}/products.json", params=params)
    
    def get_product(self, product_id):
        """Get product information.
        
        Args:
            product_id (str): Product ID
            
        Returns:
            dict: Product information
        """
        return self._make_request("GET", f"/shops/{self.shop_id}/products/{product_id}.json")
    
    def create_product(self, product_data):
        """Create a new product.
        
        Args:
            product_data (dict): Product data
            
        Returns:
            dict: Created product information
        """
        return self._make_request("POST", f"/shops/{self.shop_id}/products.json", data=product_data)
    
    def update_product(self, product_id, product_data):
        """Update a product.
        
        Args:
            product_id (str): Product ID
            product_data (dict): Product data
            
        Returns:
            dict: Updated product information
        """
        return self._make_request(
            "PUT", 
            f"/shops/{self.shop_id}/products/{product_id}.json", 
            data=product_data
        )
    
    def delete_product(self, product_id):
        """Delete a product.
        
        Args:
            product_id (str): Product ID
            
        Returns:
            dict: Response data
        """
        return self._make_request("DELETE", f"/shops/{self.shop_id}/products/{product_id}.json")
    
    def publish_product(self, product_id, external=False):
        """Publish a product.
        
        Args:
            product_id (str): Product ID
            external (bool, optional): Whether to publish to external channel
            
        Returns:
            dict: Response data
        """
        data = {"external": external}
        return self._make_request(
            "POST", 
            f"/shops/{self.shop_id}/products/{product_id}/publish.json", 
            data=data
        )
    
    def unpublish_product(self, product_id):
        """Unpublish a product.
        
        Args:
            product_id (str): Product ID
            
        Returns:
            dict: Response data
        """
        return self._make_request(
            "POST", 
            f"/shops/{self.shop_id}/products/{product_id}/unpublish.json"
        )
    
    def get_publishing_status(self, product_id):
        """Get publishing status of a product.
        
        Args:
            product_id (str): Product ID
            
        Returns:
            dict: Publishing status
        """
        return self._make_request(
            "GET", 
            f"/shops/{self.shop_id}/products/{product_id}/publishing_status.json"
        )
    
    def upload_image(self, image_data):
        """Upload an image to Printify.
        
        Args:
            image_data (dict): Image data with file_name and contents (base64)
            
        Returns:
            dict: Uploaded image information
        """
        return self._make_request("POST", "/uploads/images.json", data=image_data)
    
    def get_orders(self, page=1, limit=100):
        """Get orders from the shop.
        
        Args:
            page (int, optional): Page number
            limit (int, optional): Number of items per page
            
        Returns:
            dict: Orders information
        """
        params = {
            "page": page,
            "limit": limit
        }
        return self._make_request("GET", f"/shops/{self.shop_id}/orders.json", params=params)
    
    def get_order(self, order_id):
        """Get order information.
        
        Args:
            order_id (str): Order ID
            
        Returns:
            dict: Order information
        """
        return self._make_request("GET", f"/shops/{self.shop_id}/orders/{order_id}.json")
    
    def calculate_shipping(self, product_id, variant_id, address_data):
        """Calculate shipping cost for a product.
        
        Args:
            product_id (str): Product ID
            variant_id (int): Variant ID
            address_data (dict): Shipping address data
            
        Returns:
            dict: Shipping cost information
        """
        data = {
            "product_id": product_id,
            "variant_id": variant_id,
            "address_to": address_data
        }
        return self._make_request(
            "POST", 
            f"/shops/{self.shop_id}/orders/shipping.json", 
            data=data
        )
