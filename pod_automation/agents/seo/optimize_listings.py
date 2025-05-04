import re
import logging
from datetime import datetime
from pod_automation.agents.seo.seo_optimizer import SEOOptimizer
from pod_automation.agents.seo.tag_optimizer import TagOptimizer

# Set up logging
logger = logging.getLogger(__name__)

# Initialize the optimizers
seo_optimizer = SEOOptimizer()
tag_optimizer = TagOptimizer()

def clean_tags(tag_input):
    """Cleans a string or list of tags into a list of non-empty strings."""
    if isinstance(tag_input, list):
        return [t.strip() for t in tag_input if t and isinstance(t, str) and t.strip()]
    if isinstance(tag_input, str):
        return [t.strip() for t in tag_input.split(',') if t and t.strip()]
    return []

def optimize_listing(input_data, use_advanced_tag_optimizer=False):
    """
    Optimizes listing details (tags, title, description) based on input data.

    Args:
        input_data (dict): A dictionary containing:
            - title (str): The original listing title.
            - description (str): The original listing description.
            - tags (str or list): Comma-separated string or list of tags.
            - product_type (str, optional): The type of product (e.g., 'tshirt'). Defaults to 'tshirt'.
        use_advanced_tag_optimizer (bool, optional): Whether to use the advanced tag optimizer. Defaults to False.

    Returns:
        dict: A dictionary containing the optimized listing details:
            - tags (list): List of optimized tags.
            - title (str): Optimized title.
            - description (str): Optimized description.
            - base_keyword (str): The guessed base keyword used for optimization.
            - product_type (str): The product type used.
            - timestamp (str): ISO format timestamp of when optimization occurred.
    """
    title = input_data.get("title", "") or ""
    description = input_data.get("description", "") or ""
    tags_raw = input_data.get("tags", "") or ""
    product_type = input_data.get("product_type") or "tshirt"

    # Clean tags input into a list
    raw_tags = clean_tags(tags_raw)

    # Guess a base keyword from the title (simple heuristic)
    base_keyword = "apparel"
    title_words = re.findall(r"\b\w+\b", title.lower()) if title else []
    priority_keywords = ["cat", "dog", "funny", "cute", "art", "gift", "poster", "mug", "shirt"]
    found_keyword = None
    for word in priority_keywords:
        if word in title_words:
            found_keyword = "cat lover" if word == "cat" else ("dog lover" if word == "dog" else word)
            break
    if found_keyword:
        base_keyword = found_keyword
    elif title_words:
        base_keyword = title_words[0]

    # Optimize tags using the appropriate optimizer (with fallback to original tags if failure)
    try:
        if use_advanced_tag_optimizer:
            logger.info("Using advanced tag optimizer")
            optimized_tags = tag_optimizer.optimize_tags(raw_tags, title, product_type)
        else:
            logger.info("Using standard SEO optimizer for tags")
            optimized_tags = seo_optimizer.optimize_tags(base_keyword, product_type)
    except Exception as e:
        logger.error(f"Error generating optimized tags: {e}")
        optimized_tags = raw_tags

    # Optimize title (fallback to original title if needed)
    try:
        optimized_title = seo_optimizer.optimize_title(base_keyword, product_type, optimized_tags)
    except Exception as e:
        logger.error(f"Error optimizing title: {e}")
        optimized_title = title

    # Optimize description (fallback to original description if needed)
    try:
        optimized_description = seo_optimizer.optimize_description(base_keyword, product_type, optimized_tags)
    except Exception as e:
        logger.error(f"Error optimizing description: {e}")
        optimized_description = description

    return {
        "tags": optimized_tags,
        "title": optimized_title,
        "description": optimized_description,
        "base_keyword": base_keyword,
        "product_type": product_type,
        "timestamp": datetime.now().isoformat()
    }

# Example usage for testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    test_data = {
        "title": "Funny Cat Shirt, Cute Gift for Cat Lovers",
        "description": "A hilarious t-shirt perfect for anyone who loves cats. Made from soft cotton.",
        "tags": "cat, funny shirt, gift, pet lover, feline",
        "product_type": "tshirt"
    }
    
    # Test with standard optimizer
    print("\n=== Testing with Standard Optimizer ===\n")
    standard_optimized = optimize_listing(test_data, use_advanced_tag_optimizer=False)
    import json
    print(json.dumps(standard_optimized, indent=2))
    
    # Test with advanced tag optimizer
    print("\n=== Testing with Advanced Tag Optimizer ===\n")
    advanced_optimized = optimize_listing(test_data, use_advanced_tag_optimizer=True)
    print(json.dumps(advanced_optimized, indent=2))
    
    print("\n=== Comparison ===\n")
    print(f"Standard tags: {standard_optimized['tags']}")
    print(f"Advanced tags: {advanced_optimized['tags']}")
    print("-----------------------")
