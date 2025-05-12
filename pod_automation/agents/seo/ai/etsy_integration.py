"""
Integration with Etsy API for AI-enhanced SEO optimization.

This module provides functions to integrate the AI-enhanced SEO optimization with the Etsy API.
"""

import os
import sys
import json
import logging
from datetime import datetime
import time
from typing import Dict, List, Any, Optional

from pod_automation.agents.seo.etsy_integration import EtsyAPI
from pod_automation.agents.seo.db import seo_db
from pod_automation.agents.seo.ai.ai_seo_optimizer import AISEOOptimizer
from pod_automation.agents.seo.ai.optimization_tracker import OptimizationTracker

logger = logging.getLogger(__name__)

class AIEtsyIntegration:
    """Integration with Etsy API for AI-enhanced SEO optimization."""
    
    def __init__(self, etsy_api=None, optimizer=None, tracker=None):
        """Initialize Etsy integration.
        
        Args:
            etsy_api (EtsyAPI, optional): Etsy API client
            optimizer (AISEOOptimizer, optional): AI SEO optimizer
            tracker (OptimizationTracker, optional): Optimization tracker
        """
        # Initialize Etsy API client
        self.etsy = etsy_api or EtsyAPI()
        
        # Initialize AI SEO optimizer
        self.optimizer = optimizer or AISEOOptimizer()
        
        # Initialize optimization tracker
        self.tracker = tracker or OptimizationTracker(seo_db)
        
        logger.info("Initialized AI Etsy integration")
    
    def fetch_listings(self, status="active", limit=10):
        """Fetch listings from Etsy.
        
        Args:
            status (str): Listing status (active, draft, inactive)
            limit (int): Maximum number of listings to fetch
            
        Returns:
            list: List of listings
        """
        logger.info(f"Fetching {limit} {status} listings from Etsy")
        
        try:
            # Fetch listings from Etsy
            listings = self.etsy.get_listings(status=status, limit=limit)
            
            if not listings:
                logger.warning(f"No {status} listings found")
                return []
            
            logger.info(f"Fetched {len(listings)} {status} listings from Etsy")
            
            # Process listings
            processed_listings = []
            for listing in listings:
                # Extract listing data
                etsy_listing_id = listing.get("listing_id")
                title = listing.get("title", "")
                description = listing.get("description", "")
                tags = listing.get("tags", [])
                
                # Create listing data
                listing_data = {
                    "etsy_listing_id": etsy_listing_id,
                    "title_original": title,
                    "description_original": description,
                    "tags_original": tags,
                    "status": "pending",
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                # Save to database
                saved_listing = seo_db.create_or_update_listing(etsy_listing_id, listing_data)
                
                if saved_listing:
                    processed_listings.append(saved_listing)
                else:
                    logger.error(f"Failed to save listing {etsy_listing_id}")
            
            return processed_listings
        except Exception as e:
            logger.error(f"Error fetching listings from Etsy: {str(e)}")
            return []
    
    def optimize_listings(self, status="pending", limit=10):
        """Optimize listings.
        
        Args:
            status (str): Listing status to optimize
            limit (int): Maximum number of listings to optimize
            
        Returns:
            list: List of optimized listings
        """
        logger.info(f"Optimizing {limit} {status} listings")
        
        try:
            # Get listings from database
            listings = seo_db.get_listings(status=status, limit=limit)
            
            if not listings:
                logger.warning(f"No {status} listings found")
                return []
            
            logger.info(f"Found {len(listings)} {status} listings to optimize")
            
            # Optimize each listing
            optimized_listings = []
            for listing in listings:
                etsy_listing_id = listing.get("etsy_listing_id")
                
                logger.info(f"Optimizing listing {etsy_listing_id}")
                
                # Optimize listing
                optimized = self.optimizer.optimize_listing_ai(etsy_listing_id, listing)
                
                if optimized:
                    optimized_listings.append(optimized)
                    logger.info(f"Successfully optimized listing {etsy_listing_id}")
                else:
                    logger.error(f"Failed to optimize listing {etsy_listing_id}")
            
            return optimized_listings
        except Exception as e:
            logger.error(f"Error optimizing listings: {str(e)}")
            return []
    
    def update_listings(self, status="approved", limit=10):
        """Update listings on Etsy.
        
        Args:
            status (str): Listing status to update
            limit (int): Maximum number of listings to update
            
        Returns:
            list: List of updated listings
        """
        logger.info(f"Updating {limit} {status} listings on Etsy")
        
        try:
            # Get listings from database
            listings = seo_db.get_listings(status=status, limit=limit)
            
            if not listings:
                logger.warning(f"No {status} listings found")
                return []
            
            logger.info(f"Found {len(listings)} {status} listings to update")
            
            # Update each listing
            updated_listings = []
            for listing in listings:
                etsy_listing_id = listing.get("etsy_listing_id")
                
                logger.info(f"Updating listing {etsy_listing_id} on Etsy")
                
                # Prepare update data
                update_data = {
                    "title": listing.get("title_optimized"),
                    "description": listing.get("description_optimized"),
                    "tags": listing.get("tags_optimized")
                }
                
                # Update listing on Etsy
                updated = self.etsy.update_listing(etsy_listing_id, update_data)
                
                if updated:
                    # Update status in database
                    seo_db.update_listing_status(etsy_listing_id, "updated")
                    
                    # Add to updated listings
                    updated_listings.append(listing)
                    
                    logger.info(f"Successfully updated listing {etsy_listing_id} on Etsy")
                else:
                    logger.error(f"Failed to update listing {etsy_listing_id} on Etsy")
            
            return updated_listings
        except Exception as e:
            logger.error(f"Error updating listings on Etsy: {str(e)}")
            return []
    
    def run_full_workflow(self, fetch_limit=10, optimize_limit=10, update_limit=10):
        """Run the full workflow: fetch, optimize, and update listings.
        
        Args:
            fetch_limit (int): Maximum number of listings to fetch
            optimize_limit (int): Maximum number of listings to optimize
            update_limit (int): Maximum number of listings to update
            
        Returns:
            dict: Workflow results
        """
        logger.info("Running full workflow")
        
        results = {
            "fetched": [],
            "optimized": [],
            "updated": []
        }
        
        try:
            # Step 1: Fetch listings
            logger.info("Step 1: Fetching listings")
            fetched = self.fetch_listings(limit=fetch_limit)
            results["fetched"] = [listing.get("etsy_listing_id") for listing in fetched]
            
            # Step 2: Optimize listings
            logger.info("Step 2: Optimizing listings")
            optimized = self.optimize_listings(limit=optimize_limit)
            results["optimized"] = [listing.get("etsy_listing_id") for listing in optimized]
            
            # Step 3: Update listings
            logger.info("Step 3: Updating listings")
            updated = self.update_listings(limit=update_limit)
            results["updated"] = [listing.get("etsy_listing_id") for listing in updated]
            
            logger.info("Workflow complete")
            
            return results
        except Exception as e:
            logger.error(f"Error running workflow: {str(e)}")
            return results

def main():
    """Main entry point."""
    # Initialize integration
    integration = AIEtsyIntegration()
    
    # Run workflow
    results = integration.run_full_workflow(
        fetch_limit=5,
        optimize_limit=5,
        update_limit=5
    )
    
    # Print results
    print("Workflow Results:")
    print(f"Fetched: {len(results['fetched'])} listings")
    print(f"Optimized: {len(results['optimized'])} listings")
    print(f"Updated: {len(results['updated'])} listings")

if __name__ == '__main__':
    main()