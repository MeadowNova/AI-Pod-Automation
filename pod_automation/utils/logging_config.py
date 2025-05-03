"""
Logging configuration for POD Automation System.
Provides consistent logging setup across all modules.
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Optional

def setup_logging(
    log_level: int = logging.INFO,
    log_file: Optional[str] = None,
    console: bool = True,
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
) -> None:
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (default: INFO)
        log_file: Path to log file (default: None)
        console: Whether to log to console (default: True)
        log_format: Log message format
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Add file handler if log_file is specified
    if log_file:
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Add console handler if console is True
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # Suppress excessive logging from third-party libraries
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """Get logger with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
