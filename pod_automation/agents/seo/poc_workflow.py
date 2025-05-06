"""
Proof of Concept Workflow for the SEO Module.

This script demonstrates the complete workflow from importing listings to updating them on Etsy.
"""

import argparse
import logging
import sys
import time
from typing import Dict, List, Optional, Any

from pod_automation.agents.seo.db import get_listings, get_listing, update_listing_status
from pod_automation.agents.seo.etsy_integration import (
    fetch_active_listings, 
    import_listings_to_db, 
    optimize_listing_from_db, 
    update_etsy_listing
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def run_poc_workflow(listing_count: int = 5, optimize_count: int = 1, update_etsy: bool = False):
    """Run the proof of concept workflow.
    
    Args:
        listing_count (int): Number of listings to import
        optimize_count (int): Number of listings to optimize
        update_etsy (bool): Whether to update listings on Etsy
    """
    logger.info("Starting SEO Module Proof of Concept Workflow")
    
    # Step 1: Import listings from Etsy to database
    logger.info(f"Step 1: Importing {listing_count} listings from Etsy to database")
    imported = import_listings_to_db(listing_count, 0)
    
    if not imported:
        logger.error("No listings imported. Aborting workflow.")
        return
    
    logger.info(f"Successfully imported {len(imported)} listings to database")
    
    # Step 2: List imported listings
    logger.info("Step 2: Listing imported listings")
    listings = get_listings(limit=listing_count)
    
    if not listings:
        logger.error("No listings found in database. Aborting workflow.")
        return
    
    logger.info(f"Found {len(listings)} listings in database")
    
    # Print summary
    for i, listing in enumerate(listings):
        title = listing.get('title_original', 'No title')
        etsy_id = listing.get('etsy_listing_id', 'Unknown')
        status = listing.get('status', 'Unknown')
        print(f"{i+1}. {title} (ID: {etsy_id}, Status: {status})")
    
    # Step 3: Optimize listings
    logger.info(f"Step 3: Optimizing {optimize_count} listings")
    optimized_listings = []
    
    for i, listing in enumerate(listings[:optimize_count]):
        etsy_id = listing.get('etsy_listing_id')
        logger.info(f"Optimizing listing {etsy_id}")
        
        optimized = optimize_listing_from_db(listing, use_advanced_tag_optimizer=True)
        
        if optimized:
            logger.info(f"Successfully optimized listing {etsy_id}")
            optimized_listings.append(optimized)
            
            # Print comparison
            print("\nOriginal Title:")
            print(listing.get('title_original', 'None'))
            print("\nOptimized Title:")
            print(optimized.get('title_optimized', 'None'))
            
            print("\nOriginal Tags:")
            print(", ".join(listing.get('tags_original', [])))
            print("\nOptimized Tags:")
            print(", ".join(optimized.get('tags_optimized', [])))
            
            print(f"\nOptimization Score: {optimized.get('optimization_score', 0)}")
        else:
            logger.error(f"Failed to optimize listing {etsy_id}")
    
    if not optimized_listings:
        logger.error("No listings optimized. Aborting workflow.")
        return
    
    # Step 4: Approve optimizations
    logger.info("Step 4: Approving optimizations")
    approved_listings = []
    
    for listing in optimized_listings:
        etsy_id = listing.get('etsy_listing_id')
        logger.info(f"Approving optimization for listing {etsy_id}")
        
        success = update_listing_status(etsy_id, 'approved', 'poc_workflow')
        
        if success:
            logger.info(f"Successfully approved listing {etsy_id}")
            approved_listings.append(listing)
        else:
            logger.error(f"Failed to approve listing {etsy_id}")
    
    if not approved_listings:
        logger.error("No listings approved. Aborting workflow.")
        return
    
    # Step 5: Update listings on Etsy (optional)
    if update_etsy:
        logger.info("Step 5: Updating listings on Etsy")
        
        for listing in approved_listings:
            etsy_id = listing.get('etsy_listing_id')
            logger.info(f"Updating listing {etsy_id} on Etsy")
            
            # Get fresh listing data from database
            db_listing = get_listing(etsy_id)
            
            if not db_listing:
                logger.error(f"Listing {etsy_id} not found in database")
                continue
            
            success = update_etsy_listing(db_listing)
            
            if success:
                logger.info(f"Successfully updated listing {etsy_id} on Etsy")
            else:
                logger.error(f"Failed to update listing {etsy_id} on Etsy")
    else:
        logger.info("Step 5: Skipping Etsy updates (use --update-etsy flag to enable)")
    
    logger.info("Proof of Concept Workflow completed successfully!")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='SEO Module Proof of Concept Workflow')
    parser.add_argument('--listing-count', type=int, default=5, help='Number of listings to import')
    parser.add_argument('--optimize-count', type=int, default=1, help='Number of listings to optimize')
    parser.add_argument('--update-etsy', action='store_true', help='Update listings on Etsy')
    
    args = parser.parse_args()
    
    run_poc_workflow(args.listing_count, args.optimize_count, args.update_etsy)

if __name__ == '__main__':
    main()
