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

def format_tags_for_etsy(tags):
    """
    Format tags for Etsy API submission.

    Etsy requires tags to be a space-separated string with underscores for multi-word tags.

    Args:
        tags (list): List of tags with spaces

    Returns:
        str: Space-separated string with underscores for multi-word tags
    """
    # Replace spaces with underscores in each tag
    formatted_tags = [tag.replace(' ', '_') for tag in tags]

    # Join with spaces for Etsy's format
    return ' '.join(formatted_tags)

def extract_important_elements(title):
    """
    Extracts important elements from a title such as artist names, art styles,
    and unique selling points.

    Args:
        title (str): The original listing title.

    Returns:
        dict: A dictionary containing extracted elements:
            - artist_name (str, optional): Detected artist name
            - art_style (str, optional): Detected art style
            - unique_elements (list): Other unique elements worth preserving
    """
    result = {
        "artist_name": None,
        "art_style": None,
        "unique_elements": []
    }

    # Skip if title is empty
    if not title:
        return result

    # Convert to lowercase for case-insensitive matching
    title_lower = title.lower()

    # List of famous artists to detect
    artists = {
        "van gogh": "Van Gogh",
        "vincent van gogh": "Van Gogh",
        "klimt": "Klimt",
        "gustav klimt": "Klimt",
        "monet": "Monet",
        "claude monet": "Monet",
        "picasso": "Picasso",
        "pablo picasso": "Picasso",
        "dali": "Dali",
        "salvador dali": "Dali",
        "warhol": "Warhol",
        "andy warhol": "Warhol",
        "matisse": "Matisse",
        "henri matisse": "Matisse",
        "mondrian": "Mondrian",
        "piet mondrian": "Mondrian",
        "kandinsky": "Kandinsky",
        "wassily kandinsky": "Kandinsky",
        "da vinci": "Da Vinci",
        "leonardo da vinci": "Da Vinci",
        "michelangelo": "Michelangelo",
        "rembrandt": "Rembrandt",
        "vermeer": "Vermeer",
        "johannes vermeer": "Vermeer",
        "banksy": "Banksy",
        "frida kahlo": "Frida Kahlo",
        "kahlo": "Frida Kahlo",
        "hokusai": "Hokusai",
        "katsushika hokusai": "Hokusai",
        "mucha": "Mucha",
        "alphonse mucha": "Mucha"
    }

    # List of art styles to detect
    art_styles = {
        "impressionist": "Impressionist",
        "impressionism": "Impressionist",
        "abstract": "Abstract",
        "cubism": "Cubist",
        "cubist": "Cubist",
        "surrealism": "Surrealist",
        "surrealist": "Surrealist",
        "pop art": "Pop Art",
        "art nouveau": "Art Nouveau",
        "renaissance": "Renaissance",
        "baroque": "Baroque",
        "minimalist": "Minimalist",
        "expressionist": "Expressionist",
        "expressionism": "Expressionist",
        "art deco": "Art Deco",
        "ukiyo-e": "Ukiyo-e",
        "ukiyo e": "Ukiyo-e",
        "modernist": "Modernist",
        "modernism": "Modernist",
        "post-impressionist": "Post-Impressionist",
        "post impressionist": "Post-Impressionist",
        "watercolor": "Watercolor",
        "pointillism": "Pointillism",
        "pointillist": "Pointillism",
        "realism": "Realism",
        "realistic": "Realism"
    }

    # Famous paintings/works
    famous_works = {
        "starry night": "Starry Night",
        "the kiss": "The Kiss",
        "water lilies": "Water Lilies",
        "sunflowers": "Sunflowers",
        "mona lisa": "Mona Lisa",
        "the scream": "The Scream",
        "the great wave": "The Great Wave",
        "the persistence of memory": "The Persistence of Memory",
        "melting clocks": "The Persistence of Memory",
        "girl with a pearl earring": "Girl with a Pearl Earring",
        "campbell's soup": "Campbell's Soup",
        "campbell soup": "Campbell's Soup",
        "guernica": "Guernica",
        "the birth of venus": "The Birth of Venus"
    }

    # Check for artist names
    for artist_key, artist_name in artists.items():
        if artist_key in title_lower:
            result["artist_name"] = artist_name
            break

    # Check for art styles
    for style_key, style_name in art_styles.items():
        if style_key in title_lower:
            result["art_style"] = style_name
            break

    # Check for famous works
    for work_key, work_name in famous_works.items():
        if work_key in title_lower:
            if "unique_elements" not in result:
                result["unique_elements"] = []
            result["unique_elements"].append(work_name)

    # Extract other potentially unique elements (phrases in quotes, all caps words, etc.)
    # Find text in quotes
    quoted_text = re.findall(r'"([^"]*)"', title)
    quoted_text.extend(re.findall(r"'([^']*)'", title))

    # Find words in ALL CAPS (likely important emphasis)
    all_caps = re.findall(r'\b[A-Z]{2,}\b', title)

    # Add these to unique elements
    result["unique_elements"].extend(quoted_text)
    result["unique_elements"].extend(all_caps)

    return result

def optimize_listing(input_data, use_advanced_tag_optimizer=True):
    """
    Optimizes listing details (tags, title, description) based on input data.

    Args:
        input_data (dict): A dictionary containing:
            - title (str): The original listing title.
            - description (str): The original listing description.
            - tags (str or list): Comma-separated string or list of tags.
            - product_type (str, optional): The type of product (e.g., 'tshirt'). Defaults to 'tshirt'.
        use_advanced_tag_optimizer (bool, optional): Whether to use the advanced tag optimizer. Defaults to True.

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

    # Extract important elements from the title
    important_elements = extract_important_elements(title)

    # Guess a base keyword from the title (improved heuristic)
    base_keyword = "apparel"
    title_words = re.findall(r"\b\w+\b", title.lower()) if title else []

    # Priority keywords with more specific categories
    priority_keywords = {
        # Animals/subjects
        "cat": "cat lover",
        "dog": "dog lover",
        "bird": "bird lover",
        "butterfly": "butterfly",
        "flower": "floral",
        "animal": "animal lover",
        "wildlife": "wildlife",
        # Styles
        "funny": "funny",
        "cute": "cute",
        "vintage": "vintage",
        "retro": "retro",
        "minimalist": "minimalist",
        # Product types
        "art": "art",
        "poster": "poster",
        "print": "art print",
        "mug": "mug",
        "shirt": "t-shirt",
        "tshirt": "t-shirt",
        "t-shirt": "t-shirt",
        "hoodie": "hoodie",
        "pillow": "pillow",
        "blanket": "blanket",
        "tapestry": "tapestry",
        # Occasions
        "gift": "gift",
        "birthday": "birthday gift",
        "christmas": "christmas gift",
        "halloween": "halloween"
    }

    # Check for artist names first (they should take precedence)
    if important_elements.get("artist_name"):
        base_keyword = f"{important_elements['artist_name']} inspired"
    else:
        # Look for priority keywords
        found_keyword = None
        for word, replacement in priority_keywords.items():
            if word in title_words:
                found_keyword = replacement
                break

        if found_keyword:
            base_keyword = found_keyword
        elif title_words:
            # Use the first meaningful word if no priority keyword is found
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
        optimized_title = seo_optimizer.optimize_title(
            base_keyword,
            product_type,
            optimized_tags,
            important_elements=important_elements,
            original_title=title
        )
    except Exception as e:
        logger.error(f"Error optimizing title: {e}")
        optimized_title = title

    # Optimize description (fallback to original description if needed)
    try:
        optimized_description = seo_optimizer.optimize_description(
            base_keyword,
            product_type,
            optimized_tags,
            important_elements=important_elements,
            original_description=description,
            original_title=title
        )
    except Exception as e:
        logger.error(f"Error optimizing description: {e}")
        optimized_description = description

    # Format tags for Etsy API (if needed)
    etsy_formatted_tags = format_tags_for_etsy(optimized_tags)

    return {
        "tags": optimized_tags,
        "tags_etsy_format": etsy_formatted_tags,
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

    import json

    # Test with a regular product
    test_data_1 = {
        "title": "Funny Cat Shirt | Cute Gift for Cat Lovers",
        "description": "A hilarious t-shirt perfect for anyone who loves cats. Made from soft cotton.",
        "tags": "cat, funny shirt, gift, pet lover, feline",
        "product_type": "tshirt"
    }

    # Test with an artist-inspired product
    test_data_2 = {
        "title": "Van Gogh Cat T-Shirt | Starry Night Inspired | Cat Lover Gift",
        "description": "A beautiful t-shirt featuring a cat in the style of Van Gogh's Starry Night. Perfect gift for art lovers and cat enthusiasts.",
        "tags": "van gogh, starry night, cat, art, gift",
        "product_type": "tshirt"
    }

    # Test with a different product type
    test_data_3 = {
        "title": "Klimt Inspired Cat Art Print | The Kiss Parody with Cats | Wall Decor",
        "description": "Beautiful art print featuring cats in the style of Gustav Klimt's famous painting The Kiss.",
        "tags": "klimt, the kiss, cat art, wall decor, art print",
        "product_type": "art_print"
    }

    # Test with a non-art product
    test_data_4 = {
        "title": "Cute Dog Coffee Mug | Perfect Gift for Dog Lovers | Ceramic Cup",
        "description": "A cute coffee mug featuring adorable dogs. Perfect gift for any dog lover.",
        "tags": "dog, coffee mug, gift, pet lover, canine",
        "product_type": "mug"
    }

    # Test with a seasonal product
    test_data_5 = {
        "title": "Halloween Cat Decoration | Spooky Black Cat Ornament | Fall Decor",
        "description": "A spooky black cat decoration perfect for Halloween. Made from durable materials.",
        "tags": "halloween, cat, decoration, spooky, black cat",
        "product_type": "halloween decoration"
    }

    # Run tests with all examples
    print("\n=== Testing Regular Product ===\n")
    result_1 = optimize_listing(test_data_1)
    print(json.dumps(result_1, indent=2))

    print("\n=== Testing Artist-Inspired Product ===\n")
    result_2 = optimize_listing(test_data_2)
    print(json.dumps(result_2, indent=2))

    print("\n=== Testing Different Product Type ===\n")
    result_3 = optimize_listing(test_data_3)
    print(json.dumps(result_3, indent=2))

    print("\n=== Testing Non-Art Product ===\n")
    result_4 = optimize_listing(test_data_4)
    print(json.dumps(result_4, indent=2))

    print("\n=== Testing Seasonal Product ===\n")
    result_5 = optimize_listing(test_data_5)
    print(json.dumps(result_5, indent=2))

    print("\n=== Title Comparison ===\n")
    print(f"Regular Product Title: {result_1['title']}")
    print(f"Artist-Inspired Title: {result_2['title']}")
    print(f"Art Print Title: {result_3['title']}")
    print(f"Non-Art Product Title: {result_4['title']}")
    print(f"Seasonal Product Title: {result_5['title']}")
    print("-----------------------")

    print("\n=== Title Lengths ===\n")
    print(f"Regular Product Title Length: {len(result_1['title'])} chars")
    print(f"Artist-Inspired Title Length: {len(result_2['title'])} chars")
    print(f"Art Print Title Length: {len(result_3['title'])} chars")
    print(f"Non-Art Product Title Length: {len(result_4['title'])} chars")
    print(f"Seasonal Product Title Length: {len(result_5['title'])} chars")
    print("-----------------------")

    print("\n=== Tags Comparison ===\n")
    print(f"Regular Product Tags: {result_1['tags']}")
    print(f"Artist-Inspired Tags: {result_2['tags']}")
    print(f"Art Print Tags: {result_3['tags']}")
    print(f"Non-Art Product Tags: {result_4['tags']}")
    print(f"Seasonal Product Tags: {result_5['tags']}")
    print("-----------------------")

    print("\n=== Etsy-Formatted Tags ===\n")
    print(f"Regular Product Etsy Tags: {result_1['tags_etsy_format']}")
    print(f"Artist-Inspired Etsy Tags: {result_2['tags_etsy_format']}")
    print(f"Art Print Etsy Tags: {result_3['tags_etsy_format']}")
    print(f"Non-Art Product Etsy Tags: {result_4['tags_etsy_format']}")
    print(f"Seasonal Product Etsy Tags: {result_5['tags_etsy_format']}")
    print("-----------------------")
