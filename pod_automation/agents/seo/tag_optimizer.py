"""
Tag Optimizer for Etsy listings.

This module provides advanced tag optimization functionality for Etsy listings,
including tag categorization, scoring, and standardization.
"""

import csv
import json
import re
import os
import requests
from collections import defaultdict, Counter
import time
import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

class TagOptimizer:
    """Advanced tag optimizer for Etsy listings with category-based optimization."""

    # Default configuration
    DEFAULT_CONFIG = {
        "tag_categories": {
            "product_descriptor": 3,  # Number of tags to include from this category
            "art_style": 3,
            "gift_occasion": 3,
            "style_aesthetic": 2,
            "seasonal_trending": 2
        },
        "review_before_update": True,
        "batch_size": 10,  # Number of listings to process in one batch
        "log_file": "tag_optimization_log.txt"
    }

    # Define tag categories based on the standardization strategy
    TAG_CATEGORIES = {
        "product_descriptor": [
            "cat_art_print", "cat_tshirt", "cat_pillow_cover", "cat_wall_art",
            "cat_home_decor", "cat_poster", "cat_apparel", "cat_mug", "cat_tote",
            "cat_phone_case", "cat_sticker", "cat_tapestry", "cat_blanket"
        ],
        "art_style": [
            "klimt_cat_art", "van_gogh_cat", "starry_night_cat", "mona_lisa_cat",
            "art_nouveau_cat", "impressionist_cat_art", "ukiyo_e_cat", "pop_art_cat",
            "abstract_cat_art", "surrealist_cat", "renaissance_cat", "cubist_cat",
            "banksy_cat", "matisse_cat", "monet_cat", "picasso_cat", "dali_cat"
        ],
        "gift_occasion": [
            "cat_lover_gift", "art_lover_gift", "cat_mom_gift", "cat_dad_gift",
            "unique_gift_idea", "birthday_gift", "christmas_gift", "mothers_day_gift",
            "fathers_day_gift", "graduation_gift", "housewarming_gift", "wedding_gift"
        ],
        "style_aesthetic": [
            "funny_cat_art", "cat_parody_art", "famous_painting_parody", "humorous_wall_art",
            "cat_wall_decor", "minimalist_cat_art", "vintage_cat_art", "retro_cat_design",
            "modern_cat_art", "cute_cat_design", "whimsical_cat_art", "quirky_cat_art"
        ],
        "seasonal_trending": [
            "winter_cat_art", "valentines_day_gift", "spring_cat_art", "summer_cat_art",
            "fall_cat_art", "halloween_cat_decor", "thanksgiving_gift", "christmas_cat_gift",
            "holiday_cat_decor", "autumn_home_decor", "winter_home_decor", "spring_home_decor"
        ]
    }

    # Define common variations and their standardized forms
    TAG_VARIATIONS = {
        r"cat\s*shirt": "cat_tshirt",
        r"cat\s*tee": "cat_tshirt",
        r"cat\s*t-shirt": "cat_tshirt",
        r"cat\s*art\s*print": "cat_art_print",
        r"cat\s*poster": "cat_art_print",
        r"cat\s*wall\s*art": "cat_wall_art",
        r"cat\s*wall\s*decor": "cat_wall_decor",
        r"cat\s*home\s*decor": "cat_home_decor",
        r"cat\s*lover\s*gift": "cat_lover_gift",
        r"gift\s*for\s*cat\s*lover": "cat_lover_gift",
        r"cat\s*mom\s*gift": "cat_mom_gift",
        r"gift\s*for\s*cat\s*mom": "cat_mom_gift",
        r"cat\s*dad\s*gift": "cat_dad_gift",
        r"gift\s*for\s*cat\s*dad": "cat_dad_gift",
        r"art\s*lover\s*gift": "art_lover_gift",
        r"gift\s*for\s*art\s*lover": "art_lover_gift",
        r"funny\s*cat": "funny_cat_art",
        r"cat\s*parody": "cat_parody_art",
        r"famous\s*painting\s*parody": "famous_painting_parody",
        r"painting\s*parody": "famous_painting_parody",
        r"art\s*parody": "famous_painting_parody",
        r"klimt\s*cat": "klimt_cat_art",
        r"gustav\s*klimt\s*cat": "klimt_cat_art",
        r"van\s*gogh\s*cat": "van_gogh_cat",
        r"starry\s*night\s*cat": "starry_night_cat",
        r"mona\s*lisa\s*cat": "mona_lisa_cat",
        r"da\s*vinci\s*cat": "mona_lisa_cat",
        r"monet\s*cat": "monet_cat",
        r"picasso\s*cat": "picasso_cat",
        r"dali\s*cat": "dali_cat",
        r"matisse\s*cat": "matisse_cat",
        r"banksy\s*cat": "banksy_cat",
        r"impressionist\s*cat": "impressionist_cat_art",
        r"art\s*nouveau\s*cat": "art_nouveau_cat",
        r"renaissance\s*cat": "renaissance_cat",
        r"ukiyo\s*e\s*cat": "ukiyo_e_cat",
        r"pop\s*art\s*cat": "pop_art_cat",
        r"abstract\s*cat": "abstract_cat_art",
        r"surrealist\s*cat": "surrealist_cat",
        r"cubist\s*cat": "cubist_cat",
        r"minimalist\s*cat": "minimalist_cat_art",
        r"vintage\s*cat": "vintage_cat_art",
        r"retro\s*cat": "retro_cat_design",
        r"modern\s*cat": "modern_cat_art",
        r"cute\s*cat": "cute_cat_design",
        r"whimsical\s*cat": "whimsical_cat_art",
        r"quirky\s*cat": "quirky_cat_art",
        r"winter\s*cat": "winter_cat_art",
        r"spring\s*cat": "spring_cat_art",
        r"summer\s*cat": "summer_cat_art",
        r"fall\s*cat": "fall_cat_art",
        r"autumn\s*cat": "fall_cat_art",
        r"halloween\s*cat": "halloween_cat_decor",
        r"christmas\s*cat": "christmas_cat_gift",
        r"holiday\s*cat": "holiday_cat_decor",
        r"valentine\s*cat": "valentines_day_gift",
        r"thanksgiving\s*cat": "thanksgiving_gift"
    }

    def __init__(self, config=None):
        """Initialize the tag optimizer.

        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = self.DEFAULT_CONFIG.copy()
        if config:
            self.config.update(config)

        # Set up logging
        self.log_file = self.config.get("log_file", "tag_optimization_log.txt")

        # Initialize eRank data containers
        self.erank_data = {}
        self.trending_tags = []

        logger.info("TagOptimizer initialized")

    def log_message(self, message):
        """Write a message to the log file with timestamp."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.log_file, "a") as f:
            f.write(f"[{timestamp}] {message}\n")
        logger.info(message)

    def load_erank_keyword_data(self, file_path):
        """Load keyword data exported from eRank.

        Args:
            file_path (str): Path to the eRank keyword data CSV file

        Returns:
            dict: Dictionary of keyword data
        """
        keywords_data = {}

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    keyword = row.get('Keyword', '').lower().strip()
                    if keyword:
                        keywords_data[keyword] = {
                            'search_volume': int(row.get('Search Volume', 0)),
                            'competition': int(row.get('Competition', 50)),
                            'engagement': int(row.get('Engagement', 0)),
                            'trend': row.get('Trend', 'stable')
                        }
            self.log_message(f"Loaded {len(keywords_data)} keywords from eRank export file")
            self.erank_data = keywords_data
            return keywords_data
        except FileNotFoundError:
            self.log_message(f"eRank export file not found: {file_path}")
            return {}
        except Exception as e:
            self.log_message(f"Error loading eRank export: {str(e)}")
            return {}

    def load_trending_tags(self, file_path):
        """Load trending tags exported from eRank Trend Buzz.

        Args:
            file_path (str): Path to the eRank trending tags CSV file

        Returns:
            list: List of trending tags
        """
        trending_tags = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    keyword = row.get('Keyword', '').lower().strip()
                    if keyword:
                        trending_tags.append(keyword)
            self.log_message(f"Loaded {len(trending_tags)} trending tags from eRank export file")
            self.trending_tags = trending_tags
            return trending_tags
        except FileNotFoundError:
            self.log_message(f"eRank trending tags file not found: {file_path}")
            return []
        except Exception as e:
            self.log_message(f"Error loading eRank trending tags: {str(e)}")
            return []

    def standardize_tag(self, tag):
        """Standardize a single tag based on defined variations and patterns.

        Args:
            tag (str): The tag to standardize

        Returns:
            str: Standardized tag
        """
        # Convert to lowercase and remove any extra spaces
        tag = tag.lower().strip()

        # Replace underscores with spaces
        tag = tag.replace('_', ' ')

        # Remove special characters except spaces
        tag = re.sub(r'[^\w\s]', '', tag)

        # Remove duplicate spaces
        tag = re.sub(r'\s+', ' ', tag)

        # Remove leading/trailing spaces
        tag = tag.strip()

        # Check if it matches any of our variation patterns
        tag_with_spaces = tag
        for pattern, replacement in self.TAG_VARIATIONS.items():
            if re.search(pattern, tag_with_spaces, re.IGNORECASE):
                # Convert replacement from underscore format to space format
                return replacement.replace('_', ' ')

        # Return the standardized tag with spaces (not underscores)
        return tag

    def categorize_tag(self, tag):
        """Determine which category a tag belongs to.

        Args:
            tag (str): The tag to categorize

        Returns:
            str: Category name
        """
        standardized = self.standardize_tag(tag)

        # Convert predefined categories from underscore format to space format
        space_format_categories = {}
        for category, tags in self.TAG_CATEGORIES.items():
            space_format_categories[category] = [t.replace('_', ' ') for t in tags]

        # Check if it's in our predefined categories
        for category, tags in space_format_categories.items():
            if standardized in tags:
                return category

        # Try to infer category based on patterns
        if any(keyword in standardized for keyword in ['shirt', 'tee', 'apparel', 'clothing']):
            return "product_descriptor"
        elif any(keyword in standardized for keyword in ['art', 'print', 'poster', 'wall']):
            return "product_descriptor"
        elif any(keyword in standardized for keyword in ['gift', 'present']):
            return "gift_occasion"
        elif any(artist in standardized for artist in ['klimt', 'van gogh', 'monet', 'picasso', 'dali']):
            return "art_style"
        elif any(keyword in standardized for keyword in ['funny', 'humor', 'parody', 'whimsical']):
            return "style_aesthetic"
        elif any(season in standardized for season in ['winter', 'spring', 'summer', 'fall', 'christmas', 'halloween']):
            return "seasonal_trending"

        # Default category if we can't determine
        return "uncategorized"

    def score_tag(self, tag, erank_data=None):
        """Score a tag based on eRank data (if available) and other factors.

        Args:
            tag (str): The tag to score
            erank_data (dict, optional): eRank keyword data

        Returns:
            int: Score from 0-100
        """
        score = 50  # Default score

        # Use instance erank_data if not provided
        if erank_data is None:
            erank_data = self.erank_data

        # Get eRank data if available
        if erank_data and tag in erank_data:
            keyword_data = erank_data[tag]

            # Adjust score based on search volume (0-100)
            search_volume = keyword_data.get("search_volume", 0)
            score += min(search_volume / 10, 30)  # Max 30 points for search volume

            # Adjust score based on competition (0-100, lower is better)
            competition = keyword_data.get("competition", 50)
            score += max(0, (100 - competition) / 5)  # Max 20 points for low competition

        # Bonus points for specific categories
        category = self.categorize_tag(tag)
        if category == "product_descriptor":
            score += 5
        elif category == "gift_occasion":
            score += 3
        elif category == "seasonal_trending":
            score += 2

        # Bonus for long-tail keywords (3+ words)
        words = tag.split()
        if len(words) >= 3:
            score += 5

        # Cap score at 100
        return min(score, 100)

    def optimize_tags(self, original_tags, title, product_type=None):
        """Generate optimized tags based on original tags, title, and available data.

        Args:
            original_tags (list): List of original tags
            title (str): Listing title
            product_type (str, optional): Product type

        Returns:
            list: List of optimized tags (max 13)
        """
        logger.info(f"Optimizing tags for title: {title}")

        # Handle string input for original_tags
        if isinstance(original_tags, str):
            original_tags = [tag.strip() for tag in original_tags.split(',') if tag.strip()]

        # Parse and standardize original tags
        original_tags = [tag.strip() for tag in original_tags if tag.strip()]
        standardized_original = [self.standardize_tag(tag) for tag in original_tags]

        # Extract potential tags from title
        title_words = re.findall(r'\b\w+\b', title.lower())

        # Create bigrams and trigrams from title for more relevant multi-word tags
        title_bigrams = [f"{title_words[i]} {title_words[i+1]}" for i in range(len(title_words)-1)]
        title_trigrams = [f"{title_words[i]} {title_words[i+1]} {title_words[i+2]}" for i in range(len(title_words)-2)]

        # Determine the product category for base tags
        product_category = "other"
        if product_type:
            normalized_type = product_type.lower().replace('-', ' ').replace('_', ' ')
            if any(term in normalized_type for term in ['shirt', 'tee', 'tshirt', 'apparel', 'clothing']):
                product_category = "tshirt"
            elif any(term in normalized_type for term in ['print', 'poster', 'wall art', 'art']):
                product_category = "art_print"
            elif any(term in normalized_type for term in ['mug', 'cup']):
                product_category = "mug"
            elif any(term in normalized_type for term in ['pillow', 'cushion']):
                product_category = "pillow"
            elif any(term in normalized_type for term in ['halloween', 'christmas']):
                product_category = "seasonal"

        # Define base tags for each product category
        base_tags = {
            "tshirt": [
                "funny cat shirt",
                "cat lover gift",
                "cat tshirt",
                "cat lover tee",
                "cat graphic tee",
                "cat clothing",
                "feline shirt"
            ],
            "art_print": [
                "wall art",
                "home decor",
                "art print",
                "funny art",
                "art parody",
                "wall decor",
                "art poster"
            ],
            "mug": [
                "coffee mug",
                "funny mug",
                "cat lover mug",
                "ceramic mug",
                "cat coffee cup",
                "gift mug",
                "cat mug"
            ],
            "pillow": [
                "throw pillow",
                "decorative pillow",
                "cat pillow",
                "home decor",
                "cat lover gift",
                "sofa cushion",
                "cat decor"
            ],
            "seasonal": [
                "halloween decor",
                "cat decoration",
                "seasonal decor",
                "holiday gift",
                "cat lover gift",
                "spooky decor",
                "fall decoration"
            ],
            "other": [
                "cat lover gift",
                "funny cat gift",
                "cat themed",
                "cat lover",
                "cat gift",
                "cat present",
                "feline gift"
            ]
        }

        # Customize base tags based on keywords in title
        # Replace "cat" with other animals if detected
        animal_keywords = {
            "dog": ["dog", "puppy", "canine"],
            "bird": ["bird", "avian", "feathered"],
            "rabbit": ["rabbit", "bunny", "hare"],
            "fox": ["fox", "vulpine"],
            "wolf": ["wolf", "wolves", "lupine"]
        }

        detected_animal = "cat"  # Default
        for animal, keywords in animal_keywords.items():
            if any(keyword in title.lower() for keyword in keywords):
                detected_animal = animal
                break

        # Replace "cat" with detected animal in base tags
        if detected_animal != "cat":
            updated_base_tags = []
            for tag in base_tags[product_category]:
                updated_base_tags.append(tag.replace("cat", detected_animal).replace("feline", animal_keywords.get(detected_animal, [detected_animal])[0]))
            base_tags[product_category] = updated_base_tags

        # Generate design-specific tags
        design_specific_tags = []

        # Extract key themes from title
        key_themes = []

        # Check for artist names
        artists = {
            "van gogh": ["van gogh", "starry night", "sunflowers", "impressionist"],
            "klimt": ["klimt", "the kiss", "art nouveau", "gold leaf"],
            "monet": ["monet", "water lilies", "impressionist", "garden"],
            "picasso": ["picasso", "cubist", "abstract", "modern art"],
            "dali": ["dali", "surrealist", "melting clocks", "surrealism"]
        }

        detected_artist = None
        for artist, keywords in artists.items():
            if any(keyword in title.lower() for keyword in keywords):
                detected_artist = artist
                key_themes.extend(keywords)
                break

        # Check for themes
        themes = {
            "business": ["business", "office", "work", "professional", "suit", "tie"],
            "funny": ["funny", "humor", "joke", "hilarious", "comedy", "lol"],
            "cute": ["cute", "adorable", "kawaii", "sweet", "lovely"],
            "vintage": ["vintage", "retro", "classic", "old school", "nostalgic"],
            "holiday": ["christmas", "halloween", "thanksgiving", "holiday", "festive"]
        }

        detected_themes = []
        for theme, keywords in themes.items():
            if any(keyword in title.lower() for keyword in keywords):
                detected_themes.append(theme)
                key_themes.extend([k for k in keywords if k in title.lower()])

        # Add bigrams and trigrams that contain key themes
        for bigram in title_bigrams:
            if any(theme in bigram.lower() for theme in key_themes):
                design_specific_tags.append(bigram)

        for trigram in title_trigrams:
            if any(theme in trigram.lower() for theme in key_themes):
                design_specific_tags.append(trigram)

        # Add artist-specific tags if detected
        if detected_artist:
            if detected_artist == "van gogh":
                design_specific_tags.extend([
                    "van gogh parody",
                    "starry night art",
                    f"{detected_animal} art print",
                    f"{detected_animal} wall art",
                    "famous painting",
                    "art history"
                ])
            elif detected_artist == "klimt":
                design_specific_tags.extend([
                    "klimt parody",
                    "the kiss art",
                    f"{detected_animal} art print",
                    "art nouveau",
                    "famous painting",
                    "art history"
                ])
            elif detected_artist == "monet":
                design_specific_tags.extend([
                    "monet parody",
                    "water lilies art",
                    f"{detected_animal} art print",
                    "impressionist art",
                    "famous painting",
                    "art history"
                ])

        # Add theme-specific tags
        for theme in detected_themes:
            if theme == "business":
                design_specific_tags.extend([
                    f"business {detected_animal}",
                    f"office {detected_animal}",
                    f"{detected_animal} in suit",
                    "work humor",
                    "office humor",
                    f"professional {detected_animal}"
                ])
            elif theme == "funny":
                design_specific_tags.extend([
                    f"funny {detected_animal}",
                    f"humorous {detected_animal}",
                    f"{detected_animal} humor",
                    "funny gift",
                    "joke gift",
                    "novelty gift"
                ])
            elif theme == "cute":
                design_specific_tags.extend([
                    f"cute {detected_animal}",
                    f"adorable {detected_animal}",
                    f"kawaii {detected_animal}",
                    "cute gift",
                    f"{detected_animal} lover",
                    "animal lover gift"
                ])

        # If we don't have enough design-specific tags, add from original tags and title
        if len(design_specific_tags) < 6:
            # Add original tags that aren't already in design_specific_tags
            for tag in original_tags:
                if tag not in design_specific_tags and len(design_specific_tags) < 6:
                    design_specific_tags.append(tag)

            # Add significant words from title
            significant_words = [word for word in title_words if len(word) > 3 and word not in ['with', 'and', 'for', 'the', 'this', 'that', 'from', 'your']]
            for word in significant_words:
                if len(design_specific_tags) < 6:
                    if word not in [tag.split()[-1] for tag in design_specific_tags]:
                        design_specific_tags.append(word)

        # Combine base tags and design-specific tags
        result_tags = base_tags[product_category][:7]  # Take up to 7 base tags
        result_tags.extend(design_specific_tags[:6])   # Take up to 6 design-specific tags

        # Ensure we don't exceed 13 tags (Etsy's limit)
        result_tags = result_tags[:13]

        # Clean up tags before finalizing
        cleaned_tags = []
        for tag in result_tags:
            # Fix redundant word patterns (e.g., "cute_cute_cup")
            tag = re.sub(r'(\w+)_\1', r'\1', tag)

            # Fix redundant compound tags (e.g., "halloween_halloween_")
            tag = re.sub(r'^(\w+)_\1_', r'\1_', tag)

            # Ensure no tag exceeds 20 characters (Etsy's limit)
            # But try to preserve complete words by finding the last underscore before char 20
            if len(tag) > 20:
                last_underscore = tag[:20].rfind('_')
                if last_underscore > 0:
                    tag = tag[:last_underscore]
                else:
                    tag = tag[:20]

            # Skip very short tags
            if len(tag) < 4:
                continue

            cleaned_tags.append(tag)

        # Remove any duplicate tags (case insensitive)
        unique_tags = []
        seen = set()
        for tag in cleaned_tags:
            if tag.lower() not in seen:
                unique_tags.append(tag)
                seen.add(tag.lower())

        logger.info(f"Generated {len(unique_tags)} optimized tags")
        return unique_tags

    def process_listings_batch(self, listings):
        """Process a batch of listings and generate optimized tags.

        Args:
            listings (list): List of listing dictionaries with 'title' and 'tags' keys

        Returns:
            list: List of result dictionaries with original and optimized tags
        """
        results = []

        for i, listing in enumerate(listings):
            # Extract title and tags
            title = listing.get('title', '')
            tags = listing.get('tags', [])

            # Determine product type from title
            product_type = None
            title_lower = title.lower()
            if 'tshirt' in title_lower or 't-shirt' in title_lower or 'shirt' in title_lower:
                product_type = 'tshirt'
            elif 'print' in title_lower or 'poster' in title_lower or 'art' in title_lower:
                product_type = 'art_print'
            elif 'pillow' in title_lower or 'cushion' in title_lower:
                product_type = 'pillow_cover'

            # Generate optimized tags
            optimized_tags = self.optimize_tags(tags, title, product_type)

            # Create result object
            result = {
                'listing_id': listing.get('listing_id'),
                'title': title,
                'original_tags': tags,
                'optimized_tags': optimized_tags
            }
            results.append(result)

            # Log progress
            if (i + 1) % 10 == 0:
                self.log_message(f"Processed {i + 1} listings...")

        return results

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Create tag optimizer
    optimizer = TagOptimizer()

    # Test with a sample listing
    sample_listing = {
        'title': 'Funny Cat T-Shirt, Perfect Gift for Cat Lovers, Klimt Inspired Art',
        'tags': ['cat', 'funny', 'tshirt', 'gift', 'art', 'klimt']
    }

    # Process the sample listing
    results = optimizer.process_listings_batch([sample_listing])

    # Print results
    for result in results:
        print(f"Title: {result['title']}")
        print(f"Original tags: {result['original_tags']}")
        print(f"Optimized tags: {result['optimized_tags']}")