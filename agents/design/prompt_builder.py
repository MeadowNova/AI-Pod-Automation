import json
import os

def load_config(config_path="agent_config.json"):
    """
    Load the agent configuration from a JSON file.
    The config should include SEO rules such as title templates, description sections, and tag rules.
    """
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            return json.load(f)
    # Return default config if not available
    return {
        "title_templates": ["{keyword} - {product_type} for Cat Lovers"],
        "description_sections": ["Introduction", "Product Details", "Call to Action"],
        "tag_rules": {
            "max_tags": 13,
            "min_length": 3
        }
    }

def build_prompt(listing_data: dict) -> str:
    """
    Build a prompt for the AI optimizer.
    
    Parameters:
      - listing_data: a dictionary with keys 'title', 'description', 'tags', and 'product_type'
    
    Returns:
      A string prompt that includes the listing details and configuration instructions.
    """
    config = load_config()
    title_templates = config.get("title_templates", [])
    description_sections = config.get("description_sections", [])
    tag_rules = config.get("tag_rules", {})
    
    prompt = "You are an Etsy SEO expert. Optimize the following listing for maximum visibility.\n\n"
    prompt += f"Title: {listing_data.get('title', '')}\n"
    prompt += f"Description: {listing_data.get('description', '')}\n"
    prompt += f"Tags: {listing_data.get('tags', '')}\n"
    prompt += f"Product Type: {listing_data.get('product_type', '')}\n\n"
    prompt += "Optimization Instructions:\n"
    
    if title_templates:
        prompt += "- Use one of these title templates: " + ", ".join(title_templates) + "\n"
    if description_sections:
        prompt += "- Follow this description structure: " + " | ".join(description_sections) + "\n"
    if tag_rules:
        prompt += "- Apply these tag rules: " + json.dumps(tag_rules) + "\n"
    
    prompt += "\nGenerate an optimized title, a refined description, and an optimized set of tags (as a comma-separated string)."
    return prompt

# Example usage
if __name__ == "__main__":
    listing_example = {
        "title": "Funny Cat T-Shirt for Cat Lovers",
        "description": "A playful tee for cat enthusiasts.",
        "tags": "cat, funny, t-shirt",
        "product_type": "tshirt"
    }
    prompt = build_prompt(listing_example)
    print("Generated Prompt:\n", prompt)
