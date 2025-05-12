#!/usr/bin/env python3
"""
Test script for batch optimization API endpoint.

This script tests the batch optimization API endpoint by sending a request with multiple listings.
"""

import os
import sys
import json
import time
import logging
import requests
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API URL
API_URL = "http://localhost:8001/api/v1"

def generate_test_listings(num_listings=3):
    """Generate test listings.

    Args:
        num_listings (int): Number of listings to generate

    Returns:
        list: Test listings
    """
    listings = []
    
    # Product types and themes for variety
    product_types = ["t-shirt", "mug", "poster", "hoodie", "tote bag"]
    themes = ["cat lover", "dog mom", "plant lady", "coffee addict", "book worm"]
    
    for i in range(num_listings):
        # Select product type and theme
        product_type = product_types[i % len(product_types)]
        theme = themes[i % len(themes)]
        
        # Create listing
        listing = {
            "id": str(10000 + i),
            "etsy_listing_id": str(10000 + i),
            "title": f"{theme.title()} {product_type.title()} - Perfect Gift for {theme.title()} - Unique {product_type.title()}",
            "tags": [theme, product_type, "gift", "unique", "handmade"],
            "description": f"This {product_type} is perfect for any {theme}! Show your love with this unique design.\n\nFeatures:\n- High quality\n- Comfortable\n- Unique design\n\nMakes a great gift for any occasion!"
        }
        
        listings.append(listing)
    
    return listings

def test_batch_optimization():
    """Test batch optimization API endpoint."""
    print("\n" + "=" * 50)
    print("BATCH OPTIMIZATION API TEST")
    print("=" * 50)
    
    # Generate test listings
    num_listings = 3
    print(f"\nGenerating {num_listings} test listings...")
    listings = generate_test_listings(num_listings)
    
    # Prepare request
    request_data = {
        "listings": listings,
        "max_listings": num_listings
    }
    
    # Send request
    print(f"\nSending batch optimization request to {API_URL}/seo/optimize-listings-batch...")
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{API_URL}/seo/optimize-listings-batch",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Batch optimization successful in {total_time:.2f} seconds")
            print(f"Processed {result['processed_count']}/{result['total_count']} listings")
            
            # Print cache stats if available
            if result.get("cache_stats"):
                print("\nCache stats:")
                for key, value in result["cache_stats"].items():
                    print(f"  {key}: {value}")
            
            # Print sample of optimized listings
            if result.get("results"):
                print("\nSample optimized listing:")
                sample = result["results"][0]
                print(f"  Original listing ID: {sample.get('listing_id')}")
                print(f"  Optimized title: {sample.get('optimized_title')}")
                print(f"  Optimized tags: {sample.get('optimized_tags')}")
                print(f"  SEO score: {sample.get('seo_score')}")
            
            return True
        else:
            print(f"\n❌ Batch optimization failed with status code {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"\n❌ Error sending batch optimization request: {str(e)}")
        return False

def main():
    """Main entry point."""
    print("Testing batch optimization API endpoint")
    
    # Test batch optimization
    success = test_batch_optimization()
    
    if success:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Tests failed.")
        sys.exit(1)

if __name__ == '__main__':
    main()
