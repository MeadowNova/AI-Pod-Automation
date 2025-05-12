"""
Mock database for testing SEO optimization.

This module provides a mock database for testing SEO optimization without a real database connection.
"""

import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class MockSEODatabase:
    """Mock database for testing SEO optimization."""

    def __init__(self):
        """Initialize mock database."""
        self.keywords = [
            {"keyword": "cat lover", "search_volume": 4800, "competition": 6.8},
            {"keyword": "cat t-shirt", "search_volume": 5200, "competition": 7.2},
            {"keyword": "funny cat", "search_volume": 4200, "competition": 6.5},
            {"keyword": "cat mom", "search_volume": 3800, "competition": 5.9},
            {"keyword": "cat dad", "search_volume": 3200, "competition": 5.5},
            {"keyword": "cat gift", "search_volume": 4500, "competition": 6.2},
            {"keyword": "cat lover gift", "search_volume": 3900, "competition": 6.0},
            {"keyword": "funny cat shirt", "search_volume": 4100, "competition": 6.3},
            {"keyword": "cat tee", "search_volume": 3600, "competition": 5.8},
            {"keyword": "cat lover shirt", "search_volume": 4300, "competition": 6.4}
        ]
        
        self.listings = [
            {
                "id": 1,
                "etsy_listing_id": "12345",
                "title_original": "Cat Lover T-Shirt - Funny Cat Shirt - Cat Mom Gift",
                "tags_original": ["cat", "cat lover", "t-shirt", "funny", "cat mom", "gift"],
                "description_original": "This is a great t-shirt for cat lovers! Perfect for cat moms and cat dads."
            },
            {
                "id": 2,
                "etsy_listing_id": "23456",
                "title_original": "Funny Cat Tee - Cat Dad Shirt - Cat Lover Gift",
                "tags_original": ["cat", "funny cat", "tee", "cat dad", "gift"],
                "description_original": "A hilarious t-shirt for cat dads! Show your love for your feline friends."
            },
            {
                "id": 3,
                "etsy_listing_id": "34567",
                "title_original": "Cat Mom Shirt - Cat Lover Gift - Funny Cat T-Shirt",
                "tags_original": ["cat mom", "cat lover", "gift", "funny", "t-shirt"],
                "description_original": "The perfect gift for cat moms! This t-shirt is comfortable and stylish."
            }
        ]
        
        self.optimization_history = []
        
        logger.info("Initialized mock SEO database")
    
    def is_connected(self):
        """Check if database is connected.
        
        Returns:
            bool: Always True for mock database
        """
        return True
    
    def get_keywords(self, limit=1000):
        """Get keywords from database.
        
        Args:
            limit (int): Maximum number of keywords to return
            
        Returns:
            list: List of keywords
        """
        return self.keywords[:limit]
    
    def get_listings(self, limit=100):
        """Get listings from database.
        
        Args:
            limit (int): Maximum number of listings to return
            
        Returns:
            list: List of listings
        """
        return self.listings[:limit]
    
    def get_listing(self, listing_id):
        """Get listing by ID.
        
        Args:
            listing_id (str): Listing ID
            
        Returns:
            dict: Listing data
        """
        for listing in self.listings:
            if listing["id"] == listing_id or listing["etsy_listing_id"] == listing_id:
                return listing
        return None
    
    def get_listing_by_etsy_id(self, etsy_listing_id):
        """Get listing by Etsy ID.
        
        Args:
            etsy_listing_id (str): Etsy listing ID
            
        Returns:
            dict: Listing data
        """
        for listing in self.listings:
            if listing["etsy_listing_id"] == etsy_listing_id:
                return listing
        return None
    
    def create_or_update_listing(self, etsy_listing_id, listing_data):
        """Create or update listing.
        
        Args:
            etsy_listing_id (str): Etsy listing ID
            listing_data (dict): Listing data
            
        Returns:
            dict: Updated listing data
        """
        # Check if listing exists
        existing_listing = self.get_listing_by_etsy_id(etsy_listing_id)
        
        if existing_listing:
            # Update existing listing
            for key, value in listing_data.items():
                existing_listing[key] = value
            existing_listing["updated_at"] = datetime.now().isoformat()
            return existing_listing
        else:
            # Create new listing
            new_listing = {
                "id": len(self.listings) + 1,
                "etsy_listing_id": etsy_listing_id,
                **listing_data,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            self.listings.append(new_listing)
            return new_listing
    
    def add_optimization_history(self, listing_id, optimization_type, changes, optimizer_version, metrics=None):
        """Add optimization history.
        
        Args:
            listing_id (int): Listing ID
            optimization_type (str): Type of optimization
            changes (dict): Changes made
            optimizer_version (str): Optimizer version
            metrics (dict, optional): Metrics
            
        Returns:
            dict: Optimization history entry
        """
        history_entry = {
            "id": len(self.optimization_history) + 1,
            "listing_id": listing_id,
            "optimization_type": optimization_type,
            "changes": changes,
            "optimizer_version": optimizer_version,
            "metrics": metrics or {},
            "created_at": datetime.now().isoformat()
        }
        self.optimization_history.append(history_entry)
        return history_entry
