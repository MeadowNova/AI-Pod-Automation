#!/usr/bin/env python3
"""
Test script for dual-model Ollama configuration.

This script tests the dual-model approach with separate models for text generation and embeddings.
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_dual_model():
    """Test the dual-model approach."""
    from pod_automation.agents.seo.ai.ollama_client import OllamaClient
    
    print("\n" + "=" * 50)
    print("DUAL-MODEL OLLAMA TEST")
    print("=" * 50)
    
    # Initialize client with separate models
    print("\nInitializing Ollama client with separate models...")
    client = OllamaClient(
        generation_model="mistral:latest",
        embedding_model="nomic-embed-text"
    )
    
    # Get available models
    print("\nGetting available models...")
    models = client.get_available_models()
    print(f"Available models: {models}")
    
    # Print which models are being used
    print(f"\nUsing generation model: {client.generation_model}")
    print(f"Using embedding model: {client.embedding_model}")
    
    # Test text generation
    print("\nTesting text generation...")
    prompt = "What are the best practices for Etsy SEO?"
    
    start_time = time.time()
    response = client.generate(prompt)
    end_time = time.time()
    
    print(f"Generated text in {end_time - start_time:.2f} seconds")
    print(f"Response (first 200 chars): {response[:200]}...")
    
    # Test embedding generation
    print("\nTesting embedding generation...")
    text = "cat lover t-shirt"
    
    start_time = time.time()
    embedding = client.embed(text)
    end_time = time.time()
    
    print(f"Generated embedding in {end_time - start_time:.2f} seconds")
    print(f"Embedding dimension: {len(embedding)}")
    if embedding:
        print(f"First 5 values: {embedding[:5]}")
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Generation Model: {client.generation_model}")
    print(f"Embedding Model: {client.embedding_model}")
    print(f"Text Generation: {'✅ Success' if response else '❌ Failed'}")
    print(f"Embedding Generation: {'✅ Success' if embedding else '❌ Failed'}")
    
    if response and embedding:
        print("\n✅ Dual-model approach is working correctly!")
    else:
        print("\n❌ Dual-model approach has issues. Check the logs for details.")

def test_rag_performance():
    """Test RAG performance with the dual-model approach."""
    from pod_automation.agents.seo.ai.ollama_client import OllamaClient
    from pod_automation.agents.seo.ai.rag_system import RAGSystem
    from pod_automation.agents.seo.db.mock_db import MockSEODatabase
    
    print("\n" + "=" * 50)
    print("RAG PERFORMANCE TEST")
    print("=" * 50)
    
    # Create a mock database
    db = MockSEODatabase()
    
    # Initialize client with separate models
    client = OllamaClient(
        generation_model="mistral:latest",
        embedding_model="nomic-embed-text"
    )
    
    print(f"\nUsing generation model: {client.generation_model}")
    print(f"Using embedding model: {client.embedding_model}")
    
    # Initialize RAG system
    rag = RAGSystem(db, client)
    
    # Test indexing keywords
    print("\nIndexing keywords...")
    start_time = time.time()
    rag.index_keywords()
    end_time = time.time()
    
    print(f"Indexed {len(rag.keyword_embeddings)} keywords in {end_time - start_time:.2f} seconds")
    
    # Test retrieving relevant keywords
    print("\nRetrieving relevant keywords...")
    query = "cat lover t-shirt"
    
    start_time = time.time()
    keywords = rag.retrieve_relevant_keywords(query, top_k=3)
    end_time = time.time()
    
    print(f"Retrieved {len(keywords)} relevant keywords in {end_time - start_time:.2f} seconds")
    for i, kw in enumerate(keywords, 1):
        print(f"  {i}. '{kw['keyword']}' (similarity: {kw['similarity']:.4f})")
    
    # Print summary
    print("\n" + "=" * 50)
    print("RAG PERFORMANCE SUMMARY")
    print("=" * 50)
    print(f"Generation Model: {client.generation_model}")
    print(f"Embedding Model: {client.embedding_model}")
    print(f"Keywords Indexed: {len(rag.keyword_embeddings)}")
    print(f"Keywords Retrieved: {len(keywords)}")
    
    if rag.keyword_embeddings and keywords:
        print("\n✅ RAG system with dual-model approach is working correctly!")
    else:
        print("\n❌ RAG system has issues. Check the logs for details.")

def main():
    """Main entry point."""
    print("Testing dual-model approach for Ollama")
    
    # Test dual-model approach
    test_dual_model()
    
    # Test RAG performance
    test_rag_performance()

if __name__ == '__main__':
    main()
