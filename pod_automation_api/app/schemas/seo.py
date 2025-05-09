from typing import List, Optional
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
    optimized_title: Optional[str] = None
    optimized_tags: Optional[List[str]] = None
    optimized_description: Optional[str] = None
    seo_score: int = Field(..., ge=0, le=100)
    recommendations: List[SEORecommendation] = []
