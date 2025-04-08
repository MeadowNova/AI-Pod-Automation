"""
Main __init__.py for pod_automation package
"""

__version__ = "0.1.0"
__author__ = "POD Automation Team"
__description__ = "Automation system for print-on-demand product creation and management"

# Import main components for easier access
from pod_automation.api import PrintifyAPI, EtsyAPI
from pod_automation.config import get_config
from pod_automation.utils import optimize_api_client

__all__ = [
    'PrintifyAPI',
    'EtsyAPI',
    'get_config',
    'optimize_api_client'
]
