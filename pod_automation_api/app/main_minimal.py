"""
Minimal version of the main application that doesn't try to import pod_automation.
This is used as a fallback if the pod_automation module can't be imported.
"""

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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="POD AI Automation API",
    description="API for POD AI Automation system",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    """
    Root endpoint that returns a welcome message.
    """
    return {
        "message": "Welcome to POD AI Automation API (Minimal Version)",
        "docs": "/docs",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "healthy"}

@app.get("/api/v1/status")
def api_status():
    """
    API status endpoint.
    """
    return {
        "status": "running",
        "message": "API is running in minimal mode. Some features may be limited.",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main_minimal:app", host="0.0.0.0", port=8001, reload=True)
