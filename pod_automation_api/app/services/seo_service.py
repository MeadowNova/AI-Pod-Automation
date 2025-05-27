from typing import Dict, List, Optional
import json
import httpx
import logging

from app.core.config import settings
from app.schemas.seo import ListingOptimizationResponse, SEORecommendation
from app.services.etsy_service import get_etsy_listing
from pod_automation.agents.seo.openai_seo_optimizer import OpenAISEOOptimizer

logger = logging.getLogger(__name__)

# Initialize the OpenAI SEO optimizer
seo_optimizer = None

def get_seo_optimizer():
    """Get or create the SEO optimizer instance."""
    global seo_optimizer
    if seo_optimizer is None:
        try:
            seo_optimizer = OpenAISEOOptimizer(
                api_key=settings.OPENAI_API_KEY,
                model=settings.OPENAI_MODEL
            )
            logger.info("Initialized OpenAI SEO optimizer")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI SEO optimizer: {str(e)}")
            raise RuntimeError(f"SEO optimizer initialization failed: {str(e)}")
    return seo_optimizer


async def optimize_listing(
    user_id: str,
    listing_id: str,
    current_title: Optional[str] = None,
    current_tags: Optional[List[str]] = None,
    current_description: Optional[str] = None
) -> ListingOptimizationResponse:
    """
    Optimize an Etsy listing's SEO using AI
    """
    # Get the listing if not all data was provided
    if not all([current_title, current_tags, current_description]):
        listing = await get_etsy_listing(user_id, listing_id)
        if not listing:
            raise ValueError(f"Listing with ID {listing_id} not found")

        current_title = current_title or listing.title
        current_tags = current_tags or listing.tags or []
        current_description = current_description or listing.description or ""

    # Call the OpenAI SEO optimizer to optimize the listing
    try:
        optimizer = get_seo_optimizer()

        # Prepare listing data for optimization
        listing_data = {
            'title': current_title,
            'description': current_description,
            'tags': current_tags,
            'taxonomy_path': ['Unknown']  # Default category
        }

        # Optimize the listing using OpenAI
        optimized_listing = optimizer.optimize_listing(
            listing_data=listing_data,
            optimize_title=True,
            optimize_tags=True,
            optimize_description=True
        )

        optimization_result = {
            "optimized_title": optimized_listing.get('title', current_title),
            "optimized_tags": optimized_listing.get('tags', current_tags),
            "optimized_description": optimized_listing.get('description', current_description),
            "reasoning": "Optimized using OpenAI GPT-4o for improved SEO performance"
        }

    except Exception as e:
        logger.error(f"Error optimizing listing with OpenAI: {str(e)}")
        # Fallback to original content if optimization fails
        optimization_result = {
            "optimized_title": current_title,
            "optimized_tags": current_tags,
            "optimized_description": current_description,
            "reasoning": f"Optimization failed: {str(e)}"
        }

    # Calculate SEO score based on various factors
    seo_score = calculate_seo_score(
        original_title=current_title,
        original_tags=current_tags,
        original_description=current_description,
        optimized_title=optimization_result.get("optimized_title", ""),
        optimized_tags=optimization_result.get("optimized_tags", []),
        optimized_description=optimization_result.get("optimized_description", "")
    )

    # Generate recommendations
    recommendations = generate_recommendations(
        original_title=current_title,
        original_tags=current_tags,
        original_description=current_description,
        optimized_title=optimization_result.get("optimized_title", ""),
        optimized_tags=optimization_result.get("optimized_tags", []),
        optimized_description=optimization_result.get("optimized_description", ""),
        ai_feedback=optimization_result.get("reasoning", "")
    )

    return ListingOptimizationResponse(
        optimized_title=optimization_result.get("optimized_title"),
        optimized_tags=optimization_result.get("optimized_tags"),
        optimized_description=optimization_result.get("optimized_description"),
        seo_score=seo_score,
        recommendations=recommendations
    )


# Removed call_ai_model function - now using OpenAI SEO optimizer directly


def calculate_seo_score(
    original_title: str,
    original_tags: List[str],
    original_description: str,
    optimized_title: str,
    optimized_tags: List[str],
    optimized_description: str
) -> int:
    """
    Calculate an SEO score based on various factors
    """
    # This is a simplified scoring algorithm
    # In a real implementation, this would be more sophisticated

    score = 50  # Base score

    # Title factors
    if len(optimized_title) >= 120:
        score += 10
    elif len(optimized_title) >= 80:
        score += 5

    # Tags factors
    if len(optimized_tags) >= 13:
        score += 15
    elif len(optimized_tags) >= 10:
        score += 10
    elif len(optimized_tags) >= 7:
        score += 5

    # Description factors
    if len(optimized_description) >= 500:
        score += 10
    elif len(optimized_description) >= 300:
        score += 5

    # Improvement factors
    if len(optimized_title) > len(original_title):
        score += 5

    if len(optimized_tags) > len(original_tags):
        score += 5

    if len(optimized_description) > len(original_description):
        score += 5

    # Cap at 100
    return min(score, 100)


def generate_recommendations(
    original_title: str,
    original_tags: List[str],
    original_description: str,
    optimized_title: str,
    optimized_tags: List[str],
    optimized_description: str,
    ai_feedback: str
) -> List[SEORecommendation]:
    """
    Generate SEO recommendations based on the optimization
    """
    recommendations = []

    # Title recommendations
    title_score = min(100, int(len(optimized_title) / 140 * 100))
    if title_score < 70:
        recommendations.append(
            SEORecommendation(
                category="title",
                score=title_score,
                feedback="Your title is too short. Aim for 120-140 characters to maximize visibility."
            )
        )
    else:
        recommendations.append(
            SEORecommendation(
                category="title",
                score=title_score,
                feedback="Your title has good length. Make sure it includes relevant keywords."
            )
        )

    # Tags recommendations
    tags_score = min(100, int(len(optimized_tags) / 13 * 100))
    if tags_score < 70:
        recommendations.append(
            SEORecommendation(
                category="tags",
                score=tags_score,
                feedback=f"You're only using {len(optimized_tags)} out of 13 possible tags. Add more relevant tags to improve visibility."
            )
        )
    else:
        recommendations.append(
            SEORecommendation(
                category="tags",
                score=tags_score,
                feedback="Good use of tags. Consider using long-tail keyword phrases for some tags."
            )
        )

    # Description recommendations
    desc_score = min(100, int(len(optimized_description) / 500 * 100))
    if desc_score < 70:
        recommendations.append(
            SEORecommendation(
                category="description",
                score=desc_score,
                feedback="Your description could be more detailed. Add more information about materials, dimensions, and use cases."
            )
        )
    else:
        recommendations.append(
            SEORecommendation(
                category="description",
                score=desc_score,
                feedback="Good description length. Make sure it includes relevant keywords naturally."
            )
        )

    return recommendations
