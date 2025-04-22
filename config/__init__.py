"""
Config package initialization for pod_automation.
This module provides access to configuration utilities for the POD Automation System.
"""

# Import and expose configuration modules
from config.config import get_config, Config
from config.default_config import DEFAULT_CONFIG
from config.logging_config import setup_logging

