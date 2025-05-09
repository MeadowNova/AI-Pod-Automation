"""
Adapter for SEO optimization services.

This module provides an adapter for connecting the FastAPI BFF layer to the existing
SEO optimization services in the pod_automation system.
"""

import logging
from typing import Dict, List, Optional, Any

from app.core.config import settings
from app.schemas.seo import ListingOptimizationResponse, SEORecommendation

logger = logging.getLogger(__name__)

class SEOServiceAdapter:
    """Adapter for SEO optimization services."""
    
    def __init__(self):
        """Initialize the SEO service adapter."""
        try:
            # Import the existing SEO optimizer
            from pod_automation.agents.seo.ai.ai_seo_optimizer import AISEOOptimizer
            from pod_automation.agents.seo.db import seo_db
            
            # Initialize the optimizer with the configured model
            self.optimizer = AISEOOptimizer(ollama_model=settings.AI_MODEL_NAME)
            self.db = seo_db
            self.initialized = True
            logger.info("SEO service adapter initialized successfully")
        except ImportError as e:
            logger.error(f"Failed to import SEO optimizer: {str(e)}")
            self.initialized = False
        except Exception as e:
            logger.error(f"Failed to initialize SEO service adapter: {str(e)}")
            self.initialized = False
    
    async def optimize_listing(
        self,
        user_id: str,
        listing_id: str,
        current_title: Optional[str] = None,
        current_tags: Optional[List[str]] = None,
        current_description: Optional[str] = None
    ) -> ListingOptimizationResponse:
        """
        Optimize an Etsy listing using the existing SEO optimizer.
        
        Args:
            user_id: User ID
            listing_id: Etsy listing ID
            current_title: Current listing title (optional)
            current_tags: Current listing tags (optional)
            current_description: Current listing description (optional)
            
        Returns:
            ListingOptimizationResponse: Optimized listing data
        """
        if not self.initialized:
            logger.error("SEO service adapter not initialized")
            raise RuntimeError("SEO service not available")
        
        try:
            # Get the listing data from the database if not provided
            listing_data = {}
            if not all([current_title, current_tags, current_description]):
                # Try to get the listing from the database
                db_listing = self.db.get_listing_by_etsy_id(listing_id)
                if db_listing:
                    listing_data = db_listing
                    current_title = current_title or db_listing.get("title_original")
                    current_tags = current_tags or db_listing.get("tags_original", [])
                    current_description = current_description or db_listing.get("description_original")
            
            # If we still don't have the data, try to fetch it from Etsy
            if not all([current_title, current_tags]):
                # In a real implementation, you would fetch the listing from Etsy
                # For now, we'll raise an error
                raise ValueError(f"Listing data not found for ID {listing_id}")
            
            # Prepare the listing data for optimization
            if not listing_data:
                listing_data = {
                    "etsy_listing_id": listing_id,
                    "title_original": current_title,
                    "tags_original": current_tags,
                    "description_original": current_description
                }
            
            # Optimize the listing
            optimized_data = self.optimizer.optimize_listing_ai(listing_id, listing_data)
            
            if not optimized_data:
                raise RuntimeError(f"Failed to optimize listing {listing_id}")
            
            # Calculate SEO score
            seo_score = optimized_data.get("seo_score", 0)
            if not seo_score:
                # If no score was provided, calculate it based on the optimization
                title_score = min(100, int(len(optimized_data.get("title_optimized", "")) / 140 * 100))
                tags_score = min(100, int(len(optimized_data.get("tags_optimized", [])) / 13 * 100))
                seo_score = (title_score + tags_score) // 2
            
            # Generate recommendations
            recommendations = []
            if "recommendations" in optimized_data:
                for rec in optimized_data["recommendations"]:
                    recommendations.append(
                        SEORecommendation(
                            category=rec["category"],
                            score=rec["score"],
                            feedback=rec["feedback"]
                        )
                    )
            else:
                # Generate basic recommendations if none were provided
                title_length = len(optimized_data.get("title_optimized", ""))
                tags_count = len(optimized_data.get("tags_optimized", []))
                
                if title_length < 120:
                    recommendations.append(
                        SEORecommendation(
                            category="title",
                            score=int(title_length / 140 * 100),
                            feedback="Your title is too short. Aim for 120-140 characters."
                        )
                    )
                
                if tags_count < 13:
                    recommendations.append(
                        SEORecommendation(
                            category="tags",
                            score=int(tags_count / 13 * 100),
                            feedback=f"You're only using {tags_count} out of 13 possible tags."
                        )
                    )
            
            # Create the response
            return ListingOptimizationResponse(
                optimized_title=optimized_data.get("title_optimized"),
                optimized_tags=optimized_data.get("tags_optimized"),
                optimized_description=optimized_data.get("description_optimized"),
                seo_score=seo_score,
                recommendations=recommendations
            )
        
        except Exception as e:
            logger.error(f"Error optimizing listing: {str(e)}")
            raise


# Create a singleton instance
seo_service = SEOServiceAdapter()
