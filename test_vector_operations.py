"""
Test script to verify GPU acceleration for vector operations.
"""

import time
import logging
import torch
import numpy as np
from pod_automation.utils.gpu_utils import get_device, optimize_for_inference, clear_gpu_memory

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_vector_similarity(use_gpu=True, vector_count=100000, vector_dim=768, batch_size=5000):
    """Test vector similarity calculations with larger dataset."""
    logger.info(f"Testing vector similarity with {'GPU' if use_gpu else 'CPU'}")
    
    # Get device
    device = torch.device("cuda" if use_gpu and torch.cuda.is_available() else "cpu")
    if device.type == 'cuda':
        optimize_for_inference()
        logger.info(f"Using GPU: {torch.cuda.get_device_name(device)}")
    else:
        logger.info("Using CPU")
    
    # Create random query vector
    query = np.random.random(vector_dim).astype(np.float32)
    query_tensor = torch.tensor(query, device=device)
    query_tensor = torch.nn.functional.normalize(query_tensor.unsqueeze(0), p=2, dim=1)
    
    # Create random vectors
    logger.info(f"Creating {vector_count} random vectors...")
    vectors = np.random.random((vector_count, vector_dim)).astype(np.float32)
    
    # Time the similarity calculation
    logger.info("Starting similarity calculation...")
    start_time = time.time()
    
    # Process in batches
    for i in range(0, vector_count, batch_size):
        end_idx = min(i + batch_size, vector_count)
        batch = vectors[i:end_idx]
        
        # Convert to tensor and move to device
        batch_tensor = torch.tensor(batch, device=device)
        
        # Normalize
        batch_tensor = torch.nn.functional.normalize(batch_tensor, p=2, dim=1)
        
        # Calculate similarity
        similarities = torch.mm(query_tensor, batch_tensor.transpose(0, 1))
        
        # Move back to CPU (only for measurement, to ensure GPU computation is complete)
        _ = similarities.cpu().numpy()
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    # Clear GPU memory
    if device.type == 'cuda':
        clear_gpu_memory()
    
    logger.info(f"Time taken for {vector_count} similarity calculations: {elapsed:.4f} seconds")
    return elapsed

def main():
    """Main function."""
    # Run CPU test
    cpu_time = test_vector_similarity(use_gpu=False)
    
    # Run GPU test if available
    if torch.cuda.is_available():
        gpu_time = test_vector_similarity(use_gpu=True)
        speedup = cpu_time / gpu_time if gpu_time > 0 else 0
        logger.info(f"GPU speedup: {speedup:.2f}x")
    else:
        logger.info("GPU not available, skipping GPU test")

if __name__ == "__main__":
    main()