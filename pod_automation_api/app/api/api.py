from fastapi import APIRouter

from app.api.endpoints import auth, etsy, seo

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(etsy.router, prefix="/etsy", tags=["etsy"])
api_router.include_router(seo.router, prefix="/seo", tags=["seo"])
