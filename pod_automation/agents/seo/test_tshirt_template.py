"""
Test script to demonstrate the t-shirt template in action.
"""

import os
import sys
import json
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Import the SEO optimizer
from pod_automation.agents.seo.seo_optimizer import SEOOptimizer
from pod_automation.agents.seo.templates.template_manager import TemplateManager

def main():
    """Main function to test the t-shirt template."""
    logger.info("Testing t-shirt template")
    
    # Create SEO optimizer
    optimizer = SEOOptimizer()
    
    # Test with a regular product
    logger.info("Testing with a regular product")
    intro_text = optimizer._generate_optimized_intro(
        "cat lover", 
        "tshirt", 
        "cat", 
        {}
    )
    
    # Get the t-shirt template
    template_manager = optimizer.template_manager
    template = template_manager.get_template("tshirt")
    
    # Apply the template
    description = template_manager.apply_template(
        template,
        intro_text,
        product_name="Cat Lover T-Shirt",
        product_type="T-Shirt",
        keywords=["funny cat shirt", "cat lover gift", "cat tshirt"],
        base_keyword="cat lover"
    )
    
    # Print the result
    print("\n=== T-Shirt Template Example ===\n")
    print(description)
    
    # Test with an artist-inspired product
    logger.info("Testing with an artist-inspired product")
    intro_text = optimizer._generate_optimized_intro(
        "Van Gogh inspired", 
        "tshirt", 
        "cat", 
        {"artist_name": "Van Gogh", "unique_elements": ["Starry Night", "swirling stars"]}
    )
    
    # Apply the template
    description = template_manager.apply_template(
        template,
        intro_text,
        product_name="Van Gogh Inspired T-Shirt",
        product_type="T-Shirt",
        keywords=["van gogh", "starry night", "art tshirt"],
        base_keyword="Van Gogh inspired"
    )
    
    # Print the result
    print("\n=== Artist-Inspired T-Shirt Template Example ===\n")
    print(description)

if __name__ == "__main__":
    main()