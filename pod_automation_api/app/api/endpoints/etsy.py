from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.security import get_current_user
from app.schemas.etsy import EtsyListing, EtsyListingPagination
from app.services.etsy_service import get_etsy_listings

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
        listings = await get_etsy_listings(
            user_id=current_user,
            status=status,
            page=page,
            limit=limit
        )
        return listings
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
