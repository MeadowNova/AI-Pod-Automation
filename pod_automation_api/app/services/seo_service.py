from typing import Dict, List, Optional
import json
import httpx

from app.core.config import settings
from app.schemas.seo import ListingOptimizationResponse, SEORecommendation
from app.services.etsy_service import get_etsy_listing


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
    
    # Call the AI model to optimize the listing
    optimization_result = await call_ai_model(
        title=current_title,
        tags=current_tags,
        description=current_description
    )
    
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


async def call_ai_model(
    title: str,
    tags: List[str],
    description: str
) -> Dict:
    """
    Call the AI model to optimize the listing
    
    In a real implementation, this would call the Ollama API with the qwen3:8b model
    """
    try:
        # For development, return mock optimized data
        # In production, this would call the Ollama API
        
        # Example of how the Ollama API call would look:
        # async with httpx.AsyncClient() as client:
        #     response = await client.post(
        #         f"{settings.AI_MODEL_HOST}/api/generate",
        #         json={
        #             "model": settings.AI_MODEL_NAME,
        #             "prompt": f"Optimize this Etsy listing for SEO:\nTitle: {title}\nTags: {', '.join(tags)}\nDescription: {description}",
        #             "stream": False
        #         }
        #     )
        #     result = response.json()
        #     # Parse the AI response...
        
        # For now, return mock data
        return {
            "optimized_title": f"Improved {title} - SEO Enhanced Version with Keywords",
            "optimized_tags": tags + ["additional tag", "seo keyword"],
            "optimized_description": f"Enhanced version of: {description}\n\nWith additional SEO-friendly content that helps buyers find this product more easily.",
            "reasoning": "Added more specific keywords to the title to improve searchability. Added two additional tags that are trending in this category. Enhanced the description with more product details and search-friendly terms."
        }
    except Exception as e:
        # Log the error
        print(f"Error calling AI model: {str(e)}")
        # Return minimal changes as fallback
        return {
            "optimized_title": title,
            "optimized_tags": tags,
            "optimized_description": description,
            "reasoning": "Unable to optimize due to AI service error."
        }


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
