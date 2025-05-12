"""
Example usage of the AI-enhanced SEO optimization system.

This script demonstrates how to use the AI-enhanced SEO optimization system.
"""

import os
import json
import logging
from datetime import datetime

from pod_automation.agents.seo.db import seo_db
from pod_automation.agents.seo.ai.ai_seo_optimizer import AISEOOptimizer
from pod_automation.agents.seo.ai.optimization_tracker import OptimizationTracker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def example_optimize_listing():
    """Example of optimizing a single listing."""
    # Check if Supabase is connected
    if not seo_db.is_connected():
        logger.error("Not connected to Supabase database")
        return

    # Get a listing to optimize (for example purposes, get the first pending listing)
    listings = seo_db.get_listings(status='pending', limit=1)

    if not listings:
        logger.error("No pending listings found")
        return

    listing = listings[0]
    etsy_listing_id = listing.get('etsy_listing_id')

    logger.info(f"Optimizing listing {etsy_listing_id}")

    # Initialize optimizer
    optimizer = AISEOOptimizer(ollama_model="llama3")

    # Optimize listing
    optimized = optimizer.optimize_listing_ai(etsy_listing_id, listing)

    if not optimized:
        logger.error(f"Failed to optimize listing {etsy_listing_id}")
        return

    logger.info(f"Successfully optimized listing {etsy_listing_id}")
    logger.info(f"Original title: {listing.get('title_original', '')}")
    logger.info(f"Optimized title: {optimized.get('title_optimized', '')}")

    # Generate explanation
    explanation = optimizer.explain_optimization(listing, optimized)
    logger.info(f"Optimization explanation: {explanation}")

def example_analyze_performance():
    """Example of analyzing optimization performance."""
    # Check if Supabase is connected
    if not seo_db.is_connected():
        logger.error("Not connected to Supabase database")
        return

    # Initialize tracker
    tracker = OptimizationTracker(seo_db)

    # Analyze performance trends
    trends = tracker.analyze_performance_trends(days=30)

    logger.info(f"Performance trends: {json.dumps(trends, indent=2)}")

def example_manual_optimization():
    """Example of manually optimizing a listing without saving to database."""
    # Create a sample listing
    sample_listing = {
        'title_original': 'Cat Lover T-Shirt - Funny Cat Shirt - Cat Mom Gift',
        'tags_original': ['cat', 'cat lover', 't-shirt', 'funny', 'cat mom', 'gift'],
        'description_original': 'This is a great t-shirt for cat lovers! Perfect for cat moms and cat dads.',
        'base_keyword': 'cat lover',
        'product_type': 't-shirt'
    }

    # Initialize optimizer with the model you have available
    optimizer = AISEOOptimizer(ollama_model="qwen3:8b")

    print("\n1. Optimizing title...")
    # Optimize title
    optimized_title = optimizer.optimize_title_ai(sample_listing)
    print(f"Original title: {sample_listing['title_original']}")
    print(f"Optimized title: {optimized_title}")

    print("\n2. Optimizing tags...")
    # Optimize tags
    optimized_tags = optimizer.optimize_tags_ai(sample_listing)
    print(f"Original tags: {', '.join(sample_listing['tags_original'])}")
    print(f"Optimized tags: {', '.join(optimized_tags)}")

    print("\n3. Optimizing description...")
    # Optimize description
    optimized_description = optimizer.optimize_description_ai(sample_listing)
    print(f"Original description: {sample_listing['description_original']}")
    print(f"Optimized description (first 200 chars): {optimized_description[:200]}...")

    print("\n4. Analyzing listing...")
    # Analyze listing
    analysis = optimizer.analyze_listing(sample_listing)
    print(f"Analysis score: {analysis.get('score', 0)}")
    if 'notes' in analysis:
        if 'strengths' in analysis['notes']:
            print("Strengths:")
            for strength in analysis['notes']['strengths'][:3]:
                print(f"- {strength}")
        if 'weaknesses' in analysis['notes']:
            print("Weaknesses:")
            for weakness in analysis['notes']['weaknesses'][:3]:
                print(f"- {weakness}")

    print("\n5. Explaining optimization...")
    # Create optimized listing
    optimized_listing = {
        'title_optimized': optimized_title,
        'tags_optimized': optimized_tags,
        'description_optimized': optimized_description
    }
    explanation = optimizer.explain_optimization(sample_listing, optimized_listing)
    print(f"Explanation (first 300 chars):\n{explanation[:300]}...")

    # Return the optimized listing
    return {
        'title': optimized_title,
        'tags': optimized_tags,
        'description': optimized_description,
        'analysis': analysis
    }

def main():
    """Main entry point."""
    print("AI-Enhanced SEO Optimization Examples")
    print("====================================")

    # Check if Ollama is running
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✓ Ollama is running")
        else:
            print("✗ Ollama is not running properly")
    except:
        print("✗ Ollama is not running")

    # Check if Supabase is connected
    if seo_db.is_connected():
        print("✓ Connected to Supabase database")
    else:
        print("✗ Not connected to Supabase database")

    print("\nExample Options:")
    print("1. Optimize a listing from the database")
    print("2. Analyze optimization performance")
    print("3. Manual optimization example (no database)")
    print("q. Quit")

    choice = input("\nEnter your choice: ")

    if choice == '1':
        example_optimize_listing()
    elif choice == '2':
        example_analyze_performance()
    elif choice == '3':
        example_manual_optimization()
    elif choice.lower() == 'q':
        print("Exiting...")
    else:
        print("Invalid choice")

if __name__ == '__main__':
    main()