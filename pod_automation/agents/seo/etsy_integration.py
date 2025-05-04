"""
Etsy integration for the SEO module.

This module provides functions for retrieving and updating Etsy listings.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from pod_automation.api.etsy_api import EtsyAPI
from pod_automation.agents.seo.db import create_or_update_listing, update_listing_status, add_optimization_history
from pod_automation.agents.seo.optimize_listings import optimize_listing

logger = logging.getLogger(__name__)

class EtsyIntegration:
    """Etsy integration for the SEO module."""

    def __init__(self, etsy_api=None):
        """Initialize Etsy integration.

        Args:
            etsy_api (EtsyAPI, optional): Etsy API client. If not provided, a new one will be created.
        """
        self.etsy = etsy_api or EtsyAPI()

    def is_connected(self) -> bool:
        """Check if connected to Etsy API.

        Returns:
            bool: True if connected, False otherwise
        """
        return self.etsy.validate_connection()

    def fetch_active_listings(self, limit: int = 25, offset: int = 0) -> List[Dict[str, Any]]:
        """Fetch active listings from Etsy.

        Args:
            limit (int, optional): Maximum number of listings to fetch
            offset (int, optional): Offset for pagination

        Returns:
            list: List of listing data
        """
        logger.info(f"Fetching {limit} active listings from Etsy (offset: {offset})")

        try:
            # Check if API credentials are set
            if not self.etsy.api_key or not self.etsy.shop_id:
                logger.error("Etsy API key or shop ID not set. Please check your configuration.")
                return []

            # Check if access token is available
            if not self.etsy.access_token:
                logger.error("Etsy access token not set. Authentication required.")
                return []

            # Fetch listings from Etsy API
            # Note: We're not using the 'includes' parameter because it causes 400 Bad Request errors
            # The Etsy API v3 documentation doesn't clearly specify the correct format for this parameter
            # If additional data is needed, we can fetch it separately using the listing ID
            response = self.etsy.get_listings(
                state="active",
                limit=limit,
                offset=offset
            )

            if not response:
                logger.error("Failed to fetch listings from Etsy: Empty response")
                return []

            if 'results' not in response:
                logger.error(f"Failed to fetch listings from Etsy: Unexpected response format: {response}")
                return []

            listings = response['results']
            logger.info(f"Successfully fetched {len(listings)} listings from Etsy")

            return listings
        except ValueError as ve:
            # This is likely due to missing shop ID
            logger.error(f"Error fetching listings from Etsy: {str(ve)}")
            return []
        except Exception as e:
            logger.error(f"Error fetching listings from Etsy: {str(e)}")
            return []

    def import_listing_to_db(self, etsy_listing: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Import an Etsy listing to the database.

        Args:
            etsy_listing (dict): Etsy listing data

        Returns:
            dict: Imported listing data or None if failed
        """
        try:
            listing_id = etsy_listing.get('listing_id')
            if not listing_id:
                logger.error("Listing ID not found in Etsy listing data")
                return None

            # Extract relevant data
            title = etsy_listing.get('title', '')
            description = etsy_listing.get('description', '')
            tags = etsy_listing.get('tags', [])

            # Prepare data for database
            listing_data = {
                'title_original': title,
                'description_original': description,
                'tags_original': tags,
                'status': 'pending'
            }

            # Save to database
            db_listing = create_or_update_listing(listing_id, listing_data)

            if db_listing:
                logger.info(f"Successfully imported listing {listing_id} to database")
                return db_listing
            else:
                logger.error(f"Failed to import listing {listing_id} to database")
                return None
        except Exception as e:
            logger.error(f"Error importing listing to database: {str(e)}")
            return None

    def import_listings_to_db(self, limit: int = 25, offset: int = 0) -> List[Dict[str, Any]]:
        """Import listings from Etsy to the database.

        Args:
            limit (int, optional): Maximum number of listings to import
            offset (int, optional): Offset for pagination

        Returns:
            list: List of imported listing data
        """
        # Fetch listings from Etsy
        etsy_listings = self.fetch_active_listings(limit, offset)

        if not etsy_listings:
            return []

        # Import each listing to database
        imported_listings = []
        for listing in etsy_listings:
            db_listing = self.import_listing_to_db(listing)
            if db_listing:
                imported_listings.append(db_listing)

        logger.info(f"Successfully imported {len(imported_listings)} listings to database")
        return imported_listings

    def optimize_listing_from_db(self, db_listing: Dict[str, Any], use_advanced_tag_optimizer: bool = True) -> Optional[Dict[str, Any]]:
        """Optimize a listing from the database.

        Args:
            db_listing (dict): Database listing data
            use_advanced_tag_optimizer (bool, optional): Whether to use the advanced tag optimizer

        Returns:
            dict: Optimized listing data or None if failed
        """
        try:
            listing_id = db_listing.get('id')
            etsy_listing_id = db_listing.get('etsy_listing_id')

            if not listing_id or not etsy_listing_id:
                logger.error("Listing ID not found in database listing data")
                return None

            # Prepare data for optimization
            input_data = {
                "title": db_listing.get('title_original', ''),
                "description": db_listing.get('description_original', ''),
                "tags": db_listing.get('tags_original', []),
                "product_type": self._guess_product_type(db_listing.get('title_original', ''))
            }

            # Optimize listing
            optimized = optimize_listing(input_data, use_advanced_tag_optimizer=use_advanced_tag_optimizer)

            if not optimized:
                logger.error(f"Failed to optimize listing {etsy_listing_id}")
                return None

            # Calculate optimization score (simple heuristic)
            score = self._calculate_optimization_score(
                db_listing.get('title_original', ''),
                optimized.get('title', ''),
                db_listing.get('tags_original', []),
                optimized.get('tags', [])
            )

            # Update database with optimized data
            update_data = {
                'title_optimized': optimized.get('title', ''),
                'description_optimized': optimized.get('description', ''),
                'tags_optimized': optimized.get('tags', []),
                'status': 'optimized',
                'optimization_score': score,
                'optimization_date': datetime.now().isoformat()
            }

            updated_listing = create_or_update_listing(etsy_listing_id, update_data)

            if not updated_listing:
                logger.error(f"Failed to update listing {etsy_listing_id} with optimized data")
                return None

            # Add optimization history
            changes = {
                'title': {
                    'before': db_listing.get('title_original', ''),
                    'after': optimized.get('title', '')
                },
                'tags': {
                    'before': db_listing.get('tags_original', []),
                    'after': optimized.get('tags', [])
                }
            }

            add_optimization_history(
                listing_id,
                'full',
                changes,
                algorithm_version='v1',
                performance_metrics={'score': score}
            )

            logger.info(f"Successfully optimized listing {etsy_listing_id}")
            return updated_listing
        except Exception as e:
            logger.error(f"Error optimizing listing: {str(e)}")
            return None

    def update_etsy_listing(self, db_listing: Dict[str, Any]) -> bool:
        """Update an Etsy listing with optimized data.

        Args:
            db_listing (dict): Database listing data

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            etsy_listing_id = db_listing.get('etsy_listing_id')

            if not etsy_listing_id:
                logger.error("Etsy listing ID not found in database listing data")
                return False

            # Check if listing is approved
            if db_listing.get('status') != 'approved':
                logger.error(f"Listing {etsy_listing_id} is not approved for update")
                return False

            # Prepare data for Etsy API
            listing_data = {}

            if db_listing.get('title_optimized'):
                listing_data['title'] = db_listing.get('title_optimized')

            if db_listing.get('description_optimized'):
                listing_data['description'] = db_listing.get('description_optimized')

            if db_listing.get('tags_optimized'):
                # Try sending tags as a simple array of strings
                tags = db_listing.get('tags_optimized', [])
                # Sanitize tags - only use simple alphanumeric tags
                import re
                sanitized_tags = []
                for tag in tags:
                    # Replace underscores with spaces (Etsy might expect spaces instead)
                    tag = tag.replace('_', ' ')
                    # Remove any characters that aren't alphanumeric or spaces
                    tag = re.sub(r'[^a-zA-Z0-9 ]', '', tag)
                    tag = tag.strip()
                    if tag:  # Only add non-empty tags
                        sanitized_tags.append(tag)

                # Limit to 13 tags (Etsy's maximum)
                sanitized_tags = sanitized_tags[:13]

                # Send as an array
                listing_data['tags'] = sanitized_tags

            # Update listing on Etsy
            response = self.etsy.update_listing(etsy_listing_id, listing_data)

            if response and 'listing_id' in response:
                # Update status in database
                update_listing_status(etsy_listing_id, 'updated')
                logger.info(f"Successfully updated listing {etsy_listing_id} on Etsy")
                return True
            else:
                logger.error(f"Failed to update listing {etsy_listing_id} on Etsy")
                return False
        except Exception as e:
            logger.error(f"Error updating listing on Etsy: {str(e)}")
            return False

    def _guess_product_type(self, title: str) -> str:
        """Guess product type from title.

        Args:
            title (str): Listing title

        Returns:
            str: Guessed product type
        """
        title_lower = title.lower()

        if any(keyword in title_lower for keyword in ['tshirt', 't-shirt', 'shirt', 'tee']):
            return 'tshirt'
        elif any(keyword in title_lower for keyword in ['print', 'poster', 'art print', 'wall art']):
            return 'print'
        elif any(keyword in title_lower for keyword in ['mug', 'coffee mug', 'tea cup']):
            return 'mug'
        elif any(keyword in title_lower for keyword in ['hoodie', 'sweatshirt', 'sweater']):
            return 'hoodie'
        elif any(keyword in title_lower for keyword in ['pillow', 'cushion', 'throw pillow']):
            return 'pillow'
        elif any(keyword in title_lower for keyword in ['tote', 'bag', 'tote bag']):
            return 'tote'
        elif any(keyword in title_lower for keyword in ['sticker', 'decal']):
            return 'sticker'
        else:
            return 'other'

    def _calculate_optimization_score(self, original_title: str, optimized_title: str,
                                     original_tags: List[str], optimized_tags: List[str]) -> float:
        """Calculate optimization score.

        Args:
            original_title (str): Original title
            optimized_title (str): Optimized title
            original_tags (list): Original tags
            optimized_tags (list): Optimized tags

        Returns:
            float: Optimization score (0-100)
        """
        score = 50  # Start with neutral score

        # Title length improvement (Etsy recommends 120-140 characters)
        original_title_len = len(original_title)
        optimized_title_len = len(optimized_title)

        if original_title_len < 80 and optimized_title_len >= 120:
            score += 15  # Big improvement
        elif original_title_len < 120 and optimized_title_len >= 120:
            score += 10  # Good improvement
        elif optimized_title_len > original_title_len and optimized_title_len <= 140:
            score += 5  # Some improvement

        # Tag count improvement (Etsy allows up to 13 tags)
        original_tag_count = len(original_tags)
        optimized_tag_count = len(optimized_tags)

        if original_tag_count < 10 and optimized_tag_count >= 13:
            score += 15  # Big improvement
        elif original_tag_count < 13 and optimized_tag_count >= 13:
            score += 10  # Good improvement
        elif optimized_tag_count > original_tag_count:
            score += 5  # Some improvement

        # Tag quality improvement (simple heuristic: longer tags are usually better)
        original_tag_avg_len = sum(len(tag) for tag in original_tags) / max(1, len(original_tags))
        optimized_tag_avg_len = sum(len(tag) for tag in optimized_tags) / max(1, len(optimized_tags))

        if optimized_tag_avg_len > original_tag_avg_len * 1.5:
            score += 10  # Big improvement
        elif optimized_tag_avg_len > original_tag_avg_len * 1.2:
            score += 5  # Good improvement
        elif optimized_tag_avg_len > original_tag_avg_len:
            score += 2  # Some improvement

        # Cap score at 100
        return min(score, 100)


# Initialize Etsy integration
etsy_integration = EtsyIntegration()

# Convenience functions

def fetch_active_listings(limit: int = 25, offset: int = 0) -> List[Dict[str, Any]]:
    """Fetch active listings from Etsy."""
    return etsy_integration.fetch_active_listings(limit, offset)

def import_listings_to_db(limit: int = 25, offset: int = 0) -> List[Dict[str, Any]]:
    """Import listings from Etsy to the database."""
    return etsy_integration.import_listings_to_db(limit, offset)

def optimize_listing_from_db(db_listing: Dict[str, Any], use_advanced_tag_optimizer: bool = True) -> Optional[Dict[str, Any]]:
    """Optimize a listing from the database."""
    return etsy_integration.optimize_listing_from_db(db_listing, use_advanced_tag_optimizer)

def update_etsy_listing(db_listing: Dict[str, Any]) -> bool:
    """Update an Etsy listing with optimized data."""
    return etsy_integration.update_etsy_listing(db_listing)