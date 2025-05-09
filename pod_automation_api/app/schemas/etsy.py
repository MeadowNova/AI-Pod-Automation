from typing import List, Optional
from pydantic import BaseModel, Field


class EtsyListing(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    price: Optional[float] = None
    status: Optional[str] = None
    thumbnail_url: Optional[str] = None
    seo_score: Optional[int] = Field(None, ge=0, le=100)


class EtsyListingPagination(BaseModel):
    data: List[EtsyListing]
    pagination: dict
