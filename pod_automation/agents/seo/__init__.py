"""
SEO Optimization module for POD Automation System.

This module provides tools for optimizing Etsy listings with SEO.
"""

# Import base components
from pod_automation.agents.seo.seo_optimizer import SEOOptimizer
from pod_automation.agents.seo.db import seo_db, SEODatabase

# Import AI components (if available)
try:
    from pod_automation.agents.seo.ai import AISEOOptimizer, OllamaClient, RAGSystem
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False

__version__ = "2.0.0"