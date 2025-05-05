"""
Test script to demonstrate all templates in action.
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
    """Main function to test all templates."""
    logger.info("Testing all templates")
    
    # Create SEO optimizer
    optimizer = SEOOptimizer()
    template_manager = optimizer.template_manager
    
    # Test T-Shirt template
    logger.info("Testing T-Shirt template")
    intro_text = optimizer._generate_optimized_intro(
        "cat lover", 
        "tshirt", 
        "cat", 
        {}
    )
    
    template = template_manager.get_template("tshirt")
    description = template_manager.apply_template(
        template,
        intro_text,
        product_name="Cat Lover T-Shirt",
        product_type="T-Shirt",
        keywords=["funny cat shirt", "cat lover gift", "cat tshirt"],
        base_keyword="cat lover"
    )
    
    print("\n=== T-Shirt Template Example ===\n")
    print(description)
    
    # Test Sweatshirt template
    logger.info("Testing Sweatshirt template")
    intro_text = optimizer._generate_optimized_intro(
        "cat lover", 
        "sweatshirt", 
        "cat", 
        {}
    )
    
    template = template_manager.get_template("sweatshirt")
    description = template_manager.apply_template(
        template,
        intro_text,
        product_name="Cat Lover Sweatshirt",
        product_type="Sweatshirt",
        keywords=["funny cat sweatshirt", "cat lover gift", "cat hoodie"],
        base_keyword="cat lover"
    )
    
    print("\n=== Sweatshirt Template Example ===\n")
    print(description)
    
    # Test Art Print template
    logger.info("Testing Art Print template")
    intro_text = optimizer._generate_optimized_intro(
        "Van Gogh inspired", 
        "art_print", 
        "cat", 
        {"artist_name": "Van Gogh", "unique_elements": ["Starry Night", "swirling stars"]}
    )
    
    template = template_manager.get_template("art_print")
    description = template_manager.apply_template(
        template,
        intro_text,
        product_name="Van Gogh Inspired Art Print",
        product_type="Art Print",
        keywords=["van gogh", "starry night", "wall art"],
        base_keyword="Van Gogh inspired"
    )
    
    print("\n=== Art Print Template Example ===\n")
    print(description)
    
    # Test Default template
    logger.info("Testing Default template")
    intro_text = optimizer._generate_optimized_intro(
        "dog lover", 
        "mug", 
        "dog", 
        {}
    )
    
    template = template_manager.get_template("default")
    description = template_manager.apply_template(
        template,
        intro_text,
        product_name="Dog Lover Mug",
        product_type="Mug",
        keywords=["funny dog mug", "dog lover gift", "dog coffee cup"],
        base_keyword="dog lover"
    )
    
    print("\n=== Default Template Example ===\n")
    print(description)

if __name__ == "__main__":
    main()