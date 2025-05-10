"""
Adapter for Etsy API services.

This module provides an adapter for connecting the FastAPI BFF layer to the existing
Etsy API integration in the pod_automation system.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone

from supabase import create_client, Client
from fastapi import HTTPException, status

from app.core.config import settings
from app.schemas.etsy import (
    EtsyListing,
    EtsyListingPagination,
    EtsyCredentials,
    EtsyCredentialsCreate,
    EtsyCredentialsUpdate,
    EtsyAuthResponse,
    EtsyConnectionStatus
)

logger = logging.getLogger(__name__)

class EtsyServiceAdapter:
    """Adapter for Etsy API services."""

    def __init__(self):
        """Initialize the Etsy service adapter."""
        try:
            # Import the existing Etsy API client
            from pod_automation.api.etsy_api import EtsyAPI

            # Initialize Supabase client with hardcoded values
            self.supabase_url = "https://pnsfrhjbldbabfaiiyzj.supabase.co"
            self.supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBuc2ZyaGpibGRiYWJmYWlpeXpqIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NjA5OTg4OCwiZXhwIjoyMDYxNjc1ODg4fQ.GuHxnXup01-FMMyCHOjuYogkT3XiAWohhhM-LD5Bv7c"

            logger.info(f"Connecting to Supabase at {self.supabase_url}")
            self.supabase = create_client(self.supabase_url, self.supabase_key)

            # We'll initialize the Etsy API client when needed with user-specific tokens
            self.api_class = EtsyAPI
            self.initialized = True
            logger.info("Etsy service adapter initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import Etsy API: {str(e)}")
            self.initialized = False
        except Exception as e:
            logger.error(f"Failed to initialize Etsy service adapter: {str(e)}")
            self.initialized = False

    async def get_credentials(self, user_id: str) -> Optional[EtsyCredentials]:
        """
        Get Etsy credentials for a user.

        Args:
            user_id: User ID

        Returns:
            Optional[EtsyCredentials]: Etsy credentials or None if not found
        """
        if not self.initialized:
            logger.error("Etsy service adapter not initialized")
            raise RuntimeError("Etsy service not available")

        try:
            # Get credentials from Supabase (using public.etsy_credentials table)
            response = self.supabase.table("etsy_credentials").select("*").eq("user_id", user_id).execute()

            if not response.data or len(response.data) == 0:
                logger.warning(f"No Etsy credentials found for user {user_id}")
                return None

            cred_data = response.data[0]

            # Convert to EtsyCredentials object
            credentials = EtsyCredentials(
                user_id=uuid.UUID(cred_data["user_id"]),
                api_key=cred_data["api_key"],
                api_secret=cred_data["api_secret"],
                access_token=cred_data.get("access_token"),
                refresh_token=cred_data.get("refresh_token"),
                shop_id=cred_data.get("shop_id"),
                token_expiry=cred_data.get("token_expiry"),
                created_at=cred_data["created_at"],
                updated_at=cred_data["updated_at"]
            )

            return credentials

        except Exception as e:
            logger.error(f"Error getting Etsy credentials: {str(e)}")
            raise

    async def create_or_update_credentials(
        self,
        user_id: str,
        credentials: Union[EtsyCredentialsCreate, EtsyCredentialsUpdate]
    ) -> EtsyCredentials:
        """
        Create or update Etsy credentials for a user.

        Args:
            user_id: User ID
            credentials: Etsy credentials to create or update

        Returns:
            EtsyCredentials: Created or updated Etsy credentials
        """
        if not self.initialized:
            logger.error("Etsy service adapter not initialized")
            raise RuntimeError("Etsy service not available")

        try:
            # Check if credentials exist
            existing = await self.get_credentials(user_id)

            # Prepare data
            cred_dict = credentials.dict(exclude_unset=True)
            data = {
                "user_id": user_id,
                **cred_dict
            }

            if existing:
                # Update existing credentials
                response = self.supabase.table("etsy_credentials").update(data).eq("user_id", user_id).execute()
            else:
                # Create new credentials
                response = self.supabase.table("etsy_credentials").insert(data).execute()

            if not response.data or len(response.data) == 0:
                raise RuntimeError("Failed to create or update Etsy credentials")

            # Get the updated credentials
            return await self.get_credentials(user_id)

        except Exception as e:
            logger.error(f"Error creating or updating Etsy credentials: {str(e)}")
            raise

    async def delete_credentials(self, user_id: str) -> bool:
        """
        Delete Etsy credentials for a user.

        Args:
            user_id: User ID

        Returns:
            bool: True if credentials were deleted, False otherwise
        """
        if not self.initialized:
            logger.error("Etsy service adapter not initialized")
            raise RuntimeError("Etsy service not available")

        try:
            # Delete credentials from Supabase
            response = self.supabase.table("etsy_credentials").delete().eq("user_id", user_id).execute()

            return True

        except Exception as e:
            logger.error(f"Error deleting Etsy credentials: {str(e)}")
            raise

    async def get_etsy_client(self, user_id: str):
        """
        Get an initialized Etsy API client for a user.

        Args:
            user_id: User ID

        Returns:
            EtsyAPI: Initialized Etsy API client

        Raises:
            HTTPException: If credentials are not found or invalid
        """
        if not self.initialized:
            logger.error("Etsy service adapter not initialized")
            raise RuntimeError("Etsy service not available")

        # Get credentials
        credentials = await self.get_credentials(user_id)

        if not credentials:
            logger.error(f"No Etsy credentials found for user {user_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Etsy credentials not found. Please connect your Etsy account."
            )

        # Initialize Etsy API client
        etsy_client = self.api_class(
            api_key=credentials.api_key,
            api_secret=credentials.api_secret,
            access_token=credentials.access_token,
            refresh_token=credentials.refresh_token,
            shop_id=credentials.shop_id
        )

        # Check if token is expired and needs refresh
        if credentials.token_expiry:
            now = datetime.now(timezone.utc)
            token_expiry = datetime.fromisoformat(credentials.token_expiry)
            if token_expiry < now:
                logger.info(f"Etsy token expired for user {user_id}, refreshing...")

                # Refresh token
                if not etsy_client._refresh_token():
                    logger.error(f"Failed to refresh Etsy token for user {user_id}")
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Etsy authentication expired. Please reconnect your Etsy account."
                    )

                # Update credentials in database
                token_expiry = datetime.fromtimestamp(etsy_client.token_expiry, timezone.utc)
                # Convert datetime to ISO format string for JSON serialization
                token_expiry_str = token_expiry.isoformat()

                await self.create_or_update_credentials(
                    user_id=user_id,
                    credentials=EtsyCredentialsUpdate(
                        access_token=etsy_client.access_token,
                        refresh_token=etsy_client.refresh_token,
                        token_expiry=token_expiry_str
                    )
                )

        return etsy_client

    async def get_listings(
        self,
        user_id: str,
        status: Optional[str] = None,
        page: int = 1,
        limit: int = 20
    ) -> EtsyListingPagination:
        """
        Get Etsy listings for a user.

        Args:
            user_id: User ID
            status: Filter by listing status
            page: Page number
            limit: Number of items per page

        Returns:
            EtsyListingPagination: Paginated list of Etsy listings
        """
        if not self.initialized:
            logger.error("Etsy service adapter not initialized")
            raise RuntimeError("Etsy service not available")

        try:
            # Get Etsy client for the user
            etsy_client = await self.get_etsy_client(user_id)

            # Map status to Etsy API status
            etsy_status = status
            if status == "all":
                etsy_status = None

            # Calculate offset for pagination
            offset = (page - 1) * limit

            # Get listings from Etsy API
            response = etsy_client.get_listings(
                state=etsy_status,
                limit=limit,
                offset=offset
            )

            # Extract listings from response
            etsy_listings = response.get("results", [])

            # Convert to EtsyListing objects
            listings = []
            for listing in etsy_listings:
                # Extract tags from listing
                tags = []
                if "tags" in listing:
                    tags = listing["tags"]
                elif "tags" in listing.get("tags", []):
                    tags = listing["tags"]

                # Create EtsyListing object
                etsy_listing = EtsyListing(
                    id=str(listing["listing_id"]),
                    title=listing["title"],
                    description=listing.get("description", ""),
                    tags=tags,
                    price=float(listing.get("price", {}).get("amount", 0) / 100) if isinstance(listing.get("price", {}), dict) else 0,
                    status=listing.get("state", "active"),
                    thumbnail_url=listing.get("images", [{}])[0].get("url_570xN", "") if listing.get("images") else "",
                    seo_score=None  # We'll calculate this separately
                )
                listings.append(etsy_listing)

            # Create pagination info
            pagination = {
                "total": response.get("count", 0),
                "page": page,
                "limit": limit,
                "pages": (response.get("count", 0) + limit - 1) // limit if response.get("count", 0) > 0 else 1
            }

            return EtsyListingPagination(data=listings, pagination=pagination)

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error getting Etsy listings: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting Etsy listings: {str(e)}"
            )

    async def get_listing(self, user_id: str, listing_id: str) -> Optional[EtsyListing]:
        """
        Get a specific Etsy listing.

        Args:
            user_id: User ID
            listing_id: Etsy listing ID

        Returns:
            Optional[EtsyListing]: Etsy listing or None if not found
        """
        if not self.initialized:
            logger.error("Etsy service adapter not initialized")
            raise RuntimeError("Etsy service not available")

        try:
            # Get Etsy client for the user
            etsy_client = await self.get_etsy_client(user_id)

            # Get listing from Etsy API
            response = etsy_client.get_listing(listing_id, includes=["Images", "Tags"])

            if not response or "listing" not in response:
                return None

            listing = response["listing"]

            # Extract tags
            tags = []
            if "tags" in listing:
                tags = listing["tags"]
            elif "tags" in response:
                tags = response["tags"]

            # Extract image URL
            thumbnail_url = ""
            if "images" in response and response["images"] and len(response["images"]) > 0:
                thumbnail_url = response["images"][0].get("url_570xN", "")

            # Create EtsyListing object
            etsy_listing = EtsyListing(
                id=str(listing["listing_id"]),
                title=listing["title"],
                description=listing.get("description", ""),
                tags=tags,
                price=float(listing.get("price", {}).get("amount", 0) / 100) if isinstance(listing.get("price", {}), dict) else 0,
                status=listing.get("state", "active"),
                thumbnail_url=thumbnail_url,
                seo_score=None  # We'll calculate this separately
            )

            return etsy_listing

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error getting Etsy listing: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting Etsy listing: {str(e)}"
            )


    async def connect_etsy_account(
        self,
        user_id: str,
        credentials: EtsyCredentialsCreate
    ) -> str:
        """
        Connect an Etsy account by storing API credentials and initiating OAuth flow.

        Args:
            user_id: User ID
            credentials: Etsy API credentials

        Returns:
            str: OAuth authorization URL
        """
        if not self.initialized:
            logger.error("Etsy service adapter not initialized")
            raise RuntimeError("Etsy service not available")

        try:
            # Store credentials in Supabase
            await self.create_or_update_credentials(user_id, credentials)

            # Initialize Etsy API client
            etsy_client = self.api_class(
                api_key=credentials.api_key,
                api_secret=credentials.api_secret,
                shop_id=credentials.shop_id
            )

            # Generate OAuth URL
            redirect_uri = settings.ETSY_REDIRECT_URI
            scopes = "listings_r listings_w listings_d shops_r shops_w transactions_r transactions_w address_r address_w profile_r profile_w email_r feedback_r recommend_r recommend_w"

            # Generate authorization URL
            auth_url = f"https://www.etsy.com/oauth/connect?response_type=code&client_id={credentials.api_key}&redirect_uri={redirect_uri}&scope={scopes}&state={user_id}"

            return auth_url

        except Exception as e:
            logger.error(f"Error connecting Etsy account: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error connecting Etsy account: {str(e)}"
            )

    async def handle_oauth_callback(
        self,
        user_id: str,
        code: str
    ) -> EtsyAuthResponse:
        """
        Handle OAuth callback by exchanging code for tokens.

        Args:
            user_id: User ID
            code: Authorization code

        Returns:
            EtsyAuthResponse: OAuth response with tokens
        """
        if not self.initialized:
            logger.error("Etsy service adapter not initialized")
            raise RuntimeError("Etsy service not available")

        try:
            # Get credentials
            credentials = await self.get_credentials(user_id)

            if not credentials:
                logger.error(f"No Etsy credentials found for user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Etsy credentials not found. Please connect your Etsy account."
                )

            # Initialize Etsy API client
            etsy_client = self.api_class(
                api_key=credentials.api_key,
                api_secret=credentials.api_secret
            )

            # Exchange code for tokens
            redirect_uri = settings.ETSY_REDIRECT_URI
            token_data = etsy_client._exchange_code_for_token(code, redirect_uri)

            if not token_data:
                logger.error(f"Failed to exchange code for token for user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token. Please try again."
                )

            # Update credentials in database
            token_expiry = datetime.fromtimestamp(etsy_client.token_expiry, timezone.utc)
            # Convert datetime to ISO format string for JSON serialization
            token_expiry_str = token_expiry.isoformat()

            await self.create_or_update_credentials(
                user_id=user_id,
                credentials=EtsyCredentialsUpdate(
                    access_token=token_data.get("access_token"),
                    refresh_token=token_data.get("refresh_token"),
                    token_expiry=token_expiry_str
                )
            )

            # Get shop information
            shop_info = None
            shop_id = None
            try:
                shop_info = etsy_client.get_shop()
                if shop_info and "shop_id" in shop_info:
                    shop_id = shop_info["shop_id"]

                    # Update shop ID in credentials
                    await self.create_or_update_credentials(
                        user_id=user_id,
                        credentials=EtsyCredentialsUpdate(
                            shop_id=shop_id
                        )
                    )
            except Exception as e:
                logger.warning(f"Failed to get shop information: {str(e)}")

            # Return auth response
            return EtsyAuthResponse(
                access_token=token_data.get("access_token"),
                refresh_token=token_data.get("refresh_token"),
                token_expiry=token_expiry_str,
                shop_id=shop_id
            )

        except HTTPException:
            # Re-raise HTTP exceptions
            raise
        except Exception as e:
            logger.error(f"Error handling OAuth callback: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error handling OAuth callback: {str(e)}"
            )

    async def disconnect_etsy_account(self, user_id: str) -> bool:
        """
        Disconnect an Etsy account by deleting credentials.

        Args:
            user_id: User ID

        Returns:
            bool: True if account was disconnected, False otherwise
        """
        if not self.initialized:
            logger.error("Etsy service adapter not initialized")
            raise RuntimeError("Etsy service not available")

        try:
            # Delete credentials
            return await self.delete_credentials(user_id)

        except Exception as e:
            logger.error(f"Error disconnecting Etsy account: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error disconnecting Etsy account: {str(e)}"
            )

    async def get_connection_status(self, user_id: str) -> EtsyConnectionStatus:
        """
        Get Etsy connection status for a user.

        Args:
            user_id: User ID

        Returns:
            EtsyConnectionStatus: Connection status
        """
        if not self.initialized:
            logger.error("Etsy service adapter not initialized")
            raise RuntimeError("Etsy service not available")

        try:
            # Get credentials
            credentials = await self.get_credentials(user_id)

            if not credentials or not credentials.access_token:
                return EtsyConnectionStatus(
                    connected=False,
                    message="Not connected to Etsy. Please connect your account."
                )

            # Check if token is expired
            if credentials.token_expiry:
                now = datetime.now(timezone.utc)
                if credentials.token_expiry < now:
                    return EtsyConnectionStatus(
                        connected=False,
                        message="Etsy authentication expired. Please reconnect your account."
                    )

            # Initialize Etsy API client
            etsy_client = self.api_class(
                api_key=credentials.api_key,
                api_secret=credentials.api_secret,
                access_token=credentials.access_token,
                refresh_token=credentials.refresh_token,
                shop_id=credentials.shop_id
            )

            # Validate connection
            if not etsy_client.validate_connection():
                return EtsyConnectionStatus(
                    connected=False,
                    message="Failed to connect to Etsy API. Please check your credentials."
                )

            # Get shop information
            shop_name = None
            shop_id = credentials.shop_id

            try:
                if shop_id:
                    shop_info = etsy_client.get_shop()
                    if shop_info and "shop_name" in shop_info:
                        shop_name = shop_info["shop_name"]
            except Exception as e:
                logger.warning(f"Failed to get shop information: {str(e)}")

            return EtsyConnectionStatus(
                connected=True,
                shop_name=shop_name,
                shop_id=shop_id,
                message="Connected to Etsy"
            )

        except Exception as e:
            logger.error(f"Error getting Etsy connection status: {str(e)}")
            return EtsyConnectionStatus(
                connected=False,
                message=f"Error checking Etsy connection: {str(e)}"
            )


# Create a singleton instance
etsy_service = EtsyServiceAdapter()
