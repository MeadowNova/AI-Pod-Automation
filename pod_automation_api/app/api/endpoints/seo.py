from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.schemas.seo import ListingOptimizationRequest, ListingOptimizationResponse
from app.services.seo_service import optimize_listing

router = APIRouter()


@router.post("/optimize-listing", response_model=ListingOptimizationResponse)
async def optimize_etsy_listing(
    request: ListingOptimizationRequest,
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Optimize an Etsy listing's SEO using AI.
    """
    try:
        optimization_result = await optimize_listing(
            user_id=current_user,
            listing_id=request.listing_id,
            current_title=request.current_title,
            current_tags=request.current_tags,
            current_description=request.current_description
        )
        return optimization_result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
