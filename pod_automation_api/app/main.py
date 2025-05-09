from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import yaml
import json

from app.api.api import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix=settings.API_V1_STR)


def custom_openapi():
    """
    Load the OpenAPI schema from the YAML file instead of generating it dynamically.
    This ensures the contract is the source of truth, not the code.
    """
    if app.openapi_schema:
        return app.openapi_schema
    
    try:
        with open("openapi.yaml", "r") as f:
            openapi_schema = yaml.safe_load(f)
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    except Exception as e:
        # Fall back to auto-generated schema if file can't be loaded
        print(f"Error loading OpenAPI schema from file: {e}")
        openapi_schema = get_openapi(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            description=settings.DESCRIPTION,
            routes=app.routes,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
def read_root():
    return {"message": "Welcome to POD AI Automation API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
