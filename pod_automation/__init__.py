"""
POD Automation System - A comprehensive solution for print-on-demand automation.
"""

__version__ = "0.1.0"
__author__ = "POD Automation Team"
__description__ = "Automation system for print-on-demand product creation and management"

# Import main components for easier access
from pod_automation.pod_automation_system import PODAutomationSystem
from pod_automation.config import get_config, Config

__all__ = [
    'PODAutomationSystem',
    'get_config',
    'Config'
]
