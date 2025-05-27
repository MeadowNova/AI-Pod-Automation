"""
API Client for external SEO optimization services.

This module provides a client for interacting with external AI APIs (like OpenAI)
to generate SEO-optimized content for Etsy listings.
"""

import os
import logging
from typing import Dict, List, Optional, Union
import openai
import time

logger = logging.getLogger(__name__)

class SEOApiClient:
    """Client for external SEO optimization API services."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        """Initialize the SEO API client.
        
        Args:
            api_key: API key for the service. If None, reads from OPENAI_API_KEY env var.
            model: Model to use for optimization.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API key must be provided or set as OPENAI_API_KEY env var")
        
        self.model = model
        
        # Initialize OpenAI client
        self.client = openai.OpenAI(api_key=self.api_key)
        
        logger.info(f"Initialized SEO API client with model: {model}")
        
    def optimize_title(self, 
                      product_title: str, 
                      product_description: str, 
                      category: str,
                      keywords: List[str] = None) -> str:
        """Optimize a product title for SEO.
        
        Args:
            product_title: Original product title
            product_description: Product description for context
            category: Product category
            keywords: Target keywords to include if possible
            
        Returns:
            Optimized product title
        """
        keywords_str = ", ".join(keywords) if keywords else "N/A"
        
        prompt = f"""
        You are an expert Etsy SEO specialist. Optimize the following product title to maximize search visibility.
        
        ORIGINAL TITLE: {product_title}
        
        PRODUCT DESCRIPTION: {product_description}
        
        CATEGORY: {category}
        
        TARGET KEYWORDS: {keywords_str}
        
        Guidelines:
        - Maximum 140 characters
        - Include primary keywords early
        - Be specific about materials, style, and use case
        - Avoid keyword stuffing
        - Maintain readability and appeal to customers
        
        OPTIMIZED TITLE:
        """
        
        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Etsy SEO specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                max_tokens=100
            )
            
            end_time = time.time()
            logger.debug(f"Title optimization took {end_time - start_time:.2f} seconds")
            
            optimized_title = response.choices[0].message.content.strip()
            # Remove any prefixes like "OPTIMIZED TITLE:" that the model might include
            if ":" in optimized_title and len(optimized_title.split(":", 1)) > 1:
                optimized_title = optimized_title.split(":", 1)[1].strip()
                
            # Ensure title is not too long
            if len(optimized_title) > 140:
                optimized_title = optimized_title[:137] + "..."
                
            logger.info(f"Generated optimized title: {optimized_title}")
            return optimized_title
            
        except Exception as e:
            logger.error(f"Error optimizing title: {str(e)}")
            # Return original title if optimization fails
            return product_title
            
    def optimize_tags(self, 
                     product_title: str, 
                     product_description: str,
                     category: str) -> List[str]:
        """Generate optimized tags for a product.
        
        Args:
            product_title: Product title
            product_description: Product description
            category: Product category
            
        Returns:
            List of optimized tags (up to 13)
        """
        prompt = f"""
        You are an expert Etsy SEO specialist. Generate 13 optimized tags for the following product.
        
        PRODUCT TITLE: {product_title}
        
        PRODUCT DESCRIPTION: {product_description}
        
        CATEGORY: {category}
        
        Guidelines:
        - Each tag should be 1-3 words
        - Include a mix of broad, medium, and specific tags
        - Focus on search terms buyers would use
        - Avoid repeating the same words across tags
        - Maximum 20 characters per tag
        
        Return ONLY a comma-separated list of tags, nothing else.
        """
        
        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Etsy SEO specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            end_time = time.time()
            logger.debug(f"Tags optimization took {end_time - start_time:.2f} seconds")
            
            tags_text = response.choices[0].message.content.strip()
            # Split by comma and clean up each tag
            tags = [tag.strip() for tag in tags_text.split(',')]
            # Filter out empty tags and limit to 13 tags (Etsy maximum)
            tags = [tag for tag in tags if tag and len(tag) <= 20][:13]
            
            logger.info(f"Generated {len(tags)} optimized tags")
            return tags
            
        except Exception as e:
            logger.error(f"Error generating tags: {str(e)}")
            # Return empty list if tag generation fails
            return []
            
    def optimize_description(self, 
                           product_title: str, 
                           product_description: str,
                           category: str) -> str:
        """Optimize a product description for SEO.
        
        Args:
            product_title: Product title
            product_description: Original product description
            category: Product category
            
        Returns:
            Optimized product description
        """
        prompt = f"""
        You are an expert Etsy SEO specialist. Optimize the following product description to maximize search visibility while maintaining sales appeal.
        
        PRODUCT TITLE: {product_title}
        
        ORIGINAL DESCRIPTION: {product_description}
        
        CATEGORY: {category}
        
        Guidelines:
        - Maintain the original information and selling points
        - Improve keyword placement and density
        - Add relevant details about materials, dimensions, and use cases
        - Structure with short paragraphs and bullet points for readability
        - Keep the tone consistent with the original
        
        OPTIMIZED DESCRIPTION:
        """
        
        try:
            start_time = time.time()
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Etsy SEO specialist."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=1000
            )
            
            end_time = time.time()
            logger.debug(f"Description optimization took {end_time - start_time:.2f} seconds")
            
            optimized_description = response.choices[0].message.content.strip()
            # Remove any prefixes like "OPTIMIZED DESCRIPTION:" that the model might include
            if ":" in optimized_description and len(optimized_description.split(":", 1)) > 1:
                optimized_description = optimized_description.split(":", 1)[1].strip()
                
            logger.info(f"Generated optimized description (length: {len(optimized_description)})")
            return optimized_description
            
        except Exception as e:
            logger.error(f"Error optimizing description: {str(e)}")
            # Return original description if optimization fails
            return product_description
