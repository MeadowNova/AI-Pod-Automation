"""
SEO Optimization Tools for POD Automation System.
Enhances Etsy listings with optimized tags, titles, and descriptions for improved visibility.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from pathlib import Path
import random
import re
import requests
from collections import Counter

# Set up logging
from pod_automation.utils.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Import template manager
try:
    from .templates.template_manager import TemplateManager
except ImportError:
    # Handle the case where the template manager is not yet available
    TemplateManager = None
    logger.warning("TemplateManager not found. Description templates will not be used.")

class SEOOptimizer:
    """Optimizer for enhancing Etsy listings with SEO."""

    def __init__(self, config=None):
        """Initialize SEO optimizer.

        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}

        # Set up directories
        self.data_dir = self.config.get('data_dir', 'data/seo')
        os.makedirs(self.data_dir, exist_ok=True)

        # Load keyword data
        self.keywords = self._load_keywords()
        self.long_tail_keywords = self._load_long_tail_keywords()

        # Load templates
        self.title_templates = self._load_templates('title_templates')
        self.description_templates = self._load_templates('description_templates')

        # Initialize template manager if available
        if TemplateManager is not None:
            try:
                templates_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
                self.template_manager = TemplateManager(templates_dir)
                logger.info("Template manager initialized successfully")
            except Exception as e:
                logger.error(f"Error initializing template manager: {e}")
                self.template_manager = None
        else:
            self.template_manager = None

    def _load_keywords(self):
        """Load keyword data from file or use default.

        Returns:
            dict: Dictionary of keywords with search volume and competition
        """
        # Check if keywords file exists
        keywords_file = os.path.join(self.data_dir, 'keywords.json')

        if os.path.exists(keywords_file):
            try:
                with open(keywords_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading keywords from file: {str(e)}")

        # Use default keywords if file doesn't exist or loading fails
        default_keywords = {
            'cat': {'search_volume': 9500, 'competition': 8.5},
            'cat t-shirt': {'search_volume': 5200, 'competition': 7.2},
            'cat lover': {'search_volume': 4800, 'competition': 6.8},
            'cat gift': {'search_volume': 4500, 'competition': 7.5},
            'funny cat': {'search_volume': 4200, 'competition': 6.5},
            'cute cat': {'search_volume': 3900, 'competition': 6.2},
            'cat mom': {'search_volume': 3600, 'competition': 5.8},
            'cat dad': {'search_volume': 3300, 'competition': 5.5},
            'cat lover gift': {'search_volume': 3000, 'competition': 7.0},
            'cat shirt': {'search_volume': 2800, 'competition': 6.8},
            'cat tee': {'search_volume': 2500, 'competition': 6.5},
            'cat tshirt': {'search_volume': 2300, 'competition': 6.3},
            'cat design': {'search_volume': 2100, 'competition': 5.9},
            'cat illustration': {'search_volume': 1900, 'competition': 5.5},
            'cat art': {'search_volume': 1700, 'competition': 6.2},
            'cat poster': {'search_volume': 1500, 'competition': 5.8},
            'cat wall art': {'search_volume': 1300, 'competition': 5.5},
            'cat pillow': {'search_volume': 1100, 'competition': 5.2},
            'cat home decor': {'search_volume': 900, 'competition': 5.0},
            'cat decor': {'search_volume': 800, 'competition': 4.8}
        }

        # Save default keywords to file
        try:
            with open(keywords_file, 'w') as f:
                json.dump(default_keywords, f, indent=2)
            logger.info(f"Saved default keywords to {keywords_file}")
        except Exception as e:
            logger.error(f"Error saving default keywords to file: {str(e)}")

        return default_keywords

    def _load_long_tail_keywords(self):
        """Load long-tail keyword data from file or use default.

        Returns:
            dict: Dictionary of long-tail keywords with search volume and competition
        """
        # Check if long-tail keywords file exists
        long_tail_file = os.path.join(self.data_dir, 'long_tail_keywords.json')

        if os.path.exists(long_tail_file):
            try:
                with open(long_tail_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading long-tail keywords from file: {str(e)}")

        # Use default long-tail keywords if file doesn't exist or loading fails
        default_long_tail = {
            'cat lover birthday gift': {'search_volume': 850, 'competition': 4.5},
            'funny cat t-shirt for women': {'search_volume': 780, 'competition': 4.2},
            'cute cat shirt for girls': {'search_volume': 720, 'competition': 4.0},
            'black cat halloween shirt': {'search_volume': 680, 'competition': 3.8},
            'cat mom shirt gift': {'search_volume': 650, 'competition': 3.7},
            'cat dad fathers day gift': {'search_volume': 620, 'competition': 3.5},
            'cat lover christmas gift': {'search_volume': 600, 'competition': 4.8},
            'cat themed home decor': {'search_volume': 580, 'competition': 3.2},
            'minimalist cat wall art': {'search_volume': 550, 'competition': 3.0},
            'watercolor cat illustration': {'search_volume': 520, 'competition': 2.8},
            'geometric cat design': {'search_volume': 500, 'competition': 2.7},
            'cat silhouette poster': {'search_volume': 480, 'competition': 2.5},
            'cat quote t-shirt': {'search_volume': 450, 'competition': 3.8},
            'cat pun shirt': {'search_volume': 420, 'competition': 3.5},
            'cat face illustration': {'search_volume': 400, 'competition': 3.2},
            'cat lover throw pillow': {'search_volume': 380, 'competition': 3.0},
            'cat pattern design': {'search_volume': 350, 'competition': 2.8},
            'cat mom and cat dad matching shirts': {'search_volume': 320, 'competition': 2.5},
            'cat with glasses t-shirt': {'search_volume': 300, 'competition': 2.3},
            'cat with bow tie illustration': {'search_volume': 280, 'competition': 2.0}
        }

        # Save default long-tail keywords to file
        try:
            with open(long_tail_file, 'w') as f:
                json.dump(default_long_tail, f, indent=2)
            logger.info(f"Saved default long-tail keywords to {long_tail_file}")
        except Exception as e:
            logger.error(f"Error saving default long-tail keywords to file: {str(e)}")

        return default_long_tail

    def _load_templates(self, template_type):
        """Load templates from file or use default.

        Args:
            template_type (str): Type of templates to load
        Returns:
            list: List of templates
        """
        # Check if templates file exists
        templates_file = os.path.join(self.data_dir, f'{template_type}.json')

        if os.path.exists(templates_file):
            try:
                with open(templates_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading {template_type} from file: {str(e)}")

        # Use default templates if file doesn't exist or loading fails
        if template_type == 'title_templates':
            default_templates = [
                "{keyword} - {product_type} for Cat Lovers",
                "Cute {keyword} {product_type} - Perfect Gift for Cat Lovers",
                "{keyword} {product_type} - Unique Cat Design",
                "Funny {keyword} {product_type} - Cat Lover Gift",
                "{keyword} {product_type} - Cat Mom Gift",
                "{keyword} {product_type} - Cat Dad Gift",
                "Adorable {keyword} {product_type} - Cat Themed Gift",
                "{keyword} {product_type} - Unique Cat Lover Present",
                "Stylish {keyword} {product_type} - Cat Design",
                "{keyword} {product_type} - Perfect for Cat People"
            ]
        elif template_type == 'description_templates':
            default_templates = [
                "Show your love for cats with this adorable {keyword} {product_type}! Perfect for cat lovers, this {product_type} features a unique design that will make you stand out.\n\n"\
                "🐱 PRODUCT DETAILS 🐱\n"\
                "• High-quality {product_type}\n"\
                "• Unique cat design\n"\
                "• Makes a perfect gift for cat lovers\n"\
                "• Available in multiple sizes\n\n"\
                "🎁 PERFECT GIFT 🎁\n"\
                "This {keyword} {product_type} makes a wonderful gift for cat moms, cat dads, or anyone who loves cats. Surprise your cat-loving friends and family with this unique present!\n\n"\
                "📦 SHIPPING 📦\n"\
                "• Made to order just for you\n"\
                "• Ships within 1-3 business days\n"\
                "• Carefully packaged to ensure safe delivery\n\n"\
                "❤️ WHY CUSTOMERS LOVE US ❤️\n"\
                "• High-quality products\n"\
                "• Unique designs\n"\
                "• Fast shipping\n"\
                "• Excellent customer service\n\n"\
                "Order your {keyword} {product_type} today and show your cat love in style!",

                "Calling all cat lovers! This {keyword} {product_type} is purr-fect for showing your love for feline friends. Each {product_type} features a unique cat design that's sure to make you smile.\n\n"\
                "🐱 ABOUT THIS {product_type_upper} 🐱\n"\
                "• Premium quality materials\n"\
                "• Durable and long-lasting\n"\
                "• Unique cat-themed design\n"\
                "• Makes a great conversation starter\n\n"\
                "🎁 GIFT IDEAS 🎁\n"\
                "This {keyword} {product_type} is perfect for:\n"\
                "• Birthday gifts for cat lovers\n"\
                "• Christmas presents\n"\
                "• Mother's Day or Father's Day\n"\
                "• Just because gifts for cat people\n\n"\
                "📦 SHIPPING & HANDLING 📦\n"\
                "• Each {product_type} is made to order with care\n"\
                "• Processing time: 1-3 business days\n"\
                "• Packaged securely for safe delivery\n\n"\
                "❓ QUESTIONS? ❓\n"\
                "Feel free to message us with any questions about this {keyword} {product_type}. We're happy to help!\n\n"\
                "Add this purr-fect {keyword} {product_type} to your cart today!"
            ]
        else:
            default_templates = []

        # Save default templates to file
        try:
            with open(templates_file, 'w') as f:
                json.dump(default_templates, f, indent=2)
            logger.info(f"Saved default {template_type} to {templates_file}")
        except Exception as e:
            logger.error(f"Error saving default {template_type} to file: {str(e)}")

        return default_templates

    def update_keywords_from_etsy(self, query="cat", limit=20):
        """Update keywords based on Etsy search suggestions."""
        logger.info(f"Updating keywords from Etsy search suggestions for query: {query}")

        try:
            # In a real implementation, we would use Etsy's API or scrape search suggestions
            # For this demonstration, we'll simulate the API call

            # Simulate API call delay
            time.sleep(1)

            # Generate simulated search suggestions
            suggestions = [
                f"{query} t-shirt",
                f"{query} lover gift",
                f"{query} art print",
                f"{query} wall art",
                f"{query} poster",
                f"{query} pillow",
                f"{query} mug",
                f"{query} tote bag",
                f"{query} hoodie",
                f"{query} sweatshirt",
                f"funny {query} shirt",
                f"cute {query} design",
                f"{query} lover",
                f"{query} mom gift",
                f"{query} dad gift",
                f"{query} themed gift",
                f"{query} illustration",
                f"{query} artwork",
                f"{query} home decor",
                f"{query} accessories"
            ]

            # Limit suggestions
            suggestions = suggestions[:limit]

            # Generate simulated search volume and competition
            new_keywords = {}
            for suggestion in suggestions:
                search_volume = random.randint(100, 10000)
                competition = round(random.uniform(1, 10), 1)
                new_keywords[suggestion] = {
                    'search_volume': search_volume,
                    'competition': competition
                }

            # Update keywords
            self.keywords.update(new_keywords)

            # Save updated keywords to file
            keywords_file = os.path.join(self.data_dir, 'keywords.json')
            with open(keywords_file, 'w') as f:
                json.dump(self.keywords, f, indent=2)

            logger.info(f"Updated keywords from Etsy search suggestions. Added {len(new_keywords)} keywords.")

            return True

        except Exception as e:
            logger.error(f"Error updating keywords from Etsy: {str(e)}")
            return False

    def generate_long_tail_keywords(self, base_keywords=None, count=20):
        """Generate long-tail keywords from base keywords."""
        logger.info("Generating long-tail keywords")

        # Use provided base keywords or top keywords from self.keywords
        if base_keywords is None:
            # Sort keywords by search volume and get top 5
            sorted_keywords = sorted(
                self.keywords.items(),
                key=lambda x: x[1]['search_volume'],
                reverse=True
            )
            base_keywords = [k for k, _ in sorted_keywords[:5]]

        # Modifiers to create long-tail keywords
        modifiers = {
            'prefix': [
                'cute', 'funny', 'adorable', 'unique', 'custom', 'personalized',
                'handmade', 'vintage', 'retro', 'modern', 'minimalist', 'colorful',
                'black', 'white', 'gray', 'pink', 'blue', 'green', 'purple', 'red'
            ],
            'suffix': [
                'for women', 'for men', 'for girls', 'for boys', 'for kids',
                'gift', 'present', 'birthday gift', 'christmas gift', 'holiday gift',
                'design', 'art', 'illustration', 'artwork', 'print',
                'lover gift', 'themed gift', 'inspired gift'
            ],
            'product': [
                't-shirt', 'shirt', 'tee', 'top', 'sweatshirt', 'hoodie',
                'poster', 'print', 'wall art', 'canvas', 'pillow', 'cushion',
                'mug', 'cup', 'tote bag', 'bag', 'accessory', 'decor', 'decoration'
            ]
        }

        # Generate long-tail keywords
        long_tail = {}
        for _ in range(count):
            # Select random base keyword
            base = random.choice(base_keywords)

            # Select random modifiers
            prefix = random.choice(modifiers['prefix']) if random.random() > 0.3 else ''
            suffix = random.choice(modifiers['suffix']) if random.random() > 0.3 else ''
            product = random.choice(modifiers['product']) if random.random() > 0.3 else ''

            # Combine to create long-tail keyword
            components = [c for c in [prefix, base, product, suffix] if c]
            long_tail_keyword = ' '.join(components)

            # Generate random search volume (50-1000) and competition (1-5)
            search_volume = random.randint(50, 1000)
            competition = round(random.uniform(1, 5), 1)

            long_tail[long_tail_keyword] = {
                'search_volume': search_volume,
                'competition': competition
            }

        # Update long-tail keywords
        self.long_tail_keywords.update(long_tail)

        # Save updated long-tail keywords to file
        long_tail_file = os.path.join(self.data_dir, 'long_tail_keywords.json')
        with open(long_tail_file, 'w') as f:
            json.dump(self.long_tail_keywords, f, indent=2)

        logger.info(f"Generated {len(long_tail)} long-tail keywords")

        return long_tail

    def optimize_tags(self, base_keyword, product_type, count=13):
        """Optimize tags for an Etsy listing."""
        logger.info(f"Optimizing tags for {base_keyword} {product_type}")

        # Combine keywords and long-tail keywords
        all_keywords = {**self.keywords, **self.long_tail_keywords}

        # Filter keywords related to base_keyword and product_type
        related_keywords = {}
        for keyword, data in all_keywords.items():
            if base_keyword.lower() in keyword.lower() or product_type.lower() in keyword.lower():
                related_keywords[keyword] = data

        # If not enough related keywords, add some general cat keywords
        if len(related_keywords) < count:
            for keyword, data in all_keywords.items():
                if keyword not in related_keywords:
                    related_keywords[keyword] = data
                    if len(related_keywords) >= count * 2:
                        break

        # Sort keywords by search volume / competition ratio (higher is better)
        sorted_keywords = sorted(
            related_keywords.items(),
            key=lambda x: x[1]['search_volume'] / max(x[1]['competition'], 0.1),
            reverse=True
        )

        # Select top keywords
        selected_keywords = [k for k, _ in sorted_keywords[:count]]

        # Ensure base_keyword and product_type are included
        if base_keyword not in selected_keywords:
            selected_keywords[-1] = base_keyword

        if product_type not in selected_keywords and len(selected_keywords) > 1:
            selected_keywords[-2] = product_type

        logger.info(f"Generated {len(selected_keywords)} optimized tags")

        return selected_keywords

    def optimize_title(self, base_keyword, product_type, tags=None, important_elements=None, original_title=None):
        """
        Optimize title for an Etsy listing while preserving important elements.

        Args:
            base_keyword (str): The base keyword for optimization
            product_type (str): The product type
            tags (list, optional): List of optimized tags
            important_elements (dict, optional): Dictionary of important elements to preserve
            original_title (str, optional): The original listing title

        Returns:
            str: Optimized title
        """
        logger.info(f"Optimizing title for {base_keyword} {product_type}")

        # Initialize important elements if not provided
        if important_elements is None:
            important_elements = {}

        # Get product-specific templates if available
        product_specific_templates = self._get_product_specific_templates(product_type)

        # If we have product-specific templates, use those, otherwise use general templates
        templates_to_use = product_specific_templates if product_specific_templates else self.title_templates

        # Select a random title template
        template = random.choice(templates_to_use)

        # Format product_type to be properly capitalized
        formatted_product_type = product_type.replace('_', ' ').title()

        # Create a dictionary of placeholder values
        placeholder_values = {
            'keyword': base_keyword,
            'product_type': formatted_product_type,

            # Artist-related placeholders
            'artist': important_elements.get('artist_name', 'Art'),

            # Style-related placeholders
            'style': important_elements.get('art_style', self._get_appropriate_style(product_type)),
            'art_style': important_elements.get('art_style', self._get_appropriate_style(product_type)),
            'art_type': self._get_art_type(product_type),

            # Product-specific placeholders
            'design_feature': self._get_design_feature(base_keyword, product_type),
            'size': self._get_size(product_type),
            'room': self._get_room(product_type),
            'season': self._get_season(),

            # Gift-related placeholders
            'occasion': self._get_occasion(),
            'recipient': self._get_recipient(base_keyword),
        }

        # Replace all placeholders in the template
        title = template
        for placeholder, value in placeholder_values.items():
            placeholder_pattern = '{' + placeholder + '}'
            if placeholder_pattern in title:
                # Ensure value is a string
                if value is None:
                    value = placeholder.title()  # Use capitalized placeholder name as fallback
                title = title.replace(placeholder_pattern, str(value))

        # Add unique elements if available
        unique_elements = important_elements.get('unique_elements', [])
        for element in unique_elements:
            if element and element.lower() not in title.lower():
                if len(title) + len(f" | {element}") <= 135:
                    title += f" | {element}"

        # Remove redundant artist mentions (e.g., "Van Gogh inspired... with Van Gogh Inspired Design")
        artist_name = important_elements.get('artist_name')
        if artist_name:
            # Check for redundant mentions
            artist_pattern = re.compile(f"{re.escape(artist_name)}.*?{re.escape(artist_name)}", re.IGNORECASE)
            if artist_pattern.search(title):
                # Replace the second mention with a generic term
                title = re.sub(f"({re.escape(artist_name)})(.*)({re.escape(artist_name)})",
                              r"\1\2Artistic", title, flags=re.IGNORECASE)

        # Remove redundant product type mentions (e.g., "Halloween cat lover Halloween Decoration")
        product_words = product_type.lower().split('_')
        for word in product_words:
            if len(word) > 3:  # Only check for substantial words
                word_pattern = re.compile(f"\\b{re.escape(word)}\\b.*?\\b{re.escape(word)}\\b", re.IGNORECASE)
                if word_pattern.search(title):
                    # Replace the second mention with a generic term
                    title = re.sub(f"(\\b{re.escape(word)}\\b)(.*?)(\\b{re.escape(word)}\\b)",
                                  r"\1\2", title, flags=re.IGNORECASE, count=1)

        # Fix redundant terms
        title = re.sub(r"(Artistic)\s+(Artistic)", r"\1", title, flags=re.IGNORECASE)
        title = re.sub(r"(Stylish)\s+(Stylish)", r"\1", title, flags=re.IGNORECASE)
        title = re.sub(r"(Unique)\s+(Unique)", r"\1", title, flags=re.IGNORECASE)
        title = re.sub(r"(Decorative)\s+(Decorative)", r"\1", title, flags=re.IGNORECASE)

        # Ensure the title follows the format with pipe separators
        # First, convert any existing commas to pipes if there aren't already pipes
        if '|' not in title:
            title = title.replace(', ', ' | ')
            title = title.replace(' - ', ' | ')

        # Add unique elements if available
        unique_elements = important_elements.get('unique_elements', [])
        for element in unique_elements:
            if element and element.lower() not in title.lower():
                if len(title) + len(f" | {element}") <= 135:
                    title += f" | {element}"

        # Fix any empty pipe segments (||)
        title = re.sub(r'\|\s*\|', '|', title)
        title = re.sub(r'\s*\|\s*$', '', title)  # Remove trailing pipe
        title = re.sub(r'^\s*\|\s*', '', title)  # Remove leading pipe

        # Ensure title is at least 120 characters for better SEO (if we have enough content)
        if len(title) < 120 and tags:
            # Add some top tags to extend the title
            for tag in tags:
                formatted_tag = tag.replace('_', ' ').title()
                if formatted_tag.lower() not in title.lower() and len(title) + len(f" | {formatted_tag}") <= 135:
                    title += f" | {formatted_tag}"
                    # Check if we've reached the minimum length
                    if len(title) >= 120:
                        break

        # If still under 120 characters, add some high-value descriptive phrases
        if len(title) < 120:
            # Product-specific high-value phrases
            product_specific_phrases = {
                "tshirt": [
                    "Soft Cotton Tee",
                    "Unisex Fit",
                    "Graphic Tshirt",
                    "Printed in USA",
                    "Comfortable Fit",
                    "Durable Print",
                    "Machine Washable",
                    "Eco-Friendly Ink"
                ],
                "art_print": [
                    "Gallery Quality",
                    "Archival Paper",
                    "Vibrant Colors",
                    "Museum Quality",
                    "Fine Art Print",
                    "Acid-Free Paper",
                    "Giclee Print",
                    "Ready to Frame"
                ],
                "sweatshirt": [
                    "Cozy Fleece",
                    "Warm Hoodie",
                    "Soft Interior",
                    "Durable Stitching",
                    "Kangaroo Pocket",
                    "Ribbed Cuffs",
                    "Preshrunk Fabric",
                    "Pill-Resistant"
                ],
                "mug": [
                    "Dishwasher Safe",
                    "Microwave Safe",
                    "11oz Ceramic",
                    "Durable Print",
                    "Lead-Free",
                    "Chip-Resistant",
                    "Double-Sided Print",
                    "Glossy Finish"
                ],
                "pillow": [
                    "Hidden Zipper",
                    "Machine Washable",
                    "Soft Polyester",
                    "Vibrant Print",
                    "Durable Cover",
                    "Hypoallergenic",
                    "Removable Insert",
                    "Double-Sided Print"
                ]
            }

            # General high-value phrases for any product
            general_phrases = [
                "Handmade in USA",
                "Small Business",
                "Fast Shipping",
                "Eco-Friendly",
                "Limited Edition",
                "Exclusive Design",
                "Custom Made",
                "Satisfaction Guaranteed"
            ]

            # Determine product category
            product_category = "general"
            for category in product_specific_phrases.keys():
                if category in product_type.lower():
                    product_category = category
                    break

            # Use product-specific phrases if available, otherwise use general phrases
            filler_phrases = product_specific_phrases.get(product_category, general_phrases)

            # Add phrases until we reach the minimum length
            for phrase in filler_phrases:
                if phrase.lower() not in title.lower() and len(title) + len(f" | {phrase}") <= 135:
                    title += f" | {phrase}"
                    # Check if we've reached the minimum length
                    if len(title) >= 120:
                        break

        # Ensure title is not too long (Etsy limit is 140 characters)
        if len(title) > 140:
            # Find the last complete segment before the 137 character limit
            last_pipe = title[:137].rfind(' | ')
            if last_pipe > 0:
                title = title[:last_pipe]
            else:
                title = title[:137]

        # Final check - if still under 120, add more descriptive text with pipes
        if len(title) < 120:
            remaining_length = 140 - len(title)

            # Product-specific fillers
            product_fillers = {
                "tshirt": " | Soft Cotton | Unisex Fit | Graphic Tee | Durable Print | Made in USA",
                "art_print": " | Gallery Quality | Fine Art | Vibrant Colors | Archival Paper | Ready to Frame",
                "sweatshirt": " | Cozy Fleece | Warm Hoodie | Soft Interior | Durable | Preshrunk",
                "mug": " | Ceramic | Dishwasher Safe | Microwave Safe | Durable Print | Lead-Free",
                "pillow": " | Soft Cover | Machine Washable | Vibrant Print | Hidden Zipper | Removable Insert"
            }

            # Determine product category
            product_category = "general"
            for category in product_fillers.keys():
                if category in product_type.lower():
                    product_category = category
                    break

            # Use product-specific filler if available, otherwise use general filler
            if product_category in product_fillers:
                filler = product_fillers[product_category]
            else:
                filler = " | Handmade | Limited Edition | Fast Shipping | Exclusive Design | Small Business"

            # Add filler up to the remaining length
            title += filler[:remaining_length]

        logger.info(f"Generated optimized title: {title}")

        return title

    def _get_product_specific_templates(self, product_type):
        """Get product-specific title templates.

        Args:
            product_type (str): The product type

        Returns:
            list: List of product-specific templates
        """
        # Define templates for specific product types following the exact format requested
        product_templates = {
            # T-Shirt templates
            'tshirt': [
                # Format: [Design Theme] T-Shirt | [Style/Mood] [Product Type] | [Occasion] Gift | [Recipient] Present | [Design Feature] Tee
                "{keyword} T-Shirt | {style} {product_type} | {occasion} Gift | {recipient} Present | {design_feature} Tee",
                "{artist} Inspired T-Shirt | {style} {product_type} | {occasion} Gift | {recipient} Present | {design_feature} Tee",
                "Funny {keyword} T-Shirt | Humorous {product_type} | Coworker Gift | {recipient} Present | {design_feature} Tee",
                "Cute {keyword} T-Shirt | Adorable {product_type} | Birthday Gift | {recipient} Present | {design_feature} Tee",
                "{keyword} T-Shirt | Vintage Style Tee | Holiday Gift | {recipient} Present | Retro Design Shirt"
            ],
            't-shirt': [
                # Format: [Design Theme] T-Shirt | [Style/Mood] [Product Type] | [Occasion] Gift | [Recipient] Present | [Design Feature] Tee
                "{keyword} T-Shirt | {style} {product_type} | {occasion} Gift | {recipient} Present | {design_feature} Tee",
                "{artist} Inspired T-Shirt | {style} {product_type} | {occasion} Gift | {recipient} Present | {design_feature} Tee",
                "Funny {keyword} T-Shirt | Humorous {product_type} | Coworker Gift | {recipient} Present | {design_feature} Tee",
                "Cute {keyword} T-Shirt | Adorable {product_type} | Birthday Gift | {recipient} Present | {design_feature} Tee",
                "{keyword} T-Shirt | Vintage Style Tee | Holiday Gift | {recipient} Present | Retro Design Shirt"
            ],
            't_shirt': [
                # Format: [Design Theme] T-Shirt | [Style/Mood] [Product Type] | [Occasion] Gift | [Recipient] Present | [Design Feature] Tee
                "{keyword} T-Shirt | {style} {product_type} | {occasion} Gift | {recipient} Present | {design_feature} Tee",
                "{artist} Inspired T-Shirt | {style} {product_type} | {occasion} Gift | {recipient} Present | {design_feature} Tee",
                "Funny {keyword} T-Shirt | Humorous {product_type} | Coworker Gift | {recipient} Present | {design_feature} Tee",
                "Cute {keyword} T-Shirt | Adorable {product_type} | Birthday Gift | {recipient} Present | {design_feature} Tee",
                "{keyword} T-Shirt | Vintage Style Tee | Holiday Gift | {recipient} Present | Retro Design Shirt"
            ],

            # Art Print templates
            'art_print': [
                # Format: [Design Theme] Wall Art | [Style] [Art Type] | [Room] Decor | [Occasion] Gift | [Art Style] Print | [Size] Poster
                "{keyword} Wall Art | {style} {art_type} | {room} Decor | {occasion} Gift | {art_style} Print | {size} Poster",
                "{artist} Inspired Wall Art | {style} {art_type} | {room} Decor | {occasion} Gift | {art_style} Print | {size} Poster",
                "{keyword} Wall Art | Funny Art Parody | Living Room Decor | {recipient} Gift | {art_style} Print | {size} Poster",
                "{keyword} Wall Art | Minimalist {art_type} | Home Office Decor | Birthday Gift | {art_style} Print | {size} Poster",
                "{artist} Style Wall Art | {style} {art_type} | Bedroom Decor | Holiday Gift | Fine Art Print | {size} Poster"
            ],
            'poster': [
                # Format: [Design Theme] Wall Art | [Style] [Art Type] | [Room] Decor | [Occasion] Gift | [Art Style] Print | [Size] Poster
                "{keyword} Wall Art | {style} {art_type} | {room} Decor | {occasion} Gift | {art_style} Print | {size} Poster",
                "{artist} Inspired Wall Art | {style} {art_type} | {room} Decor | {occasion} Gift | {art_style} Print | {size} Poster",
                "{keyword} Wall Art | Funny Art Parody | Living Room Decor | {recipient} Gift | {art_style} Print | {size} Poster",
                "{keyword} Wall Art | Minimalist {art_type} | Home Office Decor | Birthday Gift | {art_style} Print | {size} Poster",
                "{artist} Style Wall Art | {style} {art_type} | Bedroom Decor | Holiday Gift | Fine Art Print | {size} Poster"
            ],
            'wall_art': [
                # Format: [Design Theme] Wall Art | [Style] [Art Type] | [Room] Decor | [Occasion] Gift | [Art Style] Print | [Size] Poster
                "{keyword} Wall Art | {style} {art_type} | {room} Decor | {occasion} Gift | {art_style} Print | {size} Poster",
                "{artist} Inspired Wall Art | {style} {art_type} | {room} Decor | {occasion} Gift | {art_style} Print | {size} Poster",
                "{keyword} Wall Art | Funny Art Parody | Living Room Decor | {recipient} Gift | {art_style} Print | {size} Poster",
                "{keyword} Wall Art | Minimalist {art_type} | Home Office Decor | Birthday Gift | {art_style} Print | {size} Poster",
                "{artist} Style Wall Art | {style} {art_type} | Bedroom Decor | Holiday Gift | Fine Art Print | {size} Poster"
            ],

            # Sweatshirt/Hoodie templates
            'sweatshirt': [
                # Format: [Design Theme] Sweatshirt | [Style/Mood] [Product Type] | [Season] Clothing | [Occasion] Gift | [Recipient] Present | Unisex Hoodie
                "{keyword} Sweatshirt | {style} {product_type} | {season} Clothing | {occasion} Gift | {recipient} Present | Unisex Hoodie",
                "{artist} Inspired Sweatshirt | {style} {product_type} | {season} Clothing | {occasion} Gift | {recipient} Present | Unisex Hoodie",
                "Funny {keyword} Sweatshirt | Humorous {product_type} | Winter Clothing | Birthday Gift | {recipient} Present | Unisex Pullover",
                "Cute {keyword} Sweatshirt | Adorable {product_type} | Fall Clothing | Holiday Gift | {recipient} Present | Cozy Hoodie",
                "{keyword} Sweatshirt | Vintage Style {product_type} | Spring Clothing | Christmas Gift | {recipient} Present | Unisex Pullover"
            ],
            'hoodie': [
                # Format: [Design Theme] Sweatshirt | [Style/Mood] [Product Type] | [Season] Clothing | [Occasion] Gift | [Recipient] Present | Unisex Hoodie
                "{keyword} Sweatshirt | {style} {product_type} | {season} Clothing | {occasion} Gift | {recipient} Present | Unisex Hoodie",
                "{artist} Inspired Sweatshirt | {style} {product_type} | {season} Clothing | {occasion} Gift | {recipient} Present | Unisex Hoodie",
                "Funny {keyword} Sweatshirt | Humorous {product_type} | Winter Clothing | Birthday Gift | {recipient} Present | Unisex Pullover",
                "Cute {keyword} Sweatshirt | Adorable {product_type} | Fall Clothing | Holiday Gift | {recipient} Present | Cozy Hoodie",
                "{keyword} Sweatshirt | Vintage Style {product_type} | Spring Clothing | Christmas Gift | {recipient} Present | Unisex Pullover"
            ],
            'pullover': [
                # Format: [Design Theme] Sweatshirt | [Style/Mood] [Product Type] | [Season] Clothing | [Occasion] Gift | [Recipient] Present | Unisex Hoodie
                "{keyword} Sweatshirt | {style} {product_type} | {season} Clothing | {occasion} Gift | {recipient} Present | Unisex Hoodie",
                "{artist} Inspired Sweatshirt | {style} {product_type} | {season} Clothing | {occasion} Gift | {recipient} Present | Unisex Hoodie",
                "Funny {keyword} Sweatshirt | Humorous {product_type} | Winter Clothing | Birthday Gift | {recipient} Present | Unisex Pullover",
                "Cute {keyword} Sweatshirt | Adorable {product_type} | Fall Clothing | Holiday Gift | {recipient} Present | Cozy Hoodie",
                "{keyword} Sweatshirt | Vintage Style {product_type} | Spring Clothing | Christmas Gift | {recipient} Present | Unisex Pullover"
            ],

            # Other product types with adapted templates
            'mug': [
                "{keyword} Coffee Mug | {style} Ceramic Cup | Kitchen Accessory | {occasion} Gift | {recipient} Present | Dishwasher Safe",
                "Funny {keyword} Mug | Humorous Ceramic Cup | Office Accessory | Coworker Gift | {recipient} Present | Microwave Safe",
                "Cute {keyword} Mug | Adorable Coffee Cup | Home Accessory | Birthday Gift | {recipient} Present | Premium Ceramic"
            ],
            'pillow': [
                "{keyword} Throw Pillow | {style} Home Decor | Living Room Accessory | {occasion} Gift | {recipient} Present | Soft Cover",
                "Decorative {keyword} Pillow | {style} Home Decor | Bedroom Accessory | Housewarming Gift | {recipient} Present | Removable Cover",
                "Cute {keyword} Cushion | Adorable Home Decor | Sofa Accessory | Birthday Gift | {recipient} Present | Comfortable Insert"
            ],
            'tote': [
                "{keyword} Tote Bag | {style} Shopping Bag | Eco-Friendly Accessory | {occasion} Gift | {recipient} Present | Durable Canvas",
                "Funny {keyword} Tote | Humorous Shopping Bag | Reusable Accessory | Birthday Gift | {recipient} Present | Spacious Design",
                "Cute {keyword} Bag | Adorable Tote | Everyday Accessory | Holiday Gift | {recipient} Present | Premium Quality"
            ],

            # Generic template for other product types
            'generic': [
                "{keyword} {product_type} | {style} Design | Premium Quality | {occasion} Gift | {recipient} Present | Unique Item",
                "Funny {keyword} {product_type} | Humorous Design | High Quality | Birthday Gift | {recipient} Present | Unique Item",
                "Cute {keyword} {product_type} | Adorable Design | Premium Quality | Holiday Gift | {recipient} Present | Unique Item"
            ]
        }

        # Normalize product type for matching
        normalized_type = product_type.lower().replace(' ', '_')

        # Check for direct match
        if normalized_type in product_templates:
            return product_templates[normalized_type]

        # Check for partial matches
        for key in product_templates:
            if key != 'generic' and (key in normalized_type or normalized_type in key):
                return product_templates[key]

        # No specific match found, return generic templates
        return product_templates['generic']

    def _get_appropriate_style(self, product_type):
        """Get an appropriate style term based on product type."""
        if 'art' in product_type.lower() or 'print' in product_type.lower() or 'poster' in product_type.lower():
            return random.choice(['Minimalist', 'Abstract', 'Impressionist', 'Pop Art', 'Modern Art', 'Contemporary', 'Watercolor', 'Digital Art'])
        elif 'shirt' in product_type.lower() or 'tee' in product_type.lower():
            return random.choice(['Vintage', 'Retro', 'Graphic', 'Funny', 'Cute', 'Aesthetic', 'Minimalist', 'Artistic'])
        elif 'hoodie' in product_type.lower() or 'sweatshirt' in product_type.lower():
            return random.choice(['Oversized', 'Vintage', 'Graphic', 'Aesthetic', 'Streetwear', 'Unisex', 'Retro', 'Minimalist'])
        elif 'pillow' in product_type.lower() or 'decor' in product_type.lower():
            return random.choice(['Boho', 'Farmhouse', 'Modern', 'Minimalist', 'Scandinavian', 'Rustic', 'Coastal', 'Industrial'])
        elif 'mug' in product_type.lower() or 'cup' in product_type.lower():
            return random.choice(['Ceramic', 'Funny', 'Novelty', 'Personalized', 'Custom', 'Handmade', 'Microwave Safe', 'Dishwasher Safe'])
        elif 'tote' in product_type.lower() or 'bag' in product_type.lower():
            return random.choice(['Canvas', 'Organic', 'Eco-Friendly', 'Reusable', 'Recycled', 'Sustainable', 'Heavy Duty', 'Large Capacity'])
        else:
            return random.choice(['Handmade', 'Custom', 'Personalized', 'Unique', 'Handcrafted', 'Limited Edition', 'Exclusive', 'One of a Kind'])

    def _get_design_feature(self, base_keyword, product_type):
        """Get an appropriate design feature based on keyword and product type."""
        if 'cat' in base_keyword.lower():
            return random.choice(['Cat Design', 'Feline Art', 'Cat Lover', 'Kitty Pattern', 'Cat Themed'])
        elif 'dog' in base_keyword.lower():
            return random.choice(['Dog Design', 'Canine Art', 'Dog Lover', 'Puppy Pattern', 'Dog Themed'])
        elif 'funny' in base_keyword.lower():
            return random.choice(['Humorous Design', 'Funny Graphic', 'Joke Art', 'Comedy Design', 'Hilarious Graphic'])
        elif 'art' in base_keyword.lower() or 'artist' in base_keyword.lower():
            return random.choice(['Artistic Design', 'Fine Art', 'Creative Graphic', 'Artistic Pattern', 'Art Inspired'])
        elif 'shirt' in product_type.lower() or 'tee' in product_type.lower():
            return random.choice(['Graphic Design', 'Printed Tee', 'Unique Pattern', 'Artistic Graphic', 'Custom Design'])
        elif 'hoodie' in product_type.lower() or 'sweatshirt' in product_type.lower():
            return random.choice(['Graphic Design', 'Printed Hoodie', 'Unique Pattern', 'Cozy Design', 'Warm Graphic'])
        else:
            return random.choice(['Unique Design', 'Custom Graphic', 'Original Artwork', 'Creative Pattern', 'Artistic Design'])

    def _get_art_type(self, product_type):
        """Get an appropriate art type based on product type."""
        if 'print' in product_type.lower() or 'poster' in product_type.lower():
            return random.choice(['Artwork', 'Illustration', 'Digital Art', 'Fine Art', 'Graphic Art'])
        elif 'wall art' in product_type.lower():
            return random.choice(['Canvas Art', 'Wall Decor', 'Framed Art', 'Gallery Print', 'Wall Hanging'])
        else:
            return random.choice(['Design', 'Artwork', 'Illustration', 'Graphic', 'Pattern'])

    def _get_size(self, product_type):
        """Get an appropriate size based on product type."""
        if 'print' in product_type.lower() or 'poster' in product_type.lower() or 'wall art' in product_type.lower():
            return random.choice(['8x10', '11x14', '16x20', '18x24', 'Multiple Sizes'])
        elif 'shirt' in product_type.lower() or 'tee' in product_type.lower():
            return random.choice(['S-3XL', 'All Sizes', 'Multiple Sizes', 'S to 5XL', 'Unisex Sizes'])
        else:
            return random.choice(['Standard Size', 'Multiple Sizes', 'Custom Size', 'Various Sizes', 'Perfect Size'])

    def _get_room(self, product_type):
        """Get an appropriate room based on product type."""
        if 'print' in product_type.lower() or 'poster' in product_type.lower() or 'wall art' in product_type.lower():
            return random.choice(['Living Room', 'Bedroom', 'Home Office', 'Kitchen', 'Bathroom'])
        elif 'pillow' in product_type.lower() or 'cushion' in product_type.lower():
            return random.choice(['Living Room', 'Bedroom', 'Sofa', 'Couch', 'Bed'])
        elif 'mug' in product_type.lower() or 'cup' in product_type.lower():
            return random.choice(['Kitchen', 'Office', 'Home', 'Desk', 'Workplace'])
        else:
            return random.choice(['Home', 'Office', 'Room', 'Space', 'Interior'])

    def _get_season(self):
        """Get a random season."""
        return random.choice(['Winter', 'Spring', 'Summer', 'Fall', 'All-Season'])

    def _get_occasion(self):
        """Get a random gift occasion."""
        return random.choice(['Birthday', 'Christmas', 'Holiday', 'Anniversary', 'Special'])

    def _get_recipient(self, base_keyword):
        """Get an appropriate recipient based on keyword."""
        if 'cat' in base_keyword.lower():
            return random.choice(['Cat Lover', 'Cat Owner', 'Cat Mom', 'Cat Dad', 'Pet Lover'])
        elif 'dog' in base_keyword.lower():
            return random.choice(['Dog Lover', 'Dog Owner', 'Dog Mom', 'Dog Dad', 'Pet Lover'])
        elif 'art' in base_keyword.lower() or 'artist' in base_keyword.lower():
            return random.choice(['Art Lover', 'Art Enthusiast', 'Artist', 'Art Collector', 'Creative Person'])
        elif 'funny' in base_keyword.lower() or 'humor' in base_keyword.lower():
            return random.choice(['Humor Lover', 'Friend', 'Coworker', 'Family Member', 'Anyone'])
        else:
            return random.choice(['Anyone', 'Friend', 'Family', 'Loved One', 'Yourself'])

    def optimize_description(self, base_keyword, product_type, tags=None, important_elements=None, original_description=None, original_title=None):
        """
        Optimize description for an Etsy listing.

        Args:
            base_keyword (str): The base keyword for optimization
            product_type (str): The product type
            tags (list, optional): List of optimized tags
            important_elements (dict, optional): Dictionary of important elements to preserve
            original_description (str, optional): The original listing description
            original_title (str, optional): The original listing title

        Returns:
            str: Optimized description
        """
        logger.info(f"Optimizing description for {base_keyword} {product_type}")

        # Initialize important elements if not provided
        if important_elements is None:
            important_elements = {}

        # Format product_type to be properly capitalized
        formatted_product_type = product_type.replace('_', ' ').title()

        # Determine the pet type from the base keyword and title
        pet_type = "pet"
        if original_title is None:
            original_title = ""

        if "cat" in base_keyword.lower() or "cat" in original_title.lower():
            pet_type = "cat"
        elif "dog" in base_keyword.lower() or "dog" in original_title.lower():
            pet_type = "dog"

        # Generate the optimized intro paragraph
        intro_text = self._generate_optimized_intro(base_keyword, product_type, pet_type, important_elements)

        # Check if we should use template manager
        if self.template_manager is not None:
            try:
                # Get appropriate template for product type
                template = self.template_manager.get_template(product_type)

                # If we have a template, use it
                if template:
                    # Extract product name from base keyword and product type
                    product_name = f"{base_keyword} {formatted_product_type}"

                    # Apply template with optimized intro
                    description = self.template_manager.apply_template(
                        template,
                        intro_text,
                        product_name=product_name,
                        product_type=formatted_product_type,
                        keywords=tags,
                        base_keyword=base_keyword
                    )

                    logger.info(f"Applied template for {product_type}")
                    logger.info(f"Generated optimized description (length: {len(description)})")
                    return description

            except Exception as e:
                logger.error(f"Error applying template: {e}")
                # Fall back to standard description generation

        # If template manager is not available or failed, use standard method
        # Select a random description template
        template = random.choice(self.description_templates)

        # Replace placeholders
        description = template.replace('{keyword}', base_keyword).replace('{product_type}', formatted_product_type)

        # Replace generic pet references with specific pet type
        if pet_type == "cat":
            description = description.replace("pet lovers", "cat lovers")
            description = description.replace("pet lover", "cat lover")
            description = description.replace("pet people", "cat people")
            description = description.replace("pet-themed", "cat-themed")
            description = description.replace("pet love", "cat love")
            description = description.replace("pet moms", "cat moms")
            description = description.replace("pet dads", "cat dads")
        elif pet_type == "dog":
            # First, replace any cat references with dog references
            description = description.replace("cat lovers", "dog lovers")
            description = description.replace("cat lover", "dog lover")
            description = description.replace("cat people", "dog people")
            description = description.replace("cat-themed", "dog-themed")
            description = description.replace("cat love", "dog love")
            description = description.replace("cat moms", "dog moms")
            description = description.replace("cat dads", "dog dads")
            description = description.replace("cats", "dogs")
            description = description.replace("cat", "dog")
            description = description.replace("feline", "canine")
            description = description.replace("purr", "bark")
            description = description.replace("purr-fect", "paw-fect")

            # Then replace any generic pet references
            description = description.replace("pet lovers", "dog lovers")
            description = description.replace("pet lover", "dog lover")
            description = description.replace("pet people", "dog people")
            description = description.replace("pet-themed", "dog-themed")
            description = description.replace("pet love", "dog love")
            description = description.replace("pet moms", "dog moms")
            description = description.replace("pet dads", "dog dads")

        # Replace product_type_upper with uppercase product_type
        description = description.replace('{product_type_upper}', formatted_product_type.upper())

        # Add artist name if available
        artist_name = important_elements.get('artist_name')
        if artist_name and '{artist}' in description:
            description = description.replace('{artist}', artist_name)
        elif artist_name and artist_name.lower() not in description.lower():
            # Add artist information if not already mentioned
            artist_info = f"\n\n🎨 ARTIST INSPIRATION 🎨\nThis design is inspired by the work of {artist_name}, bringing a touch of fine art to everyday items."
            description = description.replace("\n\n❓ QUESTIONS?", f"{artist_info}\n\n❓ QUESTIONS?")

        # Add art style if available
        art_style = important_elements.get('art_style')
        if art_style and '{style}' in description:
            description = description.replace('{style}', art_style)

        # Add unique elements if available
        unique_elements = important_elements.get('unique_elements', [])
        if unique_elements:
            unique_info = "\n• " + "\n• ".join(unique_elements)
            description = description.replace("• Unique cat design", f"• Unique design featuring:{unique_info}")

        # Add tags as keywords at the end if provided
        if tags:
            description += "\n\n🔍 KEYWORDS: " + ", ".join(tags)

        # Fix any instances of raw product_type with underscores
        description = description.replace("art_print", "Art Print")
        description = description.replace("t_shirt", "T-Shirt")
        description = description.replace("wall_art", "Wall Art")
        description = description.replace("home_decor", "Home Decor")

        logger.info(f"Generated optimized description (length: {len(description)})")

        return description

    def _generate_optimized_intro(self, base_keyword, product_type, pet_type, important_elements):
        """Generate an optimized introduction paragraph for a product description.

        Args:
            base_keyword (str): The base keyword for optimization
            product_type (str): The product type
            pet_type (str): The type of pet (cat, dog, pet)
            important_elements (dict): Dictionary of important elements to preserve

        Returns:
            str: Optimized introduction paragraph
        """
        # Format product_type to be properly capitalized
        formatted_product_type = product_type.replace('_', ' ').title()

        # Get artist name if available
        artist_name = important_elements.get('artist_name')

        # Get art style if available
        art_style = important_elements.get('art_style')

        # Get unique elements if available
        unique_elements = important_elements.get('unique_elements', [])

        # Generate intro based on product type and available elements
        if artist_name:
            # Artist-inspired product
            intro = f"Calling all {pet_type} lovers! This {artist_name} inspired {formatted_product_type} is purr-fect for showing your love for feline friends. "

            if art_style:
                intro += f"Featuring the iconic {art_style} style that made {artist_name} famous, "

            if unique_elements:
                elements_text = ", ".join(unique_elements[:2])
                intro += f"this design showcases {elements_text} in a unique artistic interpretation. "

            intro += f"Each {formatted_product_type} is carefully crafted to bring fine art into your everyday life."

        elif "funny" in base_keyword.lower() or "humor" in base_keyword.lower():
            # Funny product
            intro = f"Show your sense of humor with this hilarious {base_keyword} {formatted_product_type}! "
            intro += f"Perfect for {pet_type} lovers with a good sense of humor, this {formatted_product_type} is sure to get laughs and start conversations. "

            if unique_elements:
                elements_text = ", ".join(unique_elements[:2])
                intro += f"Featuring {elements_text}, this design is both funny and stylish."

        else:
            # Standard product
            intro = f"Show your love for {pet_type}s with this adorable {base_keyword} {formatted_product_type}! "
            intro += f"Perfect for {pet_type} lovers, this {formatted_product_type} features a unique design that will make you stand out. "

            if unique_elements:
                elements_text = ", ".join(unique_elements[:2])
                intro += f"The design showcases {elements_text}, making it a must-have for any {pet_type} enthusiast."

        return intro

    def optimize_listing(self, base_keyword, product_type):
        """Optimize an Etsy listing with tags, title, and description."""
        logger.info(f"Optimizing listing for {base_keyword} {product_type}")

        # Optimize tags
        tags = self.optimize_tags(base_keyword, product_type)

        # Optimize title
        title = self.optimize_title(base_keyword, product_type, tags)

        # Optimize description
        description = self.optimize_description(base_keyword, product_type, tags)

        # Prepare optimized listing data
        optimized_listing = {
            'base_keyword': base_keyword,
            'product_type': product_type,
            'tags': tags,
            'title': title,
            'description': description,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # Save optimized listing
        timestamp = int(time.time())
        safe_keyword = re.sub(r'[^\w\s]', '', base_keyword).replace(' ', '_')
        listing_path = os.path.join(self.data_dir, f"optimized_listing_{safe_keyword}_{timestamp}.json")

        with open(listing_path, 'w') as f:
            json.dump(optimized_listing, f, indent=2)

        logger.info(f"Optimized listing saved to: {listing_path}")

        return optimized_listing

    def analyze_competitor_listings(self, keyword, limit=10):
        """Analyze competitor listings for a keyword."""
        logger.info(f"Analyzing competitor listings for keyword: {keyword}")

        try:
            # In a real implementation, we would use Etsy's API or scrape listings
            # For this demonstration, we'll simulate the API call

            # Simulate API call delay
            time.sleep(1)

            # Generate simulated listings
            listings = []
            for i in range(limit):
                listings.append({
                    'title': f"Simulated {keyword} listing {i+1}",
                    'description': f"This is a simulated description for a {keyword} listing.",
                    'tags': [f"tag{j}" for j in range(1, 14)],
                    'price': random.randint(1500, 5000) / 100.0,
                    'views': random.randint(100, 10000),
                    'favorites': random.randint(10, 1000),
                    'sales': random.randint(1, 100)
                })

            # Analyze titles
            title_words = []
            for listing in listings:
                words = re.findall(r'\b\w+\b', listing['title'].lower())
                title_words.extend(words)
            title_word_counts = Counter(title_words)
            top_title_words = title_word_counts.most_common(20)

            # Analyze tags
            all_tags = []
            for listing in listings:
                all_tags.extend(listing['tags'])
            tag_counts = Counter(all_tags)
            top_tags = tag_counts.most_common(20)

            # Analyze prices
            prices = [listing['price'] for listing in listings]
            avg_price = sum(prices) / len(prices) if prices else 0
            min_price = min(prices) if prices else 0
            max_price = max(prices) if prices else 0

            # Prepare analysis results
            analysis = {
                'keyword': keyword,
                'listings_analyzed': len(listings),
                'top_title_words': top_title_words,
                'top_tags': top_tags,
                'price_analysis': {
                    'average': round(avg_price, 2),
                    'minimum': round(min_price, 2),
                    'maximum': round(max_price, 2)
                },
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            # Save analysis results
            timestamp = int(time.time())
            safe_keyword = re.sub(r'[^\w\s]', '', keyword).replace(' ', '_')
            analysis_path = os.path.join(self.data_dir, f"competitor_analysis_{safe_keyword}_{timestamp}.json")

            with open(analysis_path, 'w') as f:
                json.dump(analysis, f, indent=2)

            logger.info(f"Competitor analysis saved to: {analysis_path}")

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing competitor listings: {str(e)}")
            return None

    def generate_seo_report(self, keyword, product_type):
        """Generate an SEO report for a keyword and product type."""
        logger.info(f"Generating SEO report for {keyword} {product_type}")

        try:
            # Get keyword data
            keyword_data = self.keywords.get(keyword, {'search_volume': 0, 'competition': 0})
            search_volume = keyword_data['search_volume']
            competition = keyword_data['competition']

            # Analyze competitor listings
            competitor_analysis = self.analyze_competitor_listings(keyword)

            # Optimize listing
            optimized_listing = self.optimize_listing(keyword, product_type)

            # Generate report
            report = []
            report.append(f"# SEO Report for {keyword} {product_type}")
            report.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            # Keyword analysis section
            report.append("## Keyword Analysis")
            report.append(f"- **Primary Keyword**: {keyword}")
            report.append(f"- **Search Volume**: {search_volume}")
            report.append(f"- **Competition Level**: {competition}/10")

            if competition > 7:
                competition_level = "High"
                recommendation = "Consider targeting more specific long-tail keywords"
            elif competition > 4:
                competition_level = "Medium"
                recommendation = "Good balance of search volume and competition"
            else:
                competition_level = "Low"
                recommendation = "Great opportunity, but may have lower search volume"

            report.append(f"- **Competition Assessment**: {competition_level}")
            report.append(f"- **Recommendation**: {recommendation}\n")

            # Competitor analysis section
            if competitor_analysis:
                report.append("## Competitor Analysis")
                report.append(f"- **Listings Analyzed**: {competitor_analysis['listings_analyzed']}")

                report.append("\n### Top Title Words")
                for word, count in competitor_analysis['top_title_words'][:10]:
                    report.append(f"- {word}: {count} occurrences")

                report.append("\n### Top Tags")
                for tag, count in competitor_analysis['top_tags'][:10]:
                    report.append(f"- {tag}: {count} occurrences")

                report.append("\n### Price Analysis")
                price_analysis = competitor_analysis['price_analysis']
                report.append(f"- **Average Price**: ${price_analysis['average']}")
                report.append(f"- **Price Range**: ${price_analysis['minimum']} - ${price_analysis['maximum']}")

                # Price recommendation
                recommended_price = round(price_analysis['average'] * 0.9, 2)
                report.append(f"- **Recommended Price**: ${recommended_price} (slightly below average to attract buyers)\n")

            # Optimized listing section
            report.append("## Optimized Listing")
            report.append(f"- **Title**: {optimized_listing['title']}")
            report.append("\n### Optimized Tags")
            for tag in optimized_listing['tags']:
                report.append(f"- {tag}")

            report.append("\n### Optimized Description")
            report.append("```")
            report.append(optimized_listing['description'][:500] + "..." if len(optimized_listing['description']) > 500 else optimized_listing['description'])
            report.append("```\n")

            # SEO Recommendations section
            report.append("## SEO Recommendations")
            report.append("1. **Use all 13 tags** allowed by Etsy to maximize visibility")
            report.append("2. **Include keywords in your title, description, and tags** for better search ranking")
            report.append("3. **Use long-tail keywords** to target specific customer searches")
            report.append("4. **Update your listings regularly** to keep them fresh in search results")
            report.append("5. **Monitor performance** and adjust your SEO strategy based on what works")

            # Save report
            timestamp = int(time.time())
            safe_keyword = re.sub(r'[^\w\s]', '', keyword).replace(' ', '_')
            report_path = os.path.join(self.data_dir, f"seo_report_{safe_keyword}_{timestamp}.md")

            with open(report_path, 'w') as f:
                f.write('\n'.join(report))

            logger.info(f"SEO report saved to: {report_path}")

            return '\n'.join(report)

        except Exception as e:
            logger.error(f"Error generating SEO report: {str(e)}")
            return f"Error generating SEO report: {str(e)}"

def main():
    """Main function to test SEO optimizer."""
    logger.info("Testing SEO Optimizer")

    # Create SEO optimizer
    optimizer = SEOOptimizer()

    # Update keywords from Etsy
    optimizer.update_keywords_from_etsy()

    # Generate long-tail keywords
    optimizer.generate_long_tail_keywords()

    # Test optimizing a listing
    optimized_listing = optimizer.optimize_listing("cat lover", "t-shirt")

    # Generate SEO report
    report = optimizer.generate_seo_report("cat lover", "t-shirt")

    print("SEO Optimization test completed successfully.")
    print(f"Optimized title: {optimized_listing['title']}")
    print(f"Number of optimized tags: {len(optimized_listing['tags'])}")
    print(f"SEO report length: {len(report)} characters")

if __name__ == "__main__":
    main()

