#!/usr/bin/env python3
"""
Benchmark script for comparing single-model vs dual-model Ollama configuration.

This script compares the performance of using a single model for both text generation
and embeddings versus using separate specialized models for each task.
"""

import os
import sys
import time
import json
import logging
import statistics
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../..')))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def benchmark_single_model(model_name="qwen3:8b", num_runs=3):
    """Benchmark using a single model for both text generation and embeddings."""
    from pod_automation.agents.seo.ai.ollama_client import OllamaClient
    
    print(f"\nBenchmarking single model: {model_name}")
    
    # Initialize client with single model
    client = OllamaClient(
        generation_model=model_name,
        embedding_model=model_name
    )
    
    # Benchmark text generation
    generation_times = []
    prompt = "What are the best practices for Etsy SEO?"
    
    for i in range(num_runs):
        print(f"  Generation run {i+1}/{num_runs}...")
        start_time = time.time()
        response = client.generate(prompt)
        end_time = time.time()
        generation_time = end_time - start_time
        generation_times.append(generation_time)
        print(f"    Generated text in {generation_time:.2f} seconds")
    
    # Benchmark embedding generation
    embedding_times = []
    text = "cat lover t-shirt"
    
    for i in range(num_runs):
        print(f"  Embedding run {i+1}/{num_runs}...")
        start_time = time.time()
        embedding = client.embed(text)
        end_time = time.time()
        embedding_time = end_time - start_time
        embedding_times.append(embedding_time)
        print(f"    Generated embedding in {embedding_time:.2f} seconds")
    
    # Calculate statistics
    avg_generation_time = statistics.mean(generation_times)
    avg_embedding_time = statistics.mean(embedding_times)
    total_time = sum(generation_times) + sum(embedding_times)
    
    results = {
        "model": model_name,
        "generation_times": generation_times,
        "embedding_times": embedding_times,
        "avg_generation_time": avg_generation_time,
        "avg_embedding_time": avg_embedding_time,
        "total_time": total_time
    }
    
    return results

def benchmark_dual_model(generation_model="mistral:latest", embedding_model="nomic-embed-text:latest", num_runs=3):
    """Benchmark using separate models for text generation and embeddings."""
    from pod_automation.agents.seo.ai.ollama_client import OllamaClient
    
    print(f"\nBenchmarking dual model: {generation_model} (generation) + {embedding_model} (embedding)")
    
    # Initialize client with separate models
    client = OllamaClient(
        generation_model=generation_model,
        embedding_model=embedding_model
    )
    
    # Benchmark text generation
    generation_times = []
    prompt = "What are the best practices for Etsy SEO?"
    
    for i in range(num_runs):
        print(f"  Generation run {i+1}/{num_runs}...")
        start_time = time.time()
        response = client.generate(prompt)
        end_time = time.time()
        generation_time = end_time - start_time
        generation_times.append(generation_time)
        print(f"    Generated text in {generation_time:.2f} seconds")
    
    # Benchmark embedding generation
    embedding_times = []
    text = "cat lover t-shirt"
    
    for i in range(num_runs):
        print(f"  Embedding run {i+1}/{num_runs}...")
        start_time = time.time()
        embedding = client.embed(text)
        end_time = time.time()
        embedding_time = end_time - start_time
        embedding_times.append(embedding_time)
        print(f"    Generated embedding in {embedding_time:.2f} seconds")
        print(f"    Embedding dimension: {len(embedding)}")
    
    # Calculate statistics
    avg_generation_time = statistics.mean(generation_times)
    avg_embedding_time = statistics.mean(embedding_times)
    total_time = sum(generation_times) + sum(embedding_times)
    
    results = {
        "generation_model": generation_model,
        "embedding_model": embedding_model,
        "generation_times": generation_times,
        "embedding_times": embedding_times,
        "avg_generation_time": avg_generation_time,
        "avg_embedding_time": avg_embedding_time,
        "total_time": total_time
    }
    
    return results

def main():
    """Main entry point."""
    print("=" * 50)
    print("OLLAMA MODEL BENCHMARK")
    print("=" * 50)
    
    # Number of runs for each benchmark
    num_runs = 3
    
    # Benchmark single model approach
    single_model_results = benchmark_single_model("qwen3:8b", num_runs)
    
    # Benchmark dual model approach
    dual_model_results = benchmark_dual_model("mistral:latest", "nomic-embed-text:latest", num_runs)
    
    # Print results
    print("\n" + "=" * 50)
    print("BENCHMARK RESULTS")
    print("=" * 50)
    
    print("\nSingle Model Approach:")
    print(f"  Model: {single_model_results['model']}")
    print(f"  Average Generation Time: {single_model_results['avg_generation_time']:.2f} seconds")
    print(f"  Average Embedding Time: {single_model_results['avg_embedding_time']:.2f} seconds")
    print(f"  Total Time: {single_model_results['total_time']:.2f} seconds")
    
    print("\nDual Model Approach:")
    print(f"  Generation Model: {dual_model_results['generation_model']}")
    print(f"  Embedding Model: {dual_model_results['embedding_model']}")
    print(f"  Average Generation Time: {dual_model_results['avg_generation_time']:.2f} seconds")
    print(f"  Average Embedding Time: {dual_model_results['avg_embedding_time']:.2f} seconds")
    print(f"  Total Time: {dual_model_results['total_time']:.2f} seconds")
    
    # Calculate improvement
    embedding_improvement = (single_model_results['avg_embedding_time'] - dual_model_results['avg_embedding_time']) / single_model_results['avg_embedding_time'] * 100
    total_improvement = (single_model_results['total_time'] - dual_model_results['total_time']) / single_model_results['total_time'] * 100
    
    print("\nPerformance Improvement:")
    print(f"  Embedding Time Improvement: {embedding_improvement:.2f}%")
    print(f"  Total Time Improvement: {total_improvement:.2f}%")
    
    # Save results to file
    results = {
        "single_model": single_model_results,
        "dual_model": dual_model_results,
        "embedding_improvement": embedding_improvement,
        "total_improvement": total_improvement,
        "timestamp": datetime.now().isoformat()
    }
    
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to benchmark_results.json")

if __name__ == '__main__':
    main()
