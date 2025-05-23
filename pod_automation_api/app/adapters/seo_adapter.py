"""
Adapter for SEO optimization services.

This module provides an adapter for connecting the FastAPI BFF layer to the existing
SEO optimization services in the pod_automation system.
"""

import logging
import time
import socket
import os
import traceback
from typing import Dict, List, Optional, Any, Tuple
import requests

from app.core.config import settings
from app.schemas.seo import ListingOptimizationResponse, SEORecommendation

# Configure more detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SEOServiceAdapter:
    """Adapter for SEO optimization services."""

    def __init__(self):
        """Initialize the SEO service adapter."""
        self.initialized = False
        self.optimizer = None
        self.db = None

        logger.info("Initializing SEO service adapter...")
        logger.info(f"Current working directory: {os.getcwd()}")
        logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")

        try:
            # Import the existing SEO optimizer
            logger.debug("Importing required modules...")
            try:
                from pod_automation.agents.seo.ai.ai_seo_optimizer import AISEOOptimizer
                from pod_automation.agents.seo.db import seo_db
                from pod_automation.agents.seo.ai.ollama_client import OllamaClient
                logger.debug("Successfully imported required modules")
            except ImportError as e:
                logger.error(f"Failed to import required modules: {str(e)}")
                logger.error(f"Import error traceback: {traceback.format_exc()}")
                raise

            # Get container hostname for debugging
            hostname = socket.gethostname()
            logger.info(f"Container hostname: {hostname}")

            # Use the URL that we know works
            working_url = "http://host.docker.internal:11434"
            logger.info(f"Using Ollama URL: {working_url}")

            # Define preferred models - specifically use mistral for generation and nomic for embeddings
            generation_model = "mistral:latest"  # Always use mistral for generation
            embedding_model = "nomic-embed-text:latest"  # Always use nomic-embed-text for embeddings
            logger.info(f"Preferred generation model: {generation_model}")
            logger.info(f"Preferred embedding model: {embedding_model}")

            # Check basic connectivity first
            try:
                logger.debug(f"Testing basic connectivity to {working_url}")
                response = requests.get(f"{working_url}/api/tags", timeout=10)
                if response.status_code == 200:
                    logger.info(f"✅ Basic connectivity to {working_url} successful")
                    available_models = [model["name"] for model in response.json().get("models", [])]
                    logger.info(f"Available models: {available_models}")
                else:
                    logger.error(f"❌ Basic connectivity to {working_url} failed with status code {response.status_code}")
                    raise RuntimeError(f"Ollama service returned status code {response.status_code}")
            except Exception as e:
                logger.error(f"❌ Basic connectivity to {working_url} failed: {str(e)}")
                raise RuntimeError(f"Failed to connect to Ollama service: {str(e)}")

            # Create the Ollama client with the working URL
            logger.debug(f"Creating OllamaClient with URL: {working_url}")
            temp_client = OllamaClient(
                base_url=working_url,
                generation_model=generation_model,
                embedding_model=embedding_model
            )

            # Use the models that were selected by the client's auto-fallback mechanism
            generation_model = temp_client.generation_model
            embedding_model = temp_client.embedding_model

            logger.info(f"Using generation model: {generation_model}")
            logger.info(f"Using embedding model: {embedding_model}")

            # Initialize the optimizer with the configured models
            logger.debug("Initializing AISEOOptimizer...")
            self.optimizer = AISEOOptimizer(
                generation_model=generation_model,
                embedding_model=embedding_model,
                use_gpu=True  # Enable GPU acceleration if available
            )
            self.db = seo_db

            # Ensure the RAG system is properly initialized
            try:
                logger.debug("Initializing RAG system...")
                # Force indexing of a small number of listings to ensure RAG is working
                self.optimizer.rag.index_keywords()
                self.optimizer.rag.index_listings(limit=10)  # Start with just 10 listings for quick initialization
                logger.info("✅ RAG system successfully initialized and indexed initial data")
            except Exception as e:
                logger.warning(f"⚠️ RAG system initialization warning (will continue without RAG): {str(e)}")
                logger.warning(f"RAG initialization error traceback: {traceback.format_exc()}")

            self.initialized = True
            logger.info(f"✅ SEO service adapter initialized successfully with model: {generation_model}")

        except ImportError as e:
            logger.error(f"❌ Failed to import SEO optimizer: {str(e)}")
            logger.error(f"Import error traceback: {traceback.format_exc()}")
            self.initialized = False
        except ConnectionError as e:
            logger.error(f"❌ Failed to connect to Ollama service: {str(e)}")
            logger.error(f"Connection error traceback: {traceback.format_exc()}")
            self.initialized = False
        except Exception as e:
            logger.error(f"❌ Failed to initialize SEO service adapter: {str(e)}")
            logger.error(f"Initialization error traceback: {traceback.format_exc()}")
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

            # Calculate SEO scores with improved methodology
            start_time = time.time()

            # Get original and optimized content
            original_title = current_title or ""
            original_tags = current_tags or []
            original_description = current_description or ""

            optimized_title = optimized_data.get("title_optimized", "")
            optimized_tags = optimized_data.get("tags_optimized", [])
            optimized_description = optimized_data.get("description_optimized", "")

            # Calculate original SEO score
            original_seo_score = self._calculate_seo_score(original_title, original_tags, original_description)

            # Calculate optimized SEO score
            seo_score = optimized_data.get("seo_score", 0)
            if not seo_score:
                seo_score = self._calculate_seo_score(optimized_title, optimized_tags, optimized_description)

            # Calculate improvement percentage
            improvement_percentage = 0
            if original_seo_score > 0:
                improvement_percentage = ((seo_score - original_seo_score) / original_seo_score) * 100

            processing_time_ms = int((time.time() - start_time) * 1000)

            # Generate enhanced recommendations
            recommendations = self._generate_recommendations(
                original_title, original_tags, original_description,
                optimized_title, optimized_tags, optimized_description,
                original_seo_score, seo_score
            )

            # Create the response with enhanced data
            return ListingOptimizationResponse(
                listing_id=listing_id,
                original_title=original_title,
                original_tags=original_tags,
                original_description=original_description,
                optimized_title=optimized_title,
                optimized_tags=optimized_tags,
                optimized_description=optimized_description,
                seo_score=seo_score,
                original_seo_score=original_seo_score,
                improvement_percentage=improvement_percentage,
                recommendations=recommendations,
                processing_time_ms=processing_time_ms
            )

        except Exception as e:
            logger.error(f"Error optimizing listing: {str(e)}")
            raise

    def _calculate_seo_score(self, title: str, tags: List[str], description: str) -> int:
        """
        Calculate SEO score based on Etsy best practices.

        Args:
            title: Listing title
            tags: List of tags
            description: Listing description

        Returns:
            int: SEO score from 0-100
        """
        total_score = 0

        # Title scoring (40% weight)
        title_score = 0
        title_length = len(title)

        # Length scoring (optimal 120-140 chars)
        if 120 <= title_length <= 140:
            title_score += 40  # Perfect length
        elif 100 <= title_length < 120:
            title_score += 35  # Good length
        elif 80 <= title_length < 100:
            title_score += 25  # Acceptable length
        elif 60 <= title_length < 80:
            title_score += 15  # Short but usable
        else:
            title_score += 5   # Too short or too long

        # Keyword density and relevance
        common_keywords = ["vintage", "handmade", "custom", "personalized", "gift", "art", "print", "shirt", "home", "decor"]
        keyword_matches = sum(1 for keyword in common_keywords if keyword.lower() in title.lower())
        title_score += min(20, keyword_matches * 4)  # Up to 20 points for keywords

        # First 40 characters importance
        first_40_chars = title[:40].lower()
        if any(keyword in first_40_chars for keyword in ["gift", "custom", "personalized"]):
            title_score += 10

        title_score = min(100, title_score)
        total_score += title_score * 0.4

        # Tags scoring (30% weight)
        tags_score = 0
        tags_count = len(tags)

        # Tag count scoring (optimal is 13)
        if tags_count == 13:
            tags_score += 50  # Perfect tag count
        elif tags_count >= 10:
            tags_score += 40  # Good tag count
        elif tags_count >= 7:
            tags_score += 30  # Acceptable tag count
        elif tags_count >= 5:
            tags_score += 20  # Minimal tag count
        else:
            tags_score += 10  # Too few tags

        # Tag length validation (max 20 chars each)
        valid_tags = sum(1 for tag in tags if len(tag) <= 20)
        if valid_tags == tags_count and tags_count > 0:
            tags_score += 20  # All tags valid length
        elif valid_tags > 0:
            tags_score += int(20 * (valid_tags / tags_count))

        # Tag relevance and variety
        if tags_count > 0:
            unique_words = set()
            for tag in tags:
                unique_words.update(tag.lower().split())
            variety_score = min(30, len(unique_words) * 2)  # Up to 30 points for variety
            tags_score += variety_score

        tags_score = min(100, tags_score)
        total_score += tags_score * 0.3

        # Description scoring (30% weight)
        desc_score = 0
        desc_length = len(description)

        # Length scoring
        if desc_length >= 1000:
            desc_score += 40  # Excellent length
        elif desc_length >= 500:
            desc_score += 35  # Good length
        elif desc_length >= 300:
            desc_score += 25  # Acceptable length
        elif desc_length >= 150:
            desc_score += 15  # Short but usable
        else:
            desc_score += 5   # Too short

        # Content quality indicators
        if description:
            # Check for material mentions
            materials = ["cotton", "polyester", "canvas", "paper", "vinyl", "ceramic", "metal"]
            if any(material in description.lower() for material in materials):
                desc_score += 15

            # Check for size/dimension mentions
            size_indicators = ["size", "dimension", "inch", "cm", "small", "medium", "large", "xl"]
            if any(indicator in description.lower() for indicator in size_indicators):
                desc_score += 15

            # Check for care instructions
            care_words = ["wash", "care", "clean", "maintain", "iron", "dry"]
            if any(word in description.lower() for word in care_words):
                desc_score += 10

            # Check for shipping/processing time mentions
            shipping_words = ["ship", "process", "delivery", "business days", "handling"]
            if any(word in description.lower() for word in shipping_words):
                desc_score += 10

            # Penalize for excessive capitalization
            if description.isupper():
                desc_score -= 20

            # Bonus for proper formatting (paragraphs)
            if '\n' in description or '. ' in description:
                desc_score += 10

        desc_score = min(100, desc_score)
        total_score += desc_score * 0.3

        return int(total_score)

    def _generate_recommendations(
        self,
        original_title: str,
        original_tags: List[str],
        original_description: str,
        optimized_title: str,
        optimized_tags: List[str],
        optimized_description: str,
        original_score: int,
        optimized_score: int
    ) -> List[SEORecommendation]:
        """
        Generate detailed, actionable SEO recommendations.

        Args:
            original_title: Original listing title
            original_tags: Original listing tags
            original_description: Original listing description
            optimized_title: AI-optimized title
            optimized_tags: AI-optimized tags
            optimized_description: AI-optimized description
            original_score: Original SEO score
            optimized_score: Optimized SEO score

        Returns:
            List[SEORecommendation]: List of actionable recommendations
        """
        recommendations = []

        # Title recommendations
        title_length = len(optimized_title)
        if title_length < 120:
            recommendations.append(
                SEORecommendation(
                    category="title",
                    score=int(title_length / 140 * 100),
                    feedback=f"Title is {title_length} characters. Etsy recommends 120-140 characters.",
                    improvement_suggestion="Add descriptive keywords like material, style, or use case to reach optimal length.",
                    priority="high"
                )
            )
        elif title_length > 140:
            recommendations.append(
                SEORecommendation(
                    category="title",
                    score=max(50, 100 - (title_length - 140) * 2),
                    feedback=f"Title is {title_length} characters, which may be truncated in search results.",
                    improvement_suggestion="Remove less important words while keeping key descriptive terms.",
                    priority="medium"
                )
            )

        # Check for important keywords in first 40 characters
        first_40_chars = optimized_title[:40].lower()
        important_keywords = ["gift", "custom", "personalized", "handmade", "vintage"]
        if not any(keyword in first_40_chars for keyword in important_keywords):
            recommendations.append(
                SEORecommendation(
                    category="title",
                    score=70,
                    feedback="Consider placing high-impact keywords like 'gift', 'custom', or 'personalized' in the first 40 characters.",
                    improvement_suggestion="Move your most compelling selling point to the beginning of the title.",
                    priority="medium"
                )
            )

        # Tags recommendations
        tags_count = len(optimized_tags)
        if tags_count < 13:
            missing_tags = 13 - tags_count
            recommendations.append(
                SEORecommendation(
                    category="tags",
                    score=int(tags_count / 13 * 100),
                    feedback=f"Using {tags_count}/13 tags. You're missing {missing_tags} opportunities for discovery.",
                    improvement_suggestion="Add more specific tags like materials, occasions, or style descriptors.",
                    priority="high" if missing_tags > 5 else "medium"
                )
            )

        # Check for tag length violations
        long_tags = [tag for tag in optimized_tags if len(tag) > 20]
        if long_tags:
            recommendations.append(
                SEORecommendation(
                    category="tags",
                    score=max(50, 100 - len(long_tags) * 10),
                    feedback=f"{len(long_tags)} tags exceed 20 character limit: {', '.join(long_tags[:3])}{'...' if len(long_tags) > 3 else ''}",
                    improvement_suggestion="Shorten tags by removing articles (a, the) or using abbreviations.",
                    priority="high"
                )
            )

        # Check for tag variety
        if tags_count > 0:
            unique_words = set()
            for tag in optimized_tags:
                unique_words.update(tag.lower().split())
            if len(unique_words) < tags_count * 1.5:  # Low variety indicator
                recommendations.append(
                    SEORecommendation(
                        category="tags",
                        score=60,
                        feedback="Tags may be too similar. Consider more variety in descriptive terms.",
                        improvement_suggestion="Mix broad category tags with specific descriptive tags and long-tail keywords.",
                        priority="medium"
                    )
                )

        # Description recommendations
        desc_length = len(optimized_description)
        if desc_length < 300:
            recommendations.append(
                SEORecommendation(
                    category="description",
                    score=int(desc_length / 1000 * 100),
                    feedback=f"Description is {desc_length} characters. Longer descriptions perform better in search.",
                    improvement_suggestion="Add details about materials, dimensions, care instructions, and shipping information.",
                    priority="medium"
                )
            )

        # Check for missing key information in description
        missing_info = []
        if not any(material in optimized_description.lower() for material in ["cotton", "polyester", "canvas", "paper", "vinyl", "ceramic", "metal", "wood"]):
            missing_info.append("materials")
        if not any(size_word in optimized_description.lower() for size_word in ["size", "dimension", "inch", "cm", "small", "medium", "large"]):
            missing_info.append("size information")
        if not any(care_word in optimized_description.lower() for care_word in ["wash", "care", "clean", "maintain"]):
            missing_info.append("care instructions")

        if missing_info:
            recommendations.append(
                SEORecommendation(
                    category="description",
                    score=70,
                    feedback=f"Description missing: {', '.join(missing_info)}",
                    improvement_suggestion="Include comprehensive product details to help buyers make informed decisions.",
                    priority="medium"
                )
            )

        # Overall improvement recommendation
        if optimized_score > original_score:
            improvement = optimized_score - original_score
            recommendations.append(
                SEORecommendation(
                    category="overall",
                    score=optimized_score,
                    feedback=f"AI optimization improved your SEO score by {improvement} points ({((improvement/original_score)*100):.1f}% increase).",
                    improvement_suggestion="Apply these optimizations to improve your listing's search visibility.",
                    priority="high"
                )
            )

        return recommendations

    async def optimize_listings_batch(
        self,
        user_id: str,
        listings: List[Dict[str, Any]],
        max_listings: Optional[int] = None
    ) -> List[ListingOptimizationResponse]:
        """
        Optimize multiple Etsy listings in a batch.

        Args:
            user_id: User ID
            listings: List of listings to optimize
            max_listings: Maximum number of listings to process

        Returns:
            List[ListingOptimizationResponse]: List of optimized listings
        """
        if not self.initialized:
            logger.error("SEO service adapter not initialized")
            raise RuntimeError("SEO service not available")

        try:
            # Prepare listings for optimization
            prepared_listings = []
            for listing in listings:
                listing_id = listing.get("etsy_listing_id") or listing.get("id")
                title = listing.get("title") or listing.get("title_original")
                tags = listing.get("tags") or listing.get("tags_original", [])
                description = listing.get("description") or listing.get("description_original")

                if not all([listing_id, title]):
                    logger.warning(f"Skipping listing with missing data: {listing}")
                    continue

                prepared_listing = {
                    "etsy_listing_id": listing_id,
                    "title_original": title,
                    "tags_original": tags,
                    "description_original": description
                }
                prepared_listings.append(prepared_listing)

            if not prepared_listings:
                logger.warning("No valid listings to optimize")
                return []

            # Log the batch size
            logger.info(f"Optimizing batch of {len(prepared_listings)} listings")

            # Optimize listings in batch
            optimized_listings = self.optimizer.optimize_listings_batch(prepared_listings, max_listings)

            # Convert to response format
            responses = []
            for optimized in optimized_listings:
                # Calculate SEO score
                seo_score = optimized.get("optimization_score", 0)

                # Create response
                response = ListingOptimizationResponse(
                    listing_id=optimized.get("etsy_listing_id"),
                    optimized_title=optimized.get("title_optimized"),
                    optimized_tags=optimized.get("tags_optimized"),
                    optimized_description=optimized.get("description_optimized"),
                    seo_score=seo_score,
                    recommendations=[]  # We could add recommendations here if needed
                )
                responses.append(response)

            # Log cache statistics
            cache_stats = self.optimizer.ollama.get_cache_stats()
            logger.info(f"Embedding cache stats after batch: {cache_stats}")

            return responses

        except Exception as e:
            logger.error(f"Error optimizing listings batch: {str(e)}")
            raise


# Create a singleton instance
seo_service = SEOServiceAdapter()
