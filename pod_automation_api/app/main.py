import os
import logging
from pathlib import Path
import yaml
import json

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.api import api_router
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    # Log the CORS origins for debugging
    logger.info(f"Configuring CORS with origins: {settings.CORS_ORIGINS}")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for now to debug
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Add API router
app.include_router(api_router, prefix=settings.API_V1_STR)


def custom_openapi():
    """
    Load the OpenAPI schema from the YAML file instead of generating it dynamically.
    This ensures the contract is the source of truth, not the code.
    """
    if app.openapi_schema:
        return app.openapi_schema

    try:
        # Look for the openapi.yaml file in the current directory and parent directory
        openapi_path = Path("openapi.yaml")
        if not openapi_path.exists():
            openapi_path = Path("../openapi.yaml")

        if not openapi_path.exists():
            raise FileNotFoundError("openapi.yaml not found")

        with open(openapi_path, "r") as f:
            openapi_schema = yaml.safe_load(f)

        logger.info(f"Loaded OpenAPI schema from {openapi_path}")
        app.openapi_schema = openapi_schema
        return app.openapi_schema
    except Exception as e:
        # Fall back to auto-generated schema if file can't be loaded
        logger.warning(f"Error loading OpenAPI schema from file: {e}")
        logger.warning("Falling back to auto-generated schema")

        openapi_schema = get_openapi(
            title=settings.PROJECT_NAME,
            version=settings.VERSION,
            description=settings.DESCRIPTION,
            routes=app.routes,
        )
        app.openapi_schema = openapi_schema
        return app.openapi_schema


app.openapi = custom_openapi


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors and return a standardized response.
    """
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all requests to the API.
    """
    logger.info(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response: {response.status_code}")
    return response


@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message.
    """
    return {
        "message": "Welcome to POD AI Automation API",
        "docs": f"{settings.API_V1_STR}/docs",
        "version": settings.VERSION
    }


@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
