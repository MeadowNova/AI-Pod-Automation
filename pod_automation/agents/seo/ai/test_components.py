"""
Test script for AI-enhanced SEO optimization components.

This script tests the individual components of the AI-enhanced SEO optimization system.
"""

import os
import sys
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ollama_client():
    """Test the Ollama client."""
    from pod_automation.agents.seo.ai.ollama_client import OllamaClient

    print("\nTesting Ollama Client...")

    # Initialize client
    client = OllamaClient(model="qwen3:8b")

    # Test getting available models
    print("Getting available models...")
    models = client.get_available_models()
    print(f"Available models: {models}")

    # Test generating text
    print("\nGenerating text...")
    prompt = "What are the best practices for Etsy SEO?"
    response = client.generate(prompt)
    print(f"Response: {response[:200]}...")

    # Test generating embeddings
    print("\nGenerating embeddings...")
    text = "cat lover t-shirt"
    embedding = client.embed(text)
    print(f"Embedding length: {len(embedding)}")
    if embedding:
        print(f"First 5 values: {embedding[:5]}")

    print("\nOllama Client test complete")
    return bool(models) and bool(response) and bool(embedding)

def test_rag_system():
    """Test the RAG system."""
    from pod_automation.agents.seo.ai.ollama_client import OllamaClient
    from pod_automation.agents.seo.ai.rag_system import RAGSystem
    from pod_automation.agents.seo.db import seo_db

    print("\nTesting RAG System...")

    # Check if Supabase is connected
    if not seo_db.is_connected():
        print("Not connected to Supabase database, using mock data")

        # Create a mock database client
        class MockDB:
            def get_keywords(self, limit=1000):
                return [
                    {"keyword": "cat lover", "search_volume": 4800, "competition": 6.8},
                    {"keyword": "cat t-shirt", "search_volume": 5200, "competition": 7.2},
                    {"keyword": "funny cat", "search_volume": 4200, "competition": 6.5}
                ]

            def get_listings(self, limit=100):
                return [
                    {
                        "id": 1,
                        "title_original": "Cat Lover T-Shirt - Funny Cat Shirt - Cat Mom Gift",
                        "tags_original": ["cat", "cat lover", "t-shirt", "funny", "cat mom", "gift"]
                    },
                    {
                        "id": 2,
                        "title_original": "Funny Cat Tee - Cat Dad Shirt - Cat Lover Gift",
                        "tags_original": ["cat", "funny cat", "tee", "cat dad", "gift"]
                    }
                ]

        db_client = MockDB()
    else:
        db_client = seo_db

    # Initialize Ollama client
    ollama_client = OllamaClient(model="qwen3:8b")

    # Initialize RAG system
    rag = RAGSystem(db_client, ollama_client)

    # Test indexing keywords
    print("Indexing keywords...")
    rag.index_keywords()
    print(f"Indexed {len(rag.keyword_embeddings)} keywords")

    # Test indexing listings
    print("\nIndexing listings...")
    rag.index_listings(limit=5)
    print(f"Indexed {len(rag.listing_embeddings)} listings")

    # Test retrieving relevant keywords
    print("\nRetrieving relevant keywords...")
    query = "cat lover t-shirt"
    keywords = rag.retrieve_relevant_keywords(query, top_k=3)
    print(f"Retrieved {len(keywords)} relevant keywords")
    for i, kw in enumerate(keywords, 1):
        print(f"  {i}. '{kw['keyword']}' (similarity: {kw['similarity']:.4f})")

    # Test retrieving similar listings
    print("\nRetrieving similar listings...")
    listings = rag.retrieve_similar_listings(query, top_k=2)
    print(f"Retrieved {len(listings)} similar listings")
    for i, listing in enumerate(listings, 1):
        print(f"  {i}. '{listing['data'].get('title_original', '')}' (similarity: {listing['similarity']:.4f})")

    # Test formatting context
    print("\nFormatting context...")
    context = rag.format_context(keywords, listings)
    print(f"Context length: {len(context)}")
    print(f"First 200 characters: {context[:200]}...")

    print("\nRAG System test complete")
    return bool(rag.keyword_embeddings) and bool(rag.listing_embeddings) and bool(keywords) and bool(listings) and bool(context)

def test_ai_seo_optimizer():
    """Test the AI SEO optimizer."""
    from pod_automation.agents.seo.ai.ai_seo_optimizer import AISEOOptimizer

    print("\nTesting AI SEO Optimizer...")

    # Initialize optimizer
    optimizer = AISEOOptimizer(ollama_model="qwen3:8b")

    # Create a sample listing
    sample_listing = {
        'title_original': 'Cat Lover T-Shirt - Funny Cat Shirt - Cat Mom Gift',
        'tags_original': ['cat', 'cat lover', 't-shirt', 'funny', 'cat mom', 'gift'],
        'description_original': 'This is a great t-shirt for cat lovers! Perfect for cat moms and cat dads.',
        'base_keyword': 'cat lover',
        'product_type': 't-shirt'
    }

    # Test extracting keyword and product
    print("Extracting keyword and product...")
    extracted = optimizer.extract_keyword_and_product(sample_listing['title_original'])
    print(f"Extracted: {extracted}")

    # Test optimizing title
    print("\nOptimizing title...")
    title = optimizer.optimize_title_ai(sample_listing)
    print(f"Optimized title: {title}")

    # Test optimizing tags
    print("\nOptimizing tags...")
    tags = optimizer.optimize_tags_ai(sample_listing)
    print(f"Optimized tags: {tags}")

    # Test optimizing description
    print("\nOptimizing description...")
    description = optimizer.optimize_description_ai(sample_listing)
    print(f"Optimized description (first 100 chars): {description[:100]}...")

    # Test analyzing listing
    print("\nAnalyzing listing...")
    analysis = optimizer.analyze_listing(sample_listing)
    print(f"Analysis score: {analysis.get('score', 0)}")
    if 'notes' in analysis:
        if 'strengths' in analysis['notes']:
            print(f"Strengths: {', '.join(analysis['notes']['strengths'][:2])}")
        if 'weaknesses' in analysis['notes']:
            print(f"Weaknesses: {', '.join(analysis['notes']['weaknesses'][:2])}")

    # Test explaining optimization
    print("\nExplaining optimization...")
    optimized_listing = {
        'title_optimized': title,
        'tags_optimized': tags,
        'description_optimized': description
    }
    explanation = optimizer.explain_optimization(sample_listing, optimized_listing)
    print(f"Explanation (first 200 chars): {explanation[:200]}...")

    print("\nAI SEO Optimizer test complete")
    return bool(extracted) and bool(title) and bool(tags) and bool(description) and bool(analysis) and bool(explanation)

def main():
    """Main entry point."""
    print("AI-Enhanced SEO Optimization Component Tests")
    print("===========================================")

    # Test Ollama client
    ollama_success = test_ollama_client()

    # Test RAG system
    rag_success = test_rag_system()

    # Test AI SEO optimizer
    optimizer_success = test_ai_seo_optimizer()

    # Print summary
    print("\nTest Summary:")
    print(f"Ollama Client: {'✓ PASS' if ollama_success else '✗ FAIL'}")
    print(f"RAG System: {'✓ PASS' if rag_success else '✗ FAIL'}")
    print(f"AI SEO Optimizer: {'✓ PASS' if optimizer_success else '✗ FAIL'}")

    if ollama_success and rag_success and optimizer_success:
        print("\nAll tests passed! The AI-enhanced SEO optimization system is working correctly.")
    else:
        print("\nSome tests failed. Please check the logs for details.")

if __name__ == '__main__':
    main()