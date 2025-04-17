import re
from datetime import datetime
from seo_optimizer import SEOOptimizer

# Initialize the SEO optimizer
optimizer = SEOOptimizer()

def clean_tags(tag_input):
    """Cleans a string or list of tags into a list of non-empty strings."""
    if isinstance(tag_input, list):
        return [t.strip() for t in tag_input if t and isinstance(t, str) and t.strip()]
    if isinstance(tag_input, str):
        return [t.strip() for t in tag_input.split(',') if t and t.strip()]
    return []

def optimize_listing(input_data):
    """
    Optimizes listing details (tags, title, description) based on input data.
    
    Args:
        input_data (dict): A dictionary containing:
            - title (str): The original listing title.
            - description (str): The original listing description.
            - tags (str or list): Comma-separated string or list of tags.
            - product_type (str, optional): The type of product (e.g., 'tshirt'). Defaults to 'tshirt'.
    
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
    
    # Optimize tags using SEOOptimizer (with fallback to original tags if failure)
    try:
        optimized_tags = optimizer.optimize_tags(base_keyword, product_type)
    except Exception as e:
        print(f"Error generating optimized tags: {e}")
        optimized_tags = raw_tags
    
    # Optimize title (fallback to original title if needed)
    try:
        optimized_title = optimizer.optimize_title(base_keyword, product_type, optimized_tags)
    except Exception as e:
        print(f"Error optimizing title: {e}")
        optimized_title = title
    
    # Optimize description (fallback to original description if needed)
    try:
        optimized_description = optimizer.optimize_description(base_keyword, product_type, optimized_tags)
    except Exception as e:
        print(f"Error optimizing description: {e}")
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
    test_data = {
        "title": "Funny Cat Shirt, Cute Gift for Cat Lovers",
        "description": "A hilarious t-shirt perfect for anyone who loves cats. Made from soft cotton.",
        "tags": "cat, funny shirt, gift, pet lover, feline",
        "product_type": "tshirt"
    }
    optimized_data = optimize_listing(test_data)
    print("--- Optimization Test ---")
    import json
    print(json.dumps(optimized_data, indent=2))
    print("-----------------------")
