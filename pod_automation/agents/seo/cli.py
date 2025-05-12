"""
Command-line interface for the SEO module.

This module provides a command-line interface for testing the SEO module functionality.
"""

import argparse
import json
import logging
import sys
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

def fetch_command(args):
    """Fetch listings from Etsy."""
    listings = fetch_active_listings(args.limit, args.offset)
    
    if not listings:
        logger.error("No listings found")
        return
    
    logger.info(f"Fetched {len(listings)} listings from Etsy")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(listings, f, indent=2)
        logger.info(f"Saved listings to {args.output}")
    else:
        # Print summary
        for i, listing in enumerate(listings):
            print(f"{i+1}. {listing.get('title', 'No title')} (ID: {listing.get('listing_id', 'Unknown')})")

def import_command(args):
    """Import listings from Etsy to database."""
    imported = import_listings_to_db(args.limit, args.offset)
    
    if not imported:
        logger.error("No listings imported")
        return
    
    logger.info(f"Imported {len(imported)} listings to database")
    
    # Print summary
    for i, listing in enumerate(imported):
        print(f"{i+1}. {listing.get('title_original', 'No title')} (ID: {listing.get('etsy_listing_id', 'Unknown')})")

def list_command(args):
    """List listings from database."""
    listings = get_listings(args.status, args.limit, args.offset)
    
    if not listings:
        logger.error("No listings found in database")
        return
    
    logger.info(f"Found {len(listings)} listings in database")
    
    # Print summary
    for i, listing in enumerate(listings):
        title = listing.get('title_original', 'No title')
        etsy_id = listing.get('etsy_listing_id', 'Unknown')
        status = listing.get('status', 'Unknown')
        print(f"{i+1}. {title} (ID: {etsy_id}, Status: {status})")

def optimize_command(args):
    """Optimize a listing."""
    listing = get_listing(args.listing_id)
    
    if not listing:
        logger.error(f"Listing {args.listing_id} not found in database")
        return
    
    optimized = optimize_listing_from_db(listing, args.advanced)
    
    if not optimized:
        logger.error(f"Failed to optimize listing {args.listing_id}")
        return
    
    logger.info(f"Successfully optimized listing {args.listing_id}")
    
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

def approve_command(args):
    """Approve a listing optimization."""
    listing = get_listing(args.listing_id)
    
    if not listing:
        logger.error(f"Listing {args.listing_id} not found in database")
        return
    
    if listing.get('status') != 'optimized':
        logger.error(f"Listing {args.listing_id} is not optimized (status: {listing.get('status')})")
        return
    
    success = update_listing_status(args.listing_id, 'approved', 'cli_user')
    
    if not success:
        logger.error(f"Failed to approve listing {args.listing_id}")
        return
    
    logger.info(f"Successfully approved listing {args.listing_id}")

def update_command(args):
    """Update a listing on Etsy."""
    listing = get_listing(args.listing_id)
    
    if not listing:
        logger.error(f"Listing {args.listing_id} not found in database")
        return
    
    if listing.get('status') != 'approved':
        logger.error(f"Listing {args.listing_id} is not approved (status: {listing.get('status')})")
        return
    
    success = update_etsy_listing(listing)
    
    if not success:
        logger.error(f"Failed to update listing {args.listing_id} on Etsy")
        return
    
    logger.info(f"Successfully updated listing {args.listing_id} on Etsy")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='SEO Module CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch listings from Etsy')
    fetch_parser.add_argument('--limit', type=int, default=10, help='Maximum number of listings to fetch')
    fetch_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    fetch_parser.add_argument('--output', type=str, help='Output file for JSON data')
    fetch_parser.set_defaults(func=fetch_command)
    
    # Import command
    import_parser = subparsers.add_parser('import', help='Import listings from Etsy to database')
    import_parser.add_argument('--limit', type=int, default=10, help='Maximum number of listings to import')
    import_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    import_parser.set_defaults(func=import_command)
    
    # List command
    list_parser = subparsers.add_parser('list', help='List listings from database')
    list_parser.add_argument('--status', type=str, choices=['pending', 'optimized', 'approved', 'rejected', 'updated'], help='Filter by status')
    list_parser.add_argument('--limit', type=int, default=10, help='Maximum number of listings to list')
    list_parser.add_argument('--offset', type=int, default=0, help='Offset for pagination')
    list_parser.set_defaults(func=list_command)
    
    # Optimize command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize a listing')
    optimize_parser.add_argument('listing_id', type=int, help='Etsy listing ID')
    optimize_parser.add_argument('--advanced', action='store_true', help='Use advanced tag optimizer')
    optimize_parser.set_defaults(func=optimize_command)
    
    # Approve command
    approve_parser = subparsers.add_parser('approve', help='Approve a listing optimization')
    approve_parser.add_argument('listing_id', type=int, help='Etsy listing ID')
    approve_parser.set_defaults(func=approve_command)
    
    # Update command
    update_parser = subparsers.add_parser('update', help='Update a listing on Etsy')
    update_parser.add_argument('listing_id', type=int, help='Etsy listing ID')
    update_parser.set_defaults(func=update_command)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    args.func(args)

if __name__ == '__main__':
    main()