"""
Simple script to verify GPU availability and configuration.
"""

import torch
import logging
from pod_automation.utils.gpu_utils import get_device, gpu_memory_stats

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def verify_gpu():
    """Verify GPU availability and configuration."""
    logger.info("Checking GPU availability...")
    
    if torch.cuda.is_available():
        device_count = torch.cuda.device_count()
        logger.info(f"✅ CUDA is available! Found {device_count} GPU device(s).")
        
        for i in range(device_count):
            device_name = torch.cuda.get_device_name(i)
            logger.info(f"  - Device {i}: {device_name}")
            
        # Get default device
        device = get_device()
        logger.info(f"Default device: {device}")
        
        # Check CUDA version
        cuda_version = torch.version.cuda
        logger.info(f"CUDA version: {cuda_version}")
        
        # Check memory stats
        memory_stats = gpu_memory_stats()
        logger.info(f"GPU memory stats: {memory_stats}")
        
        # Run a simple tensor operation on GPU
        logger.info("Running a simple tensor operation on GPU...")
        a = torch.tensor([1.0, 2.0, 3.0], device=device)
        b = torch.tensor([4.0, 5.0, 6.0], device=device)
        c = a + b
        logger.info(f"Result: {c} (on device: {c.device})")
        
        return True
    else:
        logger.warning("❌ CUDA is not available. PyTorch will use CPU only.")
        logger.info("Please check your PyTorch installation and CUDA configuration.")
        logger.info("For GPU support, you need:")
        logger.info("1. A CUDA-capable GPU (NVIDIA)")
        logger.info("2. NVIDIA drivers installed")
        logger.info("3. CUDA Toolkit installed")
        logger.info("4. PyTorch with CUDA support installed")
        
        return False

if __name__ == "__main__":
    verify_gpu()