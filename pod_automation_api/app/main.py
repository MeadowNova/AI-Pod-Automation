import os
import logging
from pathlib import Path
import yaml
import json

import sentry_sdk
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.api.api import api_router
from app.core.config import settings
from app.adapters import etsy_adapter

# Initialize Sentry for error monitoring and performance tracking
sentry_sdk.init(
    dsn="https://5116336a0440e5e55e95e1b07de14db1@o4509373980344320.ingest.us.sentry.io/4509374289149952",
    # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring.
    # We recommend adjusting this value in production (e.g., 0.1 for 10% sampling)
    traces_sample_rate=1.0,
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
    # Set profiles_sample_rate to 1.0 to profile 100% of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

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

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup():
    """Initialize services on startup."""
    # Initialize Etsy adapter
    if not etsy_adapter.etsy_service.initialized:
        # Re-initialize the adapter
        etsy_adapter.etsy_service = etsy_adapter.EtsyServiceAdapter()
        if not etsy_adapter.etsy_service.initialized:
            raise RuntimeError("Failed to initialize Etsy service adapter")


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


@app.get("/sentry-debug")
async def trigger_error():
    """
    Debug endpoint to test Sentry error reporting.
    This will trigger a division by zero error that will be sent to Sentry.
    """
    division_by_zero = 1 / 0


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
