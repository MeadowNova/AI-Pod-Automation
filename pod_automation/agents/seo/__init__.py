"""
SEO Optimization module for Etsy listings.

This module provides functionality for optimizing Etsy listings with improved titles and tags.
"""

from pod_automation.agents.seo.seo_optimizer import SEOOptimizer
from pod_automation.agents.seo.airtable_sync import run_airtable_optimizer
from pod_automation.agents.seo.optimize_listings import optimize_listing
from pod_automation.agents.seo.tag_optimizer import TagOptimizer
from pod_automation.agents.seo.db import (
    get_listing, get_listings, create_or_update_listing, update_listing_status,
    add_optimization_history, get_optimization_history, get_keywords, add_or_update_keyword,
    get_setting, set_setting
)
from pod_automation.agents.seo.etsy_integration import (
    fetch_active_listings, import_listings_to_db, optimize_listing_from_db, update_etsy_listing
)

__all__ = [
    # Core SEO components
    'SEOOptimizer',
    'TagOptimizer',
    'run_airtable_optimizer',
    'optimize_listing',
    
    # Database functions
    'get_listing',
    'get_listings',
    'create_or_update_listing',
    'update_listing_status',
    'add_optimization_history',
    'get_optimization_history',
    'get_keywords',
    'add_or_update_keyword',
    'get_setting',
    'set_setting',
    
    # Etsy integration functions
    'fetch_active_listings',
    'import_listings_to_db',
    'optimize_listing_from_db',
    'update_etsy_listing'
]