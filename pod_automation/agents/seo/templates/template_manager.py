"""
Template Manager for SEO description templates.

This module provides functionality to load, store, and apply description templates
for different product types.
"""

import os
import logging
import re
from pathlib import Path

# Set up logging
logger = logging.getLogger(__name__)

class TemplateManager:
    """Manages description templates for different product types."""
    
    def __init__(self, templates_dir=None):
        """Initialize the template manager.
        
        Args:
            templates_dir (str, optional): Directory containing template files
        """
        if templates_dir is None:
            # Default to the 'templates' directory in the same folder as this file
            self.templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)))
        else:
            self.templates_dir = templates_dir
            
        # Dictionary to store loaded templates
        self.templates = {}
        
        # Load templates if directory exists
        if os.path.exists(self.templates_dir):
            self.load_templates()
        else:
            logger.warning(f"Templates directory not found: {self.templates_dir}")
    
    def load_templates(self):
        """Load all template files from the templates directory."""
        template_files = [f for f in os.listdir(self.templates_dir) 
                         if f.endswith('.txt') and not f.startswith('_')]
        
        for filename in template_files:
            try:
                # Extract product type from filename (e.g., tshirt_template.txt -> tshirt)
                product_type = filename.split('_')[0].lower()
                
                # Load template content
                template_path = os.path.join(self.templates_dir, filename)
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                
                # Store template
                self.templates[product_type] = template_content
                logger.info(f"Loaded template for {product_type}")
                
            except Exception as e:
                logger.error(f"Error loading template {filename}: {e}")
    
    def get_template(self, product_type):
        """Get a template for a specific product type.
        
        Args:
            product_type (str): Product type (e.g., 'tshirt', 'sweatshirt', 'art_print')
            
        Returns:
            str: Template content or None if not found
        """
        # Normalize product type
        normalized_type = product_type.lower().replace(' ', '_').replace('-', '_')
        
        # Try to find an exact match
        if normalized_type in self.templates:
            return self.templates[normalized_type]
        
        # Try to find a partial match
        for template_type, template in self.templates.items():
            if template_type in normalized_type or normalized_type in template_type:
                logger.info(f"Using {template_type} template for {product_type}")
                return template
        
        # Fall back to default template if available
        if 'default' in self.templates:
            logger.info(f"Using default template for {product_type}")
            return self.templates['default']
        
        # No template found
        logger.warning(f"No template found for {product_type}")
        return None
    
    def apply_template(self, template, intro_text, product_name=None, product_type=None, keywords=None):
        """Apply a template, replacing placeholders with actual content.
        
        Args:
            template (str): Template content
            intro_text (str): Optimized introduction text
            product_name (str, optional): Product name to replace in template
            product_type (str, optional): Product type to replace in template
            keywords (list, optional): Keywords to include in the template
            
        Returns:
            str: Filled template
        """
        if not template:
            return intro_text
        
        # Create a copy of the template
        result = template
        
        # Replace intro placeholder with optimized intro text
        intro_placeholder = "{INTRO}"
        if intro_placeholder in result:
            result = result.replace(intro_placeholder, intro_text)
        else:
            # If no intro placeholder, prepend the intro text
            result = intro_text + "\n\n" + result
        
        # Replace product name placeholder
        if product_name:
            result = result.replace("{PRODUCT_NAME}", product_name)
        
        # Replace product type placeholder
        if product_type:
            result = result.replace("{PRODUCT_TYPE}", product_type)
        
        # Replace keywords placeholder
        if keywords and isinstance(keywords, list):
            keywords_text = ", ".join(keywords)
            result = result.replace("{KEYWORDS}", keywords_text)
        
        return result
    
    def extract_intro(self, description):
        """Extract the introduction paragraph from a description.
        
        Args:
            description (str): Full product description
            
        Returns:
            str: Introduction paragraph
        """
        if not description:
            return ""
        
        # Try to find the first paragraph (text before first empty line)
        paragraphs = description.split("\n\n")
        if paragraphs:
            return paragraphs[0]
        
        # If no paragraphs found, return the first 200 characters
        return description[:200]
    
    def save_template(self, product_type, template_content):
        """Save a template for a specific product type.
        
        Args:
            product_type (str): Product type (e.g., 'tshirt', 'sweatshirt', 'art_print')
            template_content (str): Template content
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Normalize product type
            normalized_type = product_type.lower().replace(' ', '_').replace('-', '_')
            
            # Create filename
            filename = f"{normalized_type}_template.txt"
            filepath = os.path.join(self.templates_dir, filename)
            
            # Save template
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(template_content)
            
            # Update in-memory template
            self.templates[normalized_type] = template_content
            
            logger.info(f"Saved template for {product_type}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving template for {product_type}: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create template manager
    template_manager = TemplateManager()
    
    # Example template
    tshirt_template = """
{INTRO}

🔍 PRODUCT DETAILS 🔍
• Premium quality {PRODUCT_TYPE}
• Soft and comfortable fabric
• Durable print that won't fade
• Available in multiple sizes and colors

🎁 PERFECT GIFT 🎁
This {PRODUCT_NAME} makes a wonderful gift for anyone who loves unique designs.

📦 SHIPPING 📦
• Made to order just for you
• Ships within 1-3 business days
• Carefully packaged to ensure safe delivery

❤️ WHY CUSTOMERS LOVE US ❤️
• High-quality products
• Unique designs
• Fast shipping
• Excellent customer service

🔎 KEYWORDS: {KEYWORDS}
"""
    
    # Save example template
    template_manager.save_template("tshirt", tshirt_template)
    
    # Test applying template
    intro_text = "Show your unique style with this awesome t-shirt featuring a cool design!"
    product_name = "Awesome T-Shirt"
    product_type = "t-shirt"
    keywords = ["funny shirt", "cool tshirt", "unique design", "gift idea"]
    
    filled_template = template_manager.apply_template(
        tshirt_template, 
        intro_text, 
        product_name, 
        product_type, 
        keywords
    )
    
    print(filled_template)