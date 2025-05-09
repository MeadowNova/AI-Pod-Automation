from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user
from app.schemas.etsy import EtsyListing, EtsyListingPagination
from app.adapters.etsy_adapter import etsy_service

router = APIRouter()


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
