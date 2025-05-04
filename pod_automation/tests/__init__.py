"""
Test suite for the POD AI Automation system.

This package contains all tests for the POD AI Automation system, including:
- API integration tests
- Component tests
- System tests
- Unit tests
"""

# Import test modules for easier access
from pod_automation.tests.test_api import TestEtsyAPI, TestPrintifyAPI, TestPinterestAPI
from pod_automation.tests.test_api_integration import test_printify_api, test_etsy_api, test_pinterest_api

__all__ = [
    'TestEtsyAPI',
    'TestPrintifyAPI',
    'TestPinterestAPI',
    'test_printify_api',
    'test_etsy_api',
    'test_pinterest_api'
]