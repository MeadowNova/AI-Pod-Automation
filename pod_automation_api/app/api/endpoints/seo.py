from typing import Any, List
import time
import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.security import get_current_user
from app.schemas.seo import (
    ListingOptimizationRequest,
    ListingOptimizationResponse,
    BatchListingOptimizationRequest,
    BatchListingOptimizationResponse
)
from app.adapters.seo_adapter import seo_service
from app.adapters.etsy_adapter import etsy_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/optimize-listing", response_model=ListingOptimizationResponse)
async def optimize_etsy_listing(
    request: ListingOptimizationRequest,
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Optimize an Etsy listing's SEO using AI.

    This endpoint analyzes the current listing content and provides AI-generated
    optimizations for title, tags, and description to improve SEO performance.
    """
    start_time = time.time()
    logger.info(f"Starting SEO optimization for listing {request.listing_id} by user {current_user}")

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

        processing_time = time.time() - start_time
        logger.info(f"SEO optimization completed for listing {request.listing_id} in {processing_time:.2f}s")

        return optimization_result
    except RuntimeError as e:
        logger.error(f"Runtime error optimizing listing {request.listing_id}: {str(e)}")
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


@router.post("/optimize-listings-batch", response_model=BatchListingOptimizationResponse)
async def optimize_etsy_listings_batch(
    request: BatchListingOptimizationRequest,
    current_user: str = Depends(get_current_user)
) -> Any:
    """
    Optimize multiple Etsy listings in a batch using AI.

    This endpoint processes multiple listings at once, which is more efficient
    than optimizing them one by one. It uses clustering to group similar listings
    and processes them in parallel.
    """
    try:
        # Validate the request
        if not request.listings:
            raise ValueError("No listings provided for optimization")

        # Get the maximum number of listings to process
        max_listings = request.max_listings

        # Optimize listings in batch
        optimized_listings = await seo_service.optimize_listings_batch(
            user_id=current_user,
            listings=request.listings,
            max_listings=max_listings
        )

        # Get cache statistics
        cache_stats = seo_service.optimizer.ollama.get_cache_stats() if hasattr(seo_service, 'optimizer') else None

        # Create response
        response = BatchListingOptimizationResponse(
            results=optimized_listings,
            processed_count=len(optimized_listings),
            total_count=len(request.listings),
            cache_stats=cache_stats
        )

        return response
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
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
