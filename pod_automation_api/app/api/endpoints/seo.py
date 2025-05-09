from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.schemas.seo import ListingOptimizationRequest, ListingOptimizationResponse
from app.adapters.seo_adapter import seo_service
from app.adapters.etsy_adapter import etsy_service

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
        # First, check if the listing exists
        listing = await etsy_service.get_listing(
            user_id=current_user,
            listing_id=request.listing_id
        )

        if not listing and not all([request.current_title, request.current_tags]):
            raise ValueError(f"Listing with ID {request.listing_id} not found and insufficient data provided")

        # Then optimize the listing
        optimization_result = await seo_service.optimize_listing(
            user_id=current_user,
            listing_id=request.listing_id,
            current_title=request.current_title or (listing.title if listing else None),
            current_tags=request.current_tags or (listing.tags if listing else None),
            current_description=request.current_description or (listing.description if listing else None)
        )

        return optimization_result
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
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


@router.get("/dashboard", response_model=dict)
async def get_seo_dashboard(
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Get SEO dashboard data for the current user.

    This is a composite endpoint that aggregates data from multiple services
    to provide a complete dashboard view for the frontend.
    """
    try:
        # Get listings with their SEO scores
        listings_response = await etsy_service.get_listings(
            user_id=current_user,
            limit=10  # Limit to 10 most recent listings
        )

        # Calculate overall SEO score
        total_score = 0
        listings_with_score = 0

        for listing in listings_response.data:
            if listing.seo_score is not None:
                total_score += listing.seo_score
                listings_with_score += 1

        avg_score = total_score // listings_with_score if listings_with_score > 0 else 0

        # Create dashboard data
        dashboard_data = {
            "overall_seo_score": avg_score,
            "listings_optimized": listings_with_score,
            "total_listings": len(listings_response.data),
            "recent_listings": [
                {
                    "id": listing.id,
                    "title": listing.title,
                    "seo_score": listing.seo_score,
                    "thumbnail_url": listing.thumbnail_url
                }
                for listing in listings_response.data[:5]  # Show 5 most recent
            ],
            "optimization_recommendations": [
                "Use all 13 available tags for each listing",
                "Ensure titles are 120-140 characters long",
                "Include relevant keywords in the first 40 characters of titles"
            ]
        }

        return dashboard_data
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
