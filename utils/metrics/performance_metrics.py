"""
Performance metrics utilities for pod_automation.
This module provides functions for tracking and reporting performance metrics.
"""

import logging
import time
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

# Global metrics storage
_performance_metrics = {
    "function_calls": {},
    "api_calls": {},
    "start_time": time.time()
}

def track_performance(function_name: str, duration: float, memory_usage: Optional[float] = None) -> None:
    """Track performance metrics for a function call.
    
    Args:
        function_name (str): Name of the function
        duration (float): Duration of the function call in seconds
        memory_usage (float, optional): Memory usage in MB
    """
    if function_name not in _performance_metrics["function_calls"]:
        _performance_metrics["function_calls"][function_name] = {
            "count": 0,
            "total_duration": 0,
            "max_duration": 0,
            "min_duration": float('inf'),
            "memory_usage": []
        }
    
    metrics = _performance_metrics["function_calls"][function_name]
    metrics["count"] += 1
    metrics["total_duration"] += duration
    metrics["max_duration"] = max(metrics["max_duration"], duration)
    metrics["min_duration"] = min(metrics["min_duration"], duration)
    
    if memory_usage is not None:
        metrics["memory_usage"].append(memory_usage)
    
    logger.debug(f"Tracked performance for {function_name}: {duration:.4f}s")

def track_api_call(api_name: str, endpoint: str, duration: float, success: bool) -> None:
    """Track performance metrics for an API call.
    
    Args:
        api_name (str): Name of the API
        endpoint (str): API endpoint
        duration (float): Duration of the API call in seconds
        success (bool): Whether the API call was successful
    """
    if api_name not in _performance_metrics["api_calls"]:
        _performance_metrics["api_calls"][api_name] = {
            "endpoints": {},
            "total_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0
        }
    
    api_metrics = _performance_metrics["api_calls"][api_name]
    api_metrics["total_calls"] += 1
    
    if success:
        api_metrics["successful_calls"] += 1
    else:
        api_metrics["failed_calls"] += 1
    
    if endpoint not in api_metrics["endpoints"]:
        api_metrics["endpoints"][endpoint] = {
            "count": 0,
            "total_duration": 0,
            "max_duration": 0,
            "min_duration": float('inf'),
            "successful_calls": 0,
            "failed_calls": 0
        }
    
    endpoint_metrics = api_metrics["endpoints"][endpoint]
    endpoint_metrics["count"] += 1
    endpoint_metrics["total_duration"] += duration
    endpoint_metrics["max_duration"] = max(endpoint_metrics["max_duration"], duration)
    endpoint_metrics["min_duration"] = min(endpoint_metrics["min_duration"], duration)
    
    if success:
        endpoint_metrics["successful_calls"] += 1
    else:
        endpoint_metrics["failed_calls"] += 1
    
    logger.debug(f"Tracked API call to {api_name}/{endpoint}: {duration:.4f}s, success={success}")

def get_performance_report() -> Dict[str, Any]:
    """Get performance report.
    
    Returns:
        dict: Performance report
    """
    report = {
        "uptime": time.time() - _performance_metrics["start_time"],
        "function_calls": {},
        "api_calls": {}
    }
    
    # Process function calls
    for function_name, metrics in _performance_metrics["function_calls"].items():
        avg_duration = metrics["total_duration"] / metrics["count"] if metrics["count"] > 0 else 0
        avg_memory = sum(metrics["memory_usage"]) / len(metrics["memory_usage"]) if metrics["memory_usage"] else None
        
        report["function_calls"][function_name] = {
            "count": metrics["count"],
            "avg_duration": avg_duration,
            "max_duration": metrics["max_duration"],
            "min_duration": metrics["min_duration"] if metrics["min_duration"] != float('inf') else 0,
            "avg_memory_usage": avg_memory
        }
    
    # Process API calls
    for api_name, api_metrics in _performance_metrics["api_calls"].items():
        report["api_calls"][api_name] = {
            "total_calls": api_metrics["total_calls"],
            "successful_calls": api_metrics["successful_calls"],
            "failed_calls": api_metrics["failed_calls"],
            "success_rate": api_metrics["successful_calls"] / api_metrics["total_calls"] if api_metrics["total_calls"] > 0 else 0,
            "endpoints": {}
        }
        
        for endpoint, endpoint_metrics in api_metrics["endpoints"].items():
            avg_duration = endpoint_metrics["total_duration"] / endpoint_metrics["count"] if endpoint_metrics["count"] > 0 else 0
            
            report["api_calls"][api_name]["endpoints"][endpoint] = {
                "count": endpoint_metrics["count"],
                "avg_duration": avg_duration,
                "max_duration": endpoint_metrics["max_duration"],
                "min_duration": endpoint_metrics["min_duration"] if endpoint_metrics["min_duration"] != float('inf') else 0,
                "successful_calls": endpoint_metrics["successful_calls"],
                "failed_calls": endpoint_metrics["failed_calls"],
                "success_rate": endpoint_metrics["successful_calls"] / endpoint_metrics["count"] if endpoint_metrics["count"] > 0 else 0
            }
    
    return report

def reset_metrics() -> None:
    """Reset all performance metrics."""
    global _performance_metrics
    _performance_metrics = {
        "function_calls": {},
        "api_calls": {},
        "start_time": time.time()
    }
    logger.info("Performance metrics reset")
    reset_metrics()
    return _performance_metrics
    