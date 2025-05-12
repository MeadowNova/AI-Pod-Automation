"""
Database module for SEO optimization.

This module provides database access for SEO optimization.
"""

# Import the mock database for testing
from pod_automation.agents.seo.db.mock_db import MockSEODatabase

# Create a mock database instance for testing
seo_db = MockSEODatabase()

# Define the SEODatabase class for type hints
SEODatabase = MockSEODatabase
