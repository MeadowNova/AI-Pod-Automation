"""
GPU utilities for PyTorch operations.
Provides functions for device selection, memory management, and GPU acceleration.
"""

import logging
import torch

logger = logging.getLogger(__name__)

def get_device(device_id=None):
    """
    Get the appropriate device (CUDA GPU or CPU) based on availability.

    Args:
        device_id (int, optional): Specific GPU device ID to use

    Returns:
        torch.device: Selected device
    """
    if not torch.cuda.is_available():
        logger.info("CUDA not available, using CPU")
        return torch.device("cpu")

    if device_id is not None:
        if device_id >= torch.cuda.device_count():
            logger.warning(f"Requested GPU {device_id} not available, using default GPU")
            device_id = None

    if device_id is None:
        device = torch.device("cuda")
        logger.info(f"Using default GPU: {torch.cuda.get_device_name(0)}")
    else:
        device = torch.device(f"cuda:{device_id}")
        logger.info(f"Using GPU {device_id}: {torch.cuda.get_device_name(device_id)}")

    return device

def to_tensor(data, device=None):
    """
    Convert data to PyTorch tensor and move to the specified device.

    Args:
        data: Data to convert (numpy array, list, etc.)
        device (torch.device, optional): Device to move tensor to

    Returns:
        torch.Tensor: Tensor on the specified device
    """
    if device is None:
        device = get_device()

    if isinstance(data, torch.Tensor):
        return data.to(device)

    return torch.tensor(data, device=device)

def batch_process(func, data, batch_size=1024, **kwargs):
    """
    Process data in batches to avoid GPU memory issues.

    Args:
        func: Function to apply to each batch
        data: Data to process
        batch_size (int): Size of each batch
        **kwargs: Additional arguments to pass to func

    Returns:
        list: Results from processing each batch
    """
    results = []
    for i in range(0, len(data), batch_size):
        batch = data[i:i+batch_size]
        batch_result = func(batch, **kwargs)
        results.append(batch_result)

    return results

def gpu_memory_stats():
    """
    Get GPU memory usage statistics.

    Returns:
        dict: Memory statistics for each GPU
    """
    if not torch.cuda.is_available():
        return {"cuda_available": False}

    stats = {"cuda_available": True, "devices": {}}
    for i in range(torch.cuda.device_count()):
        allocated = torch.cuda.memory_allocated(i) / (1024 ** 3)  # GB
        reserved = torch.cuda.memory_reserved(i) / (1024 ** 3)    # GB
        stats["devices"][i] = {
            "name": torch.cuda.get_device_name(i),
            "allocated_gb": allocated,
            "reserved_gb": reserved
        }

    return stats

def clear_gpu_memory():
    """Clear unused GPU memory cache."""
    if torch.cuda.is_available():
        # Synchronize CUDA operations before clearing cache
        torch.cuda.synchronize()
        # Empty cache to free up memory
        torch.cuda.empty_cache()
        logger.info("Cleared GPU memory cache")

def optimize_for_inference():
    """Configure PyTorch for optimal inference performance."""
    if torch.cuda.is_available():
        # Set to inference mode
        torch.set_grad_enabled(False)
        # Use TF32 precision on Ampere or newer GPUs (like RTX 4070)
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        # Use cuDNN benchmarking to find optimal algorithms
        torch.backends.cudnn.benchmark = True
        logger.info("Optimized PyTorch for GPU inference")