import sys
import os
# Ensure current directory is in sys.path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from schemas import ListingInput, ListingOutput
from optimize_listings import optimize_listing

app = FastAPI(title="SEO Optimizer API", description="API endpoint for optimizing Etsy listings", version="1.0")

@app.post("/optimize-listing", response_model=ListingOutput)
async def optimize_listing_endpoint(listing: ListingInput):
    """Optimize an Etsy listing's title, tags, and description via API."""
    try:
        optimized = optimize_listing(listing.dict())
        return optimized
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fastapi_server:app", host="127.0.0.1", port=8000, reload=True)