#!/usr/bin/env python3
"""
Test script for batch processing and embedding cache.

This script tests the batch processing and embedding cache functionality.
"""

import os
import sys
import time
import json
import logging
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_test_listings(num_listings=10):
    """Generate test listings.

    Args:
        num_listings (int): Number of listings to generate

    Returns:
        list: Test listings
    """
    listings = []
    
    # Product types and themes for variety
    product_types = ["t-shirt", "mug", "poster", "hoodie", "tote bag"]
    themes = ["cat lover", "dog mom", "plant lady", "coffee addict", "book worm", 
              "mountain hiking", "beach life", "camping", "yoga", "meditation"]
    
    for i in range(num_listings):
        # Select product type and theme
        product_type = product_types[i % len(product_types)]
        theme = themes[i % len(themes)]
        
        # Create listing
        listing = {
            "id": i + 1,
            "etsy_listing_id": str(10000 + i),
            "title_original": f"{theme.title()} {product_type.title()} - Perfect Gift for {theme.title()} - Unique {product_type.title()}",
            "tags_original": [theme, product_type, "gift", "unique", "handmade"],
            "description_original": f"This {product_type} is perfect for any {theme}! Show your love with this unique design.\n\nFeatures:\n- High quality\n- Comfortable\n- Unique design\n\nMakes a great gift for any occasion!",
            "base_keyword": theme,
            "product_type": product_type
        }
        
        listings.append(listing)
    
    return listings

def test_embedding_cache():
    """Test embedding cache functionality."""
    from pod_automation.agents.seo.ai.ollama_client import OllamaClient
    from pod_automation.agents.seo.ai.embedding_cache import embedding_cache
    
    print("\n" + "=" * 50)
    print("EMBEDDING CACHE TEST")
    print("=" * 50)
    
    # Initialize client
    client = OllamaClient(
        generation_model="mistral:latest",
        embedding_model="nomic-embed-text:latest"
    )
    
    # Clear cache to start fresh
    embedding_cache.clear()
    
    # Test texts
    test_texts = [
        "cat lover t-shirt",
        "dog mom mug",
        "plant lady poster",
        "cat lover t-shirt",  # Duplicate to test cache hit
        "coffee addict hoodie"
    ]
    
    # Generate embeddings for each text
    for i, text in enumerate(test_texts):
        print(f"\nGenerating embedding for: '{text}'")
        
        start_time = time.time()
        embedding = client.embed(text)
        end_time = time.time()
        
        print(f"  Generated embedding in {end_time - start_time:.2f} seconds")
        print(f"  Embedding dimension: {len(embedding)}")
        
        # Get cache stats after each embedding
        stats = client.get_cache_stats()
        print(f"  Cache stats: {stats}")
    
    # Print final cache stats
    print("\nFinal cache stats:")
    stats = client.get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Verify cache is working by checking hit ratio
    if stats["hits"] > 0:
        print("\n✅ Embedding cache is working correctly!")
    else:
        print("\n❌ Embedding cache is not working correctly.")

def test_batch_processing():
    """Test batch processing functionality."""
    from pod_automation.agents.seo.ai.ai_seo_optimizer import AISEOOptimizer
    from pod_automation.agents.seo.db.mock_db import MockSEODatabase
    
    print("\n" + "=" * 50)
    print("BATCH PROCESSING TEST")
    print("=" * 50)
    
    # Create mock database
    mock_db = MockSEODatabase()
    
    # Initialize optimizer
    optimizer = AISEOOptimizer(
        generation_model="mistral:latest",
        embedding_model="nomic-embed-text:latest"
    )
    
    # Generate test listings
    num_listings = 5
    print(f"\nGenerating {num_listings} test listings...")
    listings = generate_test_listings(num_listings)
    
    # Optimize listings in batch
    print(f"\nOptimizing {num_listings} listings in batch...")
    start_time = time.time()
    optimized_listings = optimizer.optimize_listings_batch(listings)
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time_per_listing = total_time / len(optimized_listings) if optimized_listings else 0
    
    print(f"\nBatch processing completed in {total_time:.2f} seconds")
    print(f"Average time per listing: {avg_time_per_listing:.2f} seconds")
    print(f"Successfully optimized {len(optimized_listings)}/{num_listings} listings")
    
    # Print sample of optimized listings
    if optimized_listings:
        print("\nSample optimized listing:")
        sample = optimized_listings[0]
        print(f"  Original title: {sample.get('title_original', '')}")
        print(f"  Optimized title: {sample.get('title_optimized', '')}")
        print(f"  Original tags: {sample.get('tags_original', [])}")
        print(f"  Optimized tags: {sample.get('tags_optimized', [])}")
    
    # Print cache stats
    print("\nEmbedding cache stats after batch processing:")
    stats = optimizer.ollama.get_cache_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    if len(optimized_listings) == num_listings:
        print("\n✅ Batch processing is working correctly!")
    else:
        print("\n❌ Batch processing is not working correctly.")

def main():
    """Main entry point."""
    print("Testing embedding cache and batch processing")
    
    # Test embedding cache
    test_embedding_cache()
    
    # Test batch processing
    test_batch_processing()

if __name__ == '__main__':
    main()
