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
            from pod_automation.agents.seo.ai.ollama_client import OllamaClient

            # First check if Ollama is accessible
            ollama_client = OllamaClient(
                base_url=settings.AI_MODEL_HOST,
                model=settings.AI_MODEL_NAME
            )

            # Test connection by getting available models
            available_models = ollama_client.get_available_models()
            if not available_models:
                logger.warning(f"No models available from Ollama at {settings.AI_MODEL_HOST}")
                raise RuntimeError(f"Ollama service not available or no models found")

            if settings.AI_MODEL_NAME not in [model.split(':')[0] for model in available_models]:
                logger.warning(f"Model {settings.AI_MODEL_NAME} not found in available models: {available_models}")
                # Try to use an available model instead
                fallback_model = available_models[0] if available_models else settings.AI_MODEL_NAME
                logger.info(f"Falling back to available model: {fallback_model}")
                settings.AI_MODEL_NAME = fallback_model

            # Initialize the optimizer with the configured model
            self.optimizer = AISEOOptimizer(
                ollama_model=settings.AI_MODEL_NAME,
                use_gpu=True  # Enable GPU acceleration if available
            )
            self.db = seo_db

            # Ensure the RAG system is properly initialized
            try:
                # Force indexing of a small number of listings to ensure RAG is working
                self.optimizer.rag.index_keywords()
                self.optimizer.rag.index_listings(limit=10)  # Start with just 10 listings for quick initialization
                logger.info("RAG system successfully initialized and indexed initial data")
            except Exception as e:
                logger.warning(f"RAG system initialization warning (will continue without RAG): {str(e)}")

            self.initialized = True
            logger.info(f"SEO service adapter initialized successfully with model: {settings.AI_MODEL_NAME}")
        except ImportError as e:
            logger.error(f"Failed to import SEO optimizer: {str(e)}")
            self.initialized = False
        except ConnectionError as e:
            logger.error(f"Failed to connect to Ollama service: {str(e)}")
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
                # Title score: Based on length (optimal is 120-140 chars) and keyword usage
                title = optimized_data.get("title_optimized", "")
                title_length = len(title)
                title_length_score = 0
                if title_length >= 120 and title_length <= 140:
                    title_length_score = 100  # Perfect length
                elif title_length >= 100:
                    title_length_score = 80   # Good length
                elif title_length >= 80:
                    title_length_score = 60   # Acceptable length
                elif title_length >= 50:
                    title_length_score = 40   # Short title
                else:
                    title_length_score = 20   # Very short title

                # Check for keyword usage in title
                keyword_score = 0
                keywords = ["cat", "art", "print", "shirt", "gift", "home", "decor"]
                for keyword in keywords:
                    if keyword.lower() in title.lower():
                        keyword_score += 10
                keyword_score = min(50, keyword_score)  # Cap at 50 points

                title_score = (title_length_score + keyword_score) // 2

                # Tags score: Based on count (optimal is 13) and relevance
                tags = optimized_data.get("tags_optimized", [])
                tags_count = len(tags)
                tags_count_score = min(100, int(tags_count / 13 * 100))

                # Description score: Based on length and content
                description = optimized_data.get("description_optimized", "")
                desc_length = len(description)
                desc_score = 0
                if desc_length >= 1000:
                    desc_score = 100  # Excellent description
                elif desc_length >= 500:
                    desc_score = 80   # Good description
                elif desc_length >= 300:
                    desc_score = 60   # Acceptable description
                elif desc_length >= 100:
                    desc_score = 40   # Short description
                else:
                    desc_score = 20   # Very short description

                # Calculate overall score with weighted components
                seo_score = int((title_score * 0.4) + (tags_count_score * 0.3) + (desc_score * 0.3))

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
