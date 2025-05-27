"""
OpenAI-based SEO Optimizer for Etsy listings.

This module provides an SEO optimization engine that uses OpenAI's API
to generate optimized titles, tags, and descriptions for Etsy listings.
"""

import logging
from typing import Dict, List, Optional, Any

from pod_automation.agents.seo.api_client import SEOApiClient

logger = logging.getLogger(__name__)

class OpenAISEOOptimizer:
    """SEO optimization engine using OpenAI API for Etsy listings."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """Initialize the SEO optimizer.
        
        Args:
            api_key: API key for the external API service
            model: Model to use for optimization
        """
        self.api_client = SEOApiClient(api_key=api_key, model=model)
        logger.info("Initialized OpenAI SEO Optimizer")
        
    def optimize_listing(self, 
                        listing_data: Dict[str, Any],
                        optimize_title: bool = True,
                        optimize_tags: bool = True,
                        optimize_description: bool = True) -> Dict[str, Any]:
        """Optimize an Etsy listing for SEO.
        
        Args:
            listing_data: Dictionary containing listing data
            optimize_title: Whether to optimize the title
            optimize_tags: Whether to optimize the tags
            optimize_description: Whether to optimize the description
            
        Returns:
            Dictionary with optimized listing data
        """
        logger.info(f"Starting SEO optimization for listing: {listing_data.get('title', 'Unknown')[:30]}...")
        
        # Create a copy of the original listing data
        optimized_listing = listing_data.copy()
        
        # Extract necessary information
        title = listing_data.get('title', '')
        description = listing_data.get('description', '')
        
        # Extract category from taxonomy_path if available
        taxonomy_path = listing_data.get('taxonomy_path', [])
        category = taxonomy_path[-1] if taxonomy_path else 'Unknown'
        
        # Optimize title if requested
        if optimize_title and title:
            logger.info(f"Optimizing title for listing: {title[:30]}...")
            try:
                optimized_title = self.api_client.optimize_title(
                    product_title=title,
                    product_description=description,
                    category=category
                )
                optimized_listing['title'] = optimized_title
                logger.info(f"Title optimized successfully")
            except Exception as e:
                logger.error(f"Failed to optimize title: {str(e)}")
                
        # Optimize tags if requested
        if optimize_tags:
            logger.info(f"Generating tags for listing: {title[:30]}...")
            try:
                optimized_tags = self.api_client.optimize_tags(
                    product_title=title,
                    product_description=description,
                    category=category
                )
                optimized_listing['tags'] = optimized_tags
                logger.info(f"Generated {len(optimized_tags)} tags successfully")
            except Exception as e:
                logger.error(f"Failed to optimize tags: {str(e)}")
                
        # Optimize description if requested
        if optimize_description and description:
            logger.info(f"Optimizing description for listing: {title[:30]}...")
            try:
                optimized_description = self.api_client.optimize_description(
                    product_title=title,
                    product_description=description,
                    category=category
                )
                optimized_listing['description'] = optimized_description
                logger.info(f"Description optimized successfully")
            except Exception as e:
                logger.error(f"Failed to optimize description: {str(e)}")
                
        logger.info("SEO optimization completed")
        return optimized_listing
    
    def optimize_title_only(self, title: str, description: str = "", category: str = "Unknown") -> str:
        """Optimize only the title of a listing.
        
        Args:
            title: Original title
            description: Product description for context
            category: Product category
            
        Returns:
            Optimized title
        """
        return self.api_client.optimize_title(title, description, category)
    
    def optimize_tags_only(self, title: str, description: str = "", category: str = "Unknown") -> List[str]:
        """Generate optimized tags for a listing.
        
        Args:
            title: Product title
            description: Product description
            category: Product category
            
        Returns:
            List of optimized tags
        """
        return self.api_client.optimize_tags(title, description, category)
    
    def optimize_description_only(self, title: str, description: str, category: str = "Unknown") -> str:
        """Optimize only the description of a listing.
        
        Args:
            title: Product title
            description: Original description
            category: Product category
            
        Returns:
            Optimized description
        """
        return self.api_client.optimize_description(title, description, category)
    
    def batch_optimize(self, listings: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Optimize multiple listings in batch.
        
        Args:
            listings: List of listing data dictionaries
            **kwargs: Additional arguments passed to optimize_listing
            
        Returns:
            List of optimized listing data dictionaries
        """
        logger.info(f"Starting batch optimization for {len(listings)} listings")
        
        optimized_listings = []
        for i, listing in enumerate(listings):
            logger.info(f"Processing listing {i+1}/{len(listings)}")
            try:
                optimized_listing = self.optimize_listing(listing, **kwargs)
                optimized_listings.append(optimized_listing)
            except Exception as e:
                logger.error(f"Failed to optimize listing {i+1}: {str(e)}")
                # Add original listing if optimization fails
                optimized_listings.append(listing)
                
        logger.info(f"Batch optimization completed. Processed {len(optimized_listings)} listings")
        return optimized_listings
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get optimization statistics.
        
        Returns:
            Dictionary with optimization statistics
        """
        # This is a placeholder for future implementation
        # Could track API usage, success rates, etc.
        return {
            "api_provider": "OpenAI",
            "model": self.api_client.model,
            "status": "active"
        }
