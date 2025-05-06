"""
Test script to verify GPU acceleration for a realistic SEO scenario.
"""

import time
import logging
import torch
import numpy as np
from pod_automation.utils.gpu_utils import get_device, optimize_for_inference, clear_gpu_memory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def simulate_rag_system(use_gpu=True, keyword_count=5000, listing_count=1000, embedding_dim=768, query_count=100):
    """Simulate a realistic RAG system scenario."""
    logger.info(f"Simulating RAG system with {'GPU' if use_gpu else 'CPU'}")
    logger.info(f"Keywords: {keyword_count}, Listings: {listing_count}, Queries: {query_count}")
    
    # Get device
    device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
    if device.type == 'cuda':
        optimize_for_inference()
        logger.info(f"Using GPU: {torch.cuda.get_device_name(device)}")
    else:
        logger.info("Using CPU")
    
    # Create embeddings
    logger.info("Creating embeddings...")
    keyword_embeddings = np.random.random((keyword_count, embedding_dim)).astype(np.float32)
    listing_embeddings = np.random.random((listing_count, embedding_dim)).astype(np.float32)
    query_embeddings = np.random.random((query_count, embedding_dim)).astype(np.float32)
    
    # Convert to tensors
    if use_gpu:
        # For GPU, convert and normalize all at once
        keyword_tensors = torch.tensor(keyword_embeddings, device=device)
        keyword_tensors = torch.nn.functional.normalize(keyword_tensors, p=2, dim=1)
        
        listing_tensors = torch.tensor(listing_embeddings, device=device)
        listing_tensors = torch.nn.functional.normalize(listing_tensors, p=2, dim=1)
    else:
        # For CPU, keep as numpy arrays
        keyword_tensors = None
        listing_tensors = None
    
    # Time the similarity calculations
    logger.info("Starting similarity calculations...")
    start_time = time.time()
    
    for i in range(query_count):
        query = query_embeddings[i]
        
        if use_gpu:
            # GPU version
            query_tensor = torch.tensor(query, device=device)
            query_tensor = torch.nn.functional.normalize(query_tensor.unsqueeze(0), p=2, dim=1)
            
            # Calculate similarities for keywords
            keyword_similarities = torch.mm(query_tensor, keyword_tensors.transpose(0, 1)).squeeze(0)
            top_k_keywords = torch.topk(keyword_similarities, k=10)
            
            # Calculate similarities for listings
            listing_similarities = torch.mm(query_tensor, listing_tensors.transpose(0, 1)).squeeze(0)
            top_k_listings = torch.topk(listing_similarities, k=5)
            
            # Move results to CPU (to ensure GPU computation is complete)
            _ = top_k_keywords.indices.cpu().numpy()
            _ = top_k_listings.indices.cpu().numpy()
        else:
            # CPU version
            # Normalize query
            query_norm = query / np.linalg.norm(query)
            
            # Calculate similarities for keywords
            keyword_similarities = []
            for j in range(keyword_count):
                keyword = keyword_embeddings[j]
                keyword_norm = keyword / np.linalg.norm(keyword)
                similarity = np.dot(query_norm, keyword_norm)
                keyword_similarities.append(similarity)
            
            # Get top k keywords
            top_k_keywords = np.argsort(keyword_similarities)[-10:]
            
            # Calculate similarities for listings
            listing_similarities = []
            for j in range(listing_count):
                listing = listing_embeddings[j]
                listing_norm = listing / np.linalg.norm(listing)
                similarity = np.dot(query_norm, listing_norm)
                listing_similarities.append(similarity)
            
            # Get top k listings
            top_k_listings = np.argsort(listing_similarities)[-5:]
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Clear GPU memory
    if device.type == 'cuda':
        clear_gpu_memory()
    
    logger.info(f"Time taken for {query_count} queries: {elapsed:.4f} seconds")
    return elapsed

def main():
    """Main function."""
    # Run CPU test
    cpu_time = simulate_rag_system(use_gpu=False)
    
    # Run GPU test if available
    if torch.cuda.is_available():
        gpu_time = simulate_rag_system(use_gpu=True)
        speedup = cpu_time / gpu_time if gpu_time > 0 else 0
        logger.info(f"GPU speedup: {speedup:.2f}x")
    else:
        logger.info("GPU not available, skipping GPU test")

if __name__ == "__main__":
    main()