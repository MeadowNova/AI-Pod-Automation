from typing import Dict, List, Optional

from app.schemas.etsy import EtsyListing, EtsyListingPagination

# Mock data for development
MOCK_LISTINGS = [
    {
        "id": "12345",
        "title": "Vintage Sunset T-Shirt - Retro 80s Style Graphic Tee",
        "description": "A super soft vintage-style t-shirt featuring a stunning retro sunset graphic. Perfect for 80s enthusiasts and lovers of unique graphic tees. Made from 100% cotton for maximum comfort.",
        "tags": ["vintage t-shirt", "retro shirt", "80s graphics", "sunset tee", "graphic tee"],
        "price": 24.99,
        "status": "active",
        "thumbnail_url": "https://example.com/images/vintage-sunset-tee.jpg",
        "seo_score": 75
    },
    {
        "id": "67890",
        "title": "Funny Cat Mug - \"I Need More Coffee\" - Cute Pet Lover Gift",
        "description": "Start your day with a smile with this hilarious cat mug! Features a cute cat illustration and the relatable phrase \"I Need More Coffee\". A great gift for any cat owner or coffee addict.",
        "tags": ["cat mug", "funny coffee mug", "pet lover gift", "cute cat", "coffee lover"],
        "price": 15.99,
        "status": "active",
        "thumbnail_url": "https://example.com/images/cat-coffee-mug.jpg",
        "seo_score": 60
    },
    {
        "id": "24680",
        "title": "Minimalist Line Art Print - Abstract Face Poster, Modern Wall Decor",
        "description": "Add a touch of modern elegance to your home with this minimalist line art print. Featuring an abstract face design, this poster is perfect for contemporary interiors. High-quality print on premium paper.",
        "tags": ["line art", "abstract print", "minimalist decor", "modern wall art", "face poster"],
        "price": 18.50,
        "status": "draft",
        "thumbnail_url": "https://example.com/images/line-art-print.jpg",
        "seo_score": 85
    }
]


async def get_etsy_listings(
    user_id: str,
    status: Optional[str] = None,
    page: int = 1,
    limit: int = 20
) -> EtsyListingPagination:
    """
    Get Etsy listings for a user
    
    In a real implementation, this would call the Etsy API
    """
    # Filter by status if provided
    filtered_listings = MOCK_LISTINGS
    if status and status != "all":
        filtered_listings = [l for l in MOCK_LISTINGS if l["status"] == status]
    
    # Calculate pagination
    start_idx = (page - 1) * limit
    end_idx = start_idx + limit
    paginated_listings = filtered_listings[start_idx:end_idx]
    
    # Convert to EtsyListing objects
    listings = [EtsyListing(**listing) for listing in paginated_listings]
    
    # Create pagination info
    pagination = {
        "total": len(filtered_listings),
        "page": page,
        "limit": limit,
        "pages": (len(filtered_listings) + limit - 1) // limit
    }
    
    return EtsyListingPagination(data=listings, pagination=pagination)


async def get_etsy_listing(user_id: str, listing_id: str) -> Optional[EtsyListing]:
    """
    Get a specific Etsy listing
    
    In a real implementation, this would call the Etsy API
    """
    for listing in MOCK_LISTINGS:
        if listing["id"] == listing_id:
            return EtsyListing(**listing)
    return None
