"""
Etsy API client for POD Automation System.
Handles authentication and API calls to Etsy API v3.
"""

import requests
import logging
import time
import webbrowser
import http.server
import socketserver
import urllib.parse
import json
import threading
from pod_automation.config import get_config

logger = logging.getLogger(__name__)

class EtsyAPI:
    """Client for interacting with the Etsy API v3."""
    
    BASE_URL = "https://api.etsy.com/v3"
    
    def __init__(self, api_key=None, api_secret=None, access_token=None, refresh_token=None, shop_id=None):
        """Initialize Etsy API client.
        
        Args:
            api_key (str, optional): Etsy API key. If not provided, will be loaded from config.
            api_secret (str, optional): Etsy API secret. If not provided, will be loaded from config.
            access_token (str, optional): Etsy access token. If not provided, will be loaded from config.
            refresh_token (str, optional): Etsy refresh token. If not provided, will be loaded from config.
            shop_id (str, optional): Etsy shop ID. If not provided, will be loaded from config.
        """
        config = get_config()
        self.api_key = api_key or config.get("api.etsy.api_key")
        self.api_secret = api_secret or config.get("api.etsy.api_secret")
        self.access_token = access_token or config.get("api.etsy.access_token")
        self.refresh_token = refresh_token or config.get("api.etsy.refresh_token")
        self.shop_id = shop_id or config.get("api.etsy.shop_id")
        self.token_expiry = config.get("api.etsy.token_expiry", 0)
        
        if not self.api_key:
            logger.warning("Etsy API key not set. Please set it in the configuration.")
        
        if not self.shop_id:
            logger.warning("Etsy shop ID not set. Please set it in the configuration.")
    
    def _get_headers(self):
        """Get headers for API requests.
        
        Returns:
            dict: Headers for API requests
        """
        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        
        return headers
    
    def _refresh_token_if_needed(self):
        """Refresh access token if it's expired.
        
        Returns:
            bool: True if token was refreshed or is valid, False otherwise
        """
        current_time = time.time()
        
        # Check if token is expired or about to expire (within 5 minutes)
        if self.token_expiry and current_time >= (self.token_expiry - 300):
            logger.info("Access token expired or about to expire. Refreshing...")
            return self._refresh_token()
        
        return True
    
    def _refresh_token(self):
        """Refresh access token using refresh token.
        
        Returns:
            bool: True if token was refreshed successfully, False otherwise
        """
        if not self.refresh_token:
            logger.error("No refresh token available. Cannot refresh access token.")
            return False
        
        url = "https://api.etsy.com/v3/public/oauth/token"
        data = {
            "grant_type": "refresh_token",
            "client_id": self.api_key,
            "refresh_token": self.refresh_token
        }
        
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                self.token_expiry = time.time() + token_data.get("expires_in", 3600)
                
                # Update config
                config = get_config()
                config.set("api.etsy.access_token", self.access_token)
                config.set("api.etsy.refresh_token", self.refresh_token)
                config.set("api.etsy.token_expiry", self.token_expiry)
                config.save_config()
                
                logger.info("Access token refreshed successfully.")
                return True
            else:
                logger.error(f"Failed to refresh access token: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Exception refreshing access token: {str(e)}")
            return False
    
    def _make_request(self, method, endpoint, params=None, data=None, retry_count=0):
        """Make a request to the Etsy API.
        
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
        # Refresh token if needed
        if not self._refresh_token_if_needed():
            raise Exception("Failed to refresh access token. Authentication required.")
        
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
            
            # Handle token expiration
            if response.status_code == 401 and retry_count < 1:
                logger.warning("Unauthorized. Refreshing token and retrying.")
                if self._refresh_token():
                    return self._make_request(method, endpoint, params, data, retry_count + 1)
            
            # Raise for other error status codes
            response.raise_for_status()
            
            # Return JSON response if available
            if response.text:
                return response.json()
            return {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making request to Etsy API: {str(e)}")
            if retry_count < 3:
                logger.info(f"Retrying request ({retry_count + 1}/3)...")
                time.sleep(2 ** retry_count)  # Exponential backoff
                return self._make_request(method, endpoint, params, data, retry_count + 1)
            raise Exception(f"Failed to make request to Etsy API after retries: {str(e)}")
    
    def start_oauth_flow(self, redirect_uri="http://localhost:3000/oauth/redirect", scopes="listings_r listings_w"):
        """Start the OAuth flow to authenticate with Etsy.
        
        Args:
            redirect_uri (str, optional): Redirect URI for OAuth flow
            scopes (str, optional): Space-separated list of scopes
            
        Returns:
            bool: True if authentication was successful, False otherwise
        """
        if not self.api_key or not self.api_secret:
            logger.error("API key and secret must be set before starting OAuth flow.")
            return False
        
        # Generate authorization URL
        auth_url = f"https://www.etsy.com/oauth/connect?response_type=code&client_id={self.api_key}&redirect_uri={redirect_uri}&scope={scopes}&state=random_state"
        
        # Set up local server to handle redirect
        server_thread = threading.Thread(target=self._run_oauth_server, args=(redirect_uri,))
        server_thread.daemon = True
        server_thread.start()
        
        # Open browser
        logger.info(f"Opening browser to authorize application...")
        logger.info(f"If the browser doesn't open automatically, please visit this URL:\n{auth_url}")
        webbrowser.open(auth_url)
        
        # Wait for server thread to complete
        server_thread.join(timeout=300)  # Wait up to 5 minutes
        
        # Check if we got a token
        if self.access_token:
            logger.info("Authentication successful.")
            return True
        else:
            logger.error("Authentication failed or timed out.")
            return False
    
    def _run_oauth_server(self, redirect_uri):
        """Run a local server to handle OAuth redirect.
        
        Args:
            redirect_uri (str): Redirect URI for OAuth flow
        """
        parsed_uri = urllib.parse.urlparse(redirect_uri)
        host = parsed_uri.hostname
        port = parsed_uri.port
        
        class OAuthHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self2, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self2.etsy_api = self
            
            def do_GET(self2):
                if self2.path.startswith('/oauth/redirect'):
                    # Parse query parameters
                    query = urllib.parse.urlparse(self2.path).query
                    params = urllib.parse.parse_qs(query)
                    
                    if 'code' in params:
                        code = params['code'][0]
                        logger.info(f"Authorization code received.")
                        
                        # Exchange code for access token
                        token_data = self2.etsy_api._exchange_code_for_token(code, redirect_uri)
                        
                        if token_data:
                            # Send success response
                            self2.send_response(200)
                            self2.send_header('Content-type', 'text/html')
                            self2.end_headers()
                            self2.wfile.write(b"<html><body><h1>Authentication Successful!</h1><p>You can close this window and return to the application.</p></body></html>")
                        else:
                            # Send error response
                            self2.send_response(500)
                            self2.send_header('Content-type', 'text/html')
                            self2.end_headers()
                            self2.wfile.write(b"<html><body><h1>Authentication Failed</h1><p>Failed to exchange code for token. Please try again.</p></body></html>")
                    else:
                        # Send error response
                        self2.send_response(400)
                        self2.send_header('Content-type', 'text/html')
                        self2.end_headers()
                        self2.wfile.write(b"<html><body><h1>Authentication Failed</h1><p>No authorization code received. Please try again.</p></body></html>")
                else:
                    super().do_GET()
        
        with socketserver.TCPServer((host, port), OAuthHandler) as httpd:
            logger.info(f"Waiting for authorization callback on {host}:{port}...")
            httpd.handle_request()  # Handle one request, then exit
    
    def _exchange_code_for_token(self, code, redirect_uri):
        """Exchange authorization code for access token.
        
        Args:
            code (str): Authorization code
            redirect_uri (str): Redirect URI for OAuth flow
            
        Returns:
            dict: Token data or None if exchange failed
        """
        url = "https://api.etsy.com/v3/public/oauth/token"
        data = {
            "grant_type": "authorization_code",
            "client_id": self.api_key,
            "redirect_uri": redirect_uri,
            "code": code,
            "code_verifier": "random_verifier"  # In a real app, this should be properly generated
        }
        
        try:
            response = requests.post(url, data=data)
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                self.refresh_token = token_data.get("refresh_token")
                self.token_expiry = time.time() + token_data.get("expires_in", 3600)
                
                # Update config
                config = get_config()
                config.set("api.etsy.access_token", self.access_token)
                config.set("api.etsy.refresh_token", self.refresh_token)
                config.set("api.etsy.token_expiry", self.token_expiry)
                config.save_config()
                
                return token_data
            else:
                logger.error(f"Error exchanging code for token: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Exception exchanging code for token: {str(e)}")
            return None
    
    def validate_connection(self):
        """Validate API connection by fetching user information.
        
        Returns:
            bool: True if connection is valid, False otherwise
        """
        try:
            self.get_user()
            return True
        except Exception as e:
            logger.error(f"Failed to validate Etsy API connection: {str(e)}")
            return False
    
    def get_user(self):
        """Get authenticated user information.
        
        Returns:
            dict: User information
        """
        return self._make_request("GET", "/application/users/me")
    
    def get_shop(self):
        """Get shop information.
        
        Returns:
            dict: Shop information
        """
        if not self.shop_id:
            raise ValueError("Shop ID not set. Please set it in the configuration.")
        
        return self._make_request("GET", f"/application/shops/{self.shop_id}")
    
    def get_listings(self, state="active", limit=25, offset=0, includes=None):
        """Get listings from the shop.
        
        Args:
            state (str, optional): Listing state (active, inactive, draft, expired, sold_out)
            limit (int, optional): Number of results to return
            offset (int, optional): Offset for pagination
            includes (list, optional): List of resources to include
            
        Returns:
            dict: Listings information
        """
        if not self.shop_id:
            raise ValueError("Shop ID not set. Please set it in the configuration.")
        
        params = {
            "state": state,
            "limit": limit,
            "offset": offset
        }
        
        if includes:
            params["includes"] = ",".join(includes)
        
        return self._make_request(
            "GET", 
            f"/application/shops/{self.shop_id}/listings",
            params=params
        )
    
    def get_listing(self, listing_id, includes=None):
        """Get listing information.
        
        Args:
            listing_id (int): Listing ID
            includes (list, optional): List of resources to include
            
        Returns:
            dict: Listing information
        """
        params = {}
        
        if includes:
            params["includes"] = ",".join(includes)
        
        return self._make_request(
            "GET", 
            f"/application/listings/{listing_id}",
            params=params
        )
    
    def create_draft_listing(self, listing_data):
        """Create a draft listing.
        
        Args:
            listing_data (dict): Listing data
            
        Returns:
            dict: Created listing information
        """
        if not self.shop_id:
            raise ValueError("Shop ID not set. Please set it in the configuration.")
        
        return self._make_request(
            "POST", 
            f"/application/shops/{self.shop_id}/listings",
            data=listing_data
        )
    
    def update_listing(self, listing_id, listing_data):
        """Update a listing.
        
        Args:
            listing_id (int): Listing ID
            listing_data (dict): Listing data
            
        Returns:
            dict: Updated listing information
        """
        return self._make_request(
            "PUT", 
            f"/application/listings/{listing_id}",
            data=listing_data
        )
    
    def delete_listing(self, listing_id):
        """Delete a listing.
        
        Args:
            listing_id (int): Listing ID
            
        Returns:
            dict: Response data
        """
        return self._make_request("DELETE", f"/application/listings/{listing_id}")
    
    def upload_listing_image(self, listing_id, image_data, rank=None):
        """Upload an image to a listing.
        
        Args:
            listing_id (int): Listing ID
            image_data (dict): Image data with file_name and image (base64)
            rank (int, optional): Image rank
            
        Returns:
            dict: Uploaded image information
        """
        if rank is not None:
            image_data["rank"] = rank
        
        return self._make_request(
            "POST", 
            f"/application/listings/{listing_id}/images",
            data=image_data
        )
    
    def get_listing_images(self, listing_id):
        """Get images for a listing.
        
        Args:
            listing_id (int): Listing ID
            
        Returns:
            dict: Listing images information
        """
        return self._make_request("GET", f"/application/listings/{listing_id}/images")
    
    def update_listing_inventory(self, listing_id, inventory_data):
        """Update listing inventory.
        
        Args:
            listing_id (int): Listing ID
            inventory_data (dict): Inventory data
            
        Returns:
            dict: Updated inventory information
        """
        return self._make_request(
            "PUT", 
            f"/application/listings/{listing_id}/inventory",
            data=inventory_data
        )
    
    def get_listing_inventory(self, listing_id):
        """Get inventory for a listing.
        
        Args:
            listing_id (int): Listing ID
            
        Returns:
            dict: Listing inventory information
        """
        return self._make_request("GET", f"/application/listings/{listing_id}/inventory")
    
    def get_shop_sections(self):
        """Get shop sections.
        
        Returns:
            dict: Shop sections information
        """
        if not self.shop_id:
            raise ValueError("Shop ID not set. Please set it in the configuration.")
        
        return self._make_request("GET", f"/application/shops/{self.shop_id}/sections")
    
    def create_shop_section(self, section_data):
        """Create a shop section.
        
        Args:
            section_data (dict): Section data
            
        Returns:
            dict: Created section information
        """
        if not self.shop_id:
            raise ValueError("Shop ID not set. Please set it in the configuration.")
        
        return self._make_request(
            "POST", 
            f"/application/shops/{self.shop_id}/sections",
            data=section_data
        )
    
    def get_shop_receipts(self, limit=25, offset=0, was_paid=None, was_shipped=None):
        """Get shop receipts.
        
        Args:
            limit (int, optional): Number of results to return
            offset (int, optional): Offset for pagination
            was_paid (bool, optional): Filter by payment status
            was_shipped (bool, optional): Filter by shipping status
            
        Returns:
            dict: Shop receipts information
        """
        if not self.shop_id:
            raise ValueError("Shop ID not set. Please set it in the configuration.")
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        if was_paid is not None:
            params["was_paid"] = was_paid
        
        if was_shipped is not None:
            params["was_shipped"] = was_shipped
        
        return self._make_request(
            "GET", 
            f"/application/shops/{self.shop_id}/receipts",
            params=params
        )
    
    def get_shop_receipt(self, receipt_id):
        """Get receipt information.
        
        Args:
            receipt_id (int): Receipt ID
            
        Returns:
            dict: Receipt information
        """
        if not self.shop_id:
            raise ValueError("Shop ID not set. Please set it in the configuration.")
        
        return self._make_request("GET", f"/application/shops/{self.shop_id}/receipts/{receipt_id}")
    
    def get_shop_transactions(self, limit=25, offset=0):
        """Get shop transactions.
        
        Args:
            limit (int, optional): Number of results to return
            offset (int, optional): Offset for pagination
            
        Returns:
            dict: Shop transactions information
        """
        if not self.shop_id:
            raise ValueError("Shop ID not set. Please set it in the configuration.")
        
        params = {
            "limit": limit,
            "offset": offset
        }
        
        return self._make_request(
            "GET", 
            f"/application/shops/{self.shop_id}/transactions",
            params=params
        )
    
    def get_shop_transaction(self, transaction_id):
        """Get transaction information.
        
        Args:
            transaction_id (int): Transaction ID
            
        Returns:
            dict: Transaction information
        """
        if not self.shop_id:
            raise ValueError("Shop ID not set. Please set it in the configuration.")
        
        return self._make_request("GET", f"/application/shops/{self.shop_id}/transactions/{transaction_id}")
    
    def get_listing_taxonomy(self):
        """Get listing taxonomy.
        
        Returns:
            dict: Listing taxonomy information
        """
        return self._make_request("GET", "/application/seller-taxonomy/nodes")
    
    def get_listing_properties(self, taxonomy_id):
        """Get listing properties for a taxonomy.
        
        Args:
            taxonomy_id (int): Taxonomy ID
            
        Returns:
            dict: Listing properties information
        """
        return self._make_request("GET", f"/application/seller-taxonomy/nodes/{taxonomy_id}/properties")
    
    def get_shop_stats(self, stats_type="views", start_date=None, end_date=None):
        """Get shop stats.
        
        Args:
            stats_type (str, optional): Type of stats (views, visits, transactions, revenue)
            start_date (str, optional): Start date in YYYY-MM-DD format
            end_date (str, optional): End date in YYYY-MM-DD format
            
        Returns:
            dict: Shop stats information
        """
        if not self.shop_id:
            raise ValueError("Shop ID not set. Please set it in the configuration.")
        
        params = {
            "stats_type": stats_type
        }
        
        if start_date:
            params["start_date"] = start_date
        
        if end_date:
            params["end_date"] = end_date
        
        return self._make_request(
            "GET", 
            f"/application/shops/{self.shop_id}/stats",
            params=params
        )
