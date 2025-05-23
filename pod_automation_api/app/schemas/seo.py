from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class SEORecommendation(BaseModel):
    category: str
    score: int = Field(..., ge=0, le=100, description="Score from 0-100")
    feedback: str
    improvement_suggestion: Optional[str] = None
    priority: str = Field(default="medium", description="Priority level: low, medium, high")

    @validator('category')
    def validate_category(cls, v):
        allowed_categories = ['title', 'tags', 'description', 'overall']
        if v not in allowed_categories:
            raise ValueError(f'Category must be one of: {allowed_categories}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        allowed_priorities = ['low', 'medium', 'high']
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {allowed_priorities}')
        return v


class ListingOptimizationRequest(BaseModel):
    listing_id: str
    current_title: Optional[str] = None
    current_tags: Optional[List[str]] = None
    current_description: Optional[str] = None


class ListingOptimizationResponse(BaseModel):
    listing_id: Optional[str] = None
    original_title: Optional[str] = None
    original_tags: Optional[List[str]] = None
    original_description: Optional[str] = None
    optimized_title: Optional[str] = None
    optimized_tags: Optional[List[str]] = None
    optimized_description: Optional[str] = None
    seo_score: int = Field(..., ge=0, le=100, description="Overall SEO score")
    original_seo_score: Optional[int] = Field(None, ge=0, le=100, description="Original SEO score before optimization")
    improvement_percentage: Optional[float] = Field(None, description="Percentage improvement in SEO score")
    recommendations: List[SEORecommendation] = []
    processing_time_ms: Optional[int] = Field(None, description="Time taken to process optimization in milliseconds")

    @validator('optimized_tags')
    def validate_tags_count(cls, v):
        if v and len(v) > 13:
            raise ValueError('Etsy allows maximum 13 tags per listing')
        return v

    @validator('optimized_tags')
    def validate_tag_length(cls, v):
        if v:
            for tag in v:
                if len(tag) > 20:
                    raise ValueError(f'Tag "{tag}" exceeds 20 character limit')
        return v


class BatchListingOptimizationRequest(BaseModel):
    listings: List[Dict[str, Any]] = Field(..., description="List of listings to optimize")
    max_listings: Optional[int] = Field(None, description="Maximum number of listings to process")


class BatchListingOptimizationResponse(BaseModel):
    results: List[ListingOptimizationResponse]
    processed_count: int
    total_count: int
    cache_stats: Optional[Dict[str, Any]] = None
