"""
Simple demonstration of the AI-enhanced SEO optimization system.

This script demonstrates the basic functionality of the AI-enhanced SEO optimization system
using a sample listing without requiring database access.
"""

import os
import sys
import json
import logging
from datetime import datetime

from pod_automation.agents.seo.ai.ai_seo_optimizer import AISEOOptimizer

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_demo():
    """Run a simple demonstration of the AI-enhanced SEO optimization."""
    print("=" * 80)
    print("AI-ENHANCED SEO OPTIMIZATION DEMO")
    print("=" * 80)
    
    # Create a sample listing
    sample_listing = {
        'title_original': 'Cat Lover T-Shirt - Funny Cat Shirt - Cat Mom Gift',
        'tags_original': ['cat', 'cat lover', 't-shirt', 'funny', 'cat mom', 'gift'],
        'description_original': 'This is a great t-shirt for cat lovers! Perfect for cat moms and cat dads. Show your love for cats with this comfortable and stylish shirt.',
        'base_keyword': 'cat lover',
        'product_type': 't-shirt'
    }
    
    print("\nSample Listing:")
    print(f"Title: {sample_listing['title_original']}")
    print(f"Tags: {', '.join(sample_listing['tags_original'])}")
    print(f"Description: {sample_listing['description_original']}")
    
    # Initialize optimizer with qwen3:8b model
    print("\nInitializing AI SEO Optimizer with qwen3:8b model...")
    optimizer = AISEOOptimizer(ollama_model="qwen3:8b")
    
    # Step 1: Optimize title
    print("\n" + "=" * 40)
    print("STEP 1: OPTIMIZING TITLE")
    print("=" * 40)
    print("Generating AI-optimized title...")
    optimized_title = optimizer.optimize_title_ai(sample_listing)
    print("\nOriginal Title:")
    print(sample_listing['title_original'])
    print("\nOptimized Title:")
    print(optimized_title)
    print(f"\nCharacter count: {len(optimized_title)} (Etsy recommends 120-140 characters)")
    
    # Step 2: Optimize tags
    print("\n" + "=" * 40)
    print("STEP 2: OPTIMIZING TAGS")
    print("=" * 40)
    print("Generating AI-optimized tags...")
    optimized_tags = optimizer.optimize_tags_ai(sample_listing)
    print("\nOriginal Tags:")
    print(', '.join(sample_listing['tags_original']))
    print("\nOptimized Tags:")
    print(', '.join(optimized_tags))
    print(f"\nTag count: {len(optimized_tags)} (Etsy allows up to 13 tags)")
    
    # Step 3: Optimize description
    print("\n" + "=" * 40)
    print("STEP 3: OPTIMIZING DESCRIPTION")
    print("=" * 40)
    print("Generating AI-optimized description...")
    optimized_description = optimizer.optimize_description_ai(sample_listing)
    print("\nOriginal Description:")
    print(sample_listing['description_original'])
    print("\nOptimized Description (first 300 characters):")
    print(optimized_description[:300] + "...")
    
    # Step 4: Analyze listing
    print("\n" + "=" * 40)
    print("STEP 4: ANALYZING LISTING")
    print("=" * 40)
    print("Analyzing original listing...")
    analysis = optimizer.analyze_listing(sample_listing)
    print(f"\nSEO Score: {analysis.get('score', 0)}/100")
    
    if 'notes' in analysis:
        if 'strengths' in analysis['notes']:
            print("\nStrengths:")
            for strength in analysis['notes']['strengths']:
                print(f"✓ {strength}")
        
        if 'weaknesses' in analysis['notes']:
            print("\nWeaknesses:")
            for weakness in analysis['notes']['weaknesses']:
                print(f"✗ {weakness}")
        
        if 'recommendations' in analysis:
            print("\nRecommendations:")
            for recommendation in analysis['recommendations']:
                print(f"→ {recommendation}")
    
    # Step 5: Explain optimization
    print("\n" + "=" * 40)
    print("STEP 5: EXPLAINING OPTIMIZATION")
    print("=" * 40)
    
    # Create optimized listing
    optimized_listing = {
        'title_optimized': optimized_title,
        'tags_optimized': optimized_tags,
        'description_optimized': optimized_description
    }
    
    print("Generating explanation of optimization changes...")
    explanation = optimizer.explain_optimization(sample_listing, optimized_listing)
    print("\nExplanation:")
    print(explanation)
    
    print("\n" + "=" * 80)
    print("DEMO COMPLETE")
    print("=" * 80)
    print("\nThe AI-enhanced SEO optimization system successfully:")
    print("✓ Generated an optimized title")
    print("✓ Generated optimized tags")
    print("✓ Generated an optimized description")
    print("✓ Analyzed the listing's SEO quality")
    print("✓ Explained the optimization changes")
    
    return {
        'title': optimized_title,
        'tags': optimized_tags,
        'description': optimized_description,
        'analysis': analysis
    }

if __name__ == '__main__':
    run_demo()