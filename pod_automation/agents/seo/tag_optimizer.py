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
        # Convert to lowercase and remove any spaces
        tag = tag.lower().strip()
        
        # Replace underscores with spaces for pattern matching
        tag_with_spaces = tag.replace('_', ' ')
        
        # Check if it matches any of our variation patterns
        for pattern, replacement in self.TAG_VARIATIONS.items():
            if re.search(pattern, tag_with_spaces, re.IGNORECASE):
                return replacement
        
        # If no match found, convert spaces to underscores and return
        return tag.replace(' ', '_')
    
    def categorize_tag(self, tag):
        """Determine which category a tag belongs to.
        
        Args:
            tag (str): The tag to categorize
            
        Returns:
            str: Category name
        """
        standardized = self.standardize_tag(tag)
        
        # Check if it's in our predefined categories
        for category, tags in self.TAG_CATEGORIES.items():
            if standardized in tags:
                return category
        
        # Try to infer category based on patterns
        if any(keyword in standardized for keyword in ['shirt', 'tee', 'apparel', 'clothing']):
            return "product_descriptor"
        elif any(keyword in standardized for keyword in ['art', 'print', 'poster', 'wall']):
            return "product_descriptor"
        elif any(keyword in standardized for keyword in ['gift', 'present']):
            return "gift_occasion"
        elif any(artist in standardized for artist in ['klimt', 'van_gogh', 'monet', 'picasso', 'dali']):
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
        words = tag.split('_')
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
        title_bigrams = [f"{title_words[i]}_{title_words[i+1]}" for i in range(len(title_words)-1)]
        potential_title_tags = [self.standardize_tag(word) for word in title_words + title_bigrams]
        
        # Categorize all potential tags
        all_potential_tags = standardized_original + potential_title_tags
        categorized = defaultdict(list)
        for tag in all_potential_tags:
            category = self.categorize_tag(tag)
            if tag not in categorized[category]:
                categorized[category].append(tag)
        
        # Add trending tags if available
        if self.trending_tags:
            for tag in self.trending_tags:
                standardized_tag = self.standardize_tag(tag)
                if standardized_tag not in categorized["seasonal_trending"]:
                    categorized["seasonal_trending"].append(standardized_tag)
        
        # Score all tags
        scored_tags = {}
        for category, tags in categorized.items():
            scored_tags[category] = [(tag, self.score_tag(tag)) for tag in tags]
            # Sort by score, highest first
            scored_tags[category].sort(key=lambda x: x[1], reverse=True)
        
        # Select the best tags from each category based on configuration
        result_tags = []
        for category, count in self.config["tag_categories"].items():
            selected = [tag for tag, score in scored_tags.get(category, [])[:count]]
            result_tags.extend(selected)
        
        # If we don't have enough tags, add from uncategorized
        uncategorized = [tag for tag, score in scored_tags.get("uncategorized", [])
                        if tag not in result_tags]
        result_tags.extend(uncategorized[:13-len(result_tags)])
        
        # Ensure we don't exceed 13 tags (Etsy's limit)
        result_tags = result_tags[:13]
        
        logger.info(f"Generated {len(result_tags)} optimized tags")
        return result_tags
    
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