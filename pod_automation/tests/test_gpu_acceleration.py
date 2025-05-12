"""
Test script to verify GPU acceleration for the AI SEO optimizer.
Compares performance between CPU and GPU modes.
"""

import time
import logging
import argparse
import torch
import numpy as np
from pod_automation.agents.seo.ai.ai_seo_optimizer import AISEOOptimizer
from pod_automation.utils.gpu_utils import get_device, gpu_memory_stats

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_gpu_availability():
    """Verify if GPU is available for PyTorch."""
    if torch.cuda.is_available():
        device_count = torch.cuda.device_count()
        logger.info(f"GPU is available! Found {device_count} device(s).")
        for i in range(device_count):
            logger.info(f"Device {i}: {torch.cuda.get_device_name(i)}")
        return True
    else:
        logger.info("GPU is not available. Tests will run in CPU mode only.")
        return False

def benchmark_vector_similarity(use_gpu=True, vector_count=1000, vector_dim=768):
    """Benchmark vector similarity calculations."""
    logger.info(f"Benchmarking vector similarity with {'GPU' if use_gpu else 'CPU'}")

    # Create random vectors
    vectors = [np.random.random(vector_dim).astype(np.float32) for _ in range(vector_count)]
    query = np.random.random(vector_dim).astype(np.float32)

    # Initialize optimizer with or without GPU
    optimizer = AISEOOptimizer(use_gpu=use_gpu)

    # Check if GPU is actually being used
    if use_gpu:
        gpu_status = optimizer.check_gpu_status()
        logger.info(f"GPU status: {gpu_status}")

    # Time the similarity calculation
    start_time = time.time()

    # Perform similarity search using the RAG system
    for vector in vectors:
        # Convert to list to avoid numpy array truth value error
        optimizer.rag._cosine_similarity(query.tolist(), vector.tolist())

    end_time = time.time()
    elapsed = end_time - start_time

    logger.info(f"Time taken for {vector_count} similarity calculations: {elapsed:.4f} seconds")
    return elapsed

def benchmark_batch_similarity(use_gpu=True, vector_count=10000, vector_dim=768, batch_size=100):
    """Benchmark batch vector similarity calculations."""
    logger.info(f"Benchmarking batch vector similarity with {'GPU' if use_gpu else 'CPU'}")

    # Create random vectors
    vectors = [np.random.random(vector_dim).astype(np.float32) for _ in range(vector_count)]
    query = np.random.random(vector_dim).astype(np.float32)

    # Initialize optimizer with or without GPU
    optimizer = AISEOOptimizer(use_gpu=use_gpu)

    # Time the batch similarity calculation
    start_time = time.time()

    # Use the batch similarity method - convert to lists to avoid numpy array truth value error
    vectors_list = [v.tolist() for v in vectors]
    optimizer.rag._batch_cosine_similarity(query.tolist(), vectors_list, batch_size=batch_size)

    end_time = time.time()
    elapsed = end_time - start_time

    logger.info(f"Time taken for batch similarity with {vector_count} vectors: {elapsed:.4f} seconds")
    return elapsed

def benchmark_listing_optimization(use_gpu=True):
    """Benchmark listing optimization."""
    logger.info(f"Benchmarking listing optimization with {'GPU' if use_gpu else 'CPU'}")

    # Initialize optimizer with or without GPU
    optimizer = AISEOOptimizer(use_gpu=use_gpu)

    # Sample listing data
    listing_data = {
        "title_original": "Cat Lover T-Shirt - Funny Cat Tee for Cat Mom - Cat Dad Gift",
        "tags_original": ["cat lover", "cat shirt", "funny cat", "cat mom", "cat dad", "cat gift"],
        "description_original": "This is a sample description for a cat lover t-shirt.",
        "base_keyword": "cat lover",
        "product_type": "t-shirt"
    }

    # Time the optimization
    start_time = time.time()

    # Optimize the listing
    optimizer.optimize_listing_ai(listing_data=listing_data)

    end_time = time.time()
    elapsed = end_time - start_time

    logger.info(f"Time taken for listing optimization: {elapsed:.4f} seconds")
    return elapsed

def main():
    """Main function to run benchmarks."""
    parser = argparse.ArgumentParser(description="Test GPU acceleration for AI SEO optimizer")
    parser.add_argument("--cpu-only", action="store_true", help="Run tests in CPU mode only")
    args = parser.parse_args()

    # Verify GPU availability
    gpu_available = verify_gpu_availability()

    if args.cpu_only:
        logger.info("Running in CPU-only mode as requested")
        run_gpu_tests = False
    else:
        run_gpu_tests = gpu_available

    # Run benchmarks
    results = {}

    # Vector similarity benchmark
    cpu_time = benchmark_vector_similarity(use_gpu=False)
    results["vector_similarity_cpu"] = cpu_time

    if run_gpu_tests:
        gpu_time = benchmark_vector_similarity(use_gpu=True)
        results["vector_similarity_gpu"] = gpu_time
        results["vector_similarity_speedup"] = cpu_time / gpu_time if gpu_time > 0 else 0

    # Batch similarity benchmark
    cpu_time = benchmark_batch_similarity(use_gpu=False)
    results["batch_similarity_cpu"] = cpu_time

    if run_gpu_tests:
        gpu_time = benchmark_batch_similarity(use_gpu=True)
        results["batch_similarity_gpu"] = gpu_time
        results["batch_similarity_speedup"] = cpu_time / gpu_time if gpu_time > 0 else 0

    # Listing optimization benchmark
    cpu_time = benchmark_listing_optimization(use_gpu=False)
    results["listing_optimization_cpu"] = cpu_time

    if run_gpu_tests:
        gpu_time = benchmark_listing_optimization(use_gpu=True)
        results["listing_optimization_gpu"] = gpu_time
        results["listing_optimization_speedup"] = cpu_time / gpu_time if gpu_time > 0 else 0

    # Print summary
    logger.info("\n--- Benchmark Results ---")
    for key, value in results.items():
        if "speedup" in key:
            logger.info(f"{key}: {value:.2f}x")
        else:
            logger.info(f"{key}: {value:.4f} seconds")

if __name__ == "__main__":
    main()