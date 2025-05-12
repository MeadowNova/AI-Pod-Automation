from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status, Request

from app.core.security import get_current_user
from app.schemas.etsy import (
    EtsyListing,
    EtsyListingPagination,
    EtsyCredentialsCreate,
    EtsyCredentialsUpdate,
    EtsyAuthResponse,
    EtsyConnectionStatus
)
from app.adapters.etsy_adapter import etsy_service

router = APIRouter()


@router.get("/test-listings", response_model=EtsyListingPagination)
async def test_etsy_listings(
    status: Optional[str] = Query(None, description="Filter by listing status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page")
) -> Any:
    """
    Test endpoint to retrieve Etsy listings without authentication.
    Uses the hardcoded admin user ID.
    """
    try:
        admin_user_id = "1433b2f4-e878-40cf-ad30-f6fb9dba2fb0"
        listings = await etsy_service.get_listings(
            user_id=admin_user_id,
            status=status,
            page=page,
            limit=limit
        )
        return listings
    except RuntimeError as e:
        raise HTTPException(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/test-listings/{listing_id}", response_model=EtsyListing)
async def test_etsy_listing(
    listing_id: str
) -> Any:
    """
    Test endpoint to retrieve a specific Etsy listing without authentication.
    Uses the hardcoded admin user ID.
    """
    try:
        admin_user_id = "1433b2f4-e878-40cf-ad30-f6fb9dba2fb0"
        listing = await etsy_service.get_listing(
            user_id=admin_user_id,
            listing_id=listing_id
        )
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Listing with ID {listing_id} not found"
            )
        return listing
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/listings", response_model=EtsyListingPagination)
async def read_etsy_listings(
    status: Optional[str] = Query(None, description="Filter listings by status"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Number of items per page"),
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Retrieve Etsy listings for the current user.
    """
    try:
        listings = await etsy_service.get_listings(
            user_id=current_user,
            status=status,
            page=page,
            limit=limit
        )
        return listings
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/listings/{listing_id}", response_model=EtsyListing)
async def read_etsy_listing(
    listing_id: str,
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Retrieve a specific Etsy listing.
    """
    try:
        listing = await etsy_service.get_listing(
            user_id=current_user,
            listing_id=listing_id
        )
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Listing with ID {listing_id} not found"
            )
        return listing
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/status", response_model=EtsyConnectionStatus)
async def get_etsy_connection_status(
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Get Etsy connection status for the current user.
    """
    try:
        return await etsy_service.get_connection_status(user_id=current_user)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/connect", response_model=str)
async def connect_etsy_account(
    credentials: EtsyCredentialsCreate,
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Connect an Etsy account by storing API credentials and initiating OAuth flow.

    Returns the OAuth authorization URL that the user should visit to authorize the app.
    """
    try:
        auth_url = await etsy_service.connect_etsy_account(
            user_id=current_user,
            credentials=credentials
        )
        return auth_url
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/callback", response_model=EtsyAuthResponse)
async def handle_etsy_oauth_callback(
    request: Request,
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Handle OAuth callback from Etsy.

    This endpoint is called by the browser after the user authorizes the app on Etsy.
    """
    try:
        # Get code from query parameters
        params = dict(request.query_params)
        code = params.get("code")
        state = params.get("state")

        if not code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Authorization code not provided"
            )

        # Verify state matches user ID
        if state != current_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid state parameter"
            )

        # Handle OAuth callback
        return await etsy_service.handle_oauth_callback(
            user_id=current_user,
            code=code
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.delete("/disconnect", response_model=bool)
async def disconnect_etsy_account(
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Disconnect an Etsy account by deleting credentials.
    """
    try:
        return await etsy_service.disconnect_etsy_account(user_id=current_user)
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
