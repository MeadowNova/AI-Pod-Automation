from typing import List, Optional
from datetime import datetime
from uuid import UUID
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


class EtsyCredentialsBase(BaseModel):
    api_key: str
    api_secret: str
    shop_id: Optional[str] = None


class EtsyCredentialsCreate(EtsyCredentialsBase):
    pass


class EtsyCredentialsUpdate(BaseModel):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    shop_id: Optional[str] = None
    token_expiry: Optional[str] = None


class EtsyCredentials(EtsyCredentialsBase):
    user_id: UUID
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expiry: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class EtsyAuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_expiry: str
    shop_id: Optional[str] = None


class EtsyConnectionStatus(BaseModel):
    connected: bool
    shop_name: Optional[str] = None
    shop_id: Optional[str] = None
    message: Optional[str] = None
