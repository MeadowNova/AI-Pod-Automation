from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SEORecommendation(BaseModel):
    category: str
    score: int
    feedback: str


class ListingOptimizationRequest(BaseModel):
    listing_id: str
    current_title: Optional[str] = None
    current_tags: Optional[List[str]] = None
    current_description: Optional[str] = None


class ListingOptimizationResponse(BaseModel):
    listing_id: Optional[str] = None
    optimized_title: Optional[str] = None
    optimized_tags: Optional[List[str]] = None
    optimized_description: Optional[str] = None
    seo_score: int = Field(..., ge=0, le=100)
    recommendations: List[SEORecommendation] = []


class BatchListingOptimizationRequest(BaseModel):
    listings: List[Dict[str, Any]] = Field(..., description="List of listings to optimize")
    max_listings: Optional[int] = Field(None, description="Maximum number of listings to process")


class BatchListingOptimizationResponse(BaseModel):
    results: List[ListingOptimizationResponse]
    processed_count: int
    total_count: int
    cache_stats: Optional[Dict[str, Any]] = None
