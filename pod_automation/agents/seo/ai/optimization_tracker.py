"""
Tracking system for SEO optimizations.

This module provides functionality to track and analyze SEO optimization performance.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class OptimizationTracker:
    """Tracking system for SEO optimizations."""
    
    def __init__(self, db_client):
        """Initialize optimization tracker.
        
        Args:
            db_client: Database client
        """
        self.db = db_client
        logger.info("Initialized optimization tracker")
    
    def record_optimization(self, listing_id, optimization_data):
        """Record an optimization.
        
        Args:
            listing_id (int): Listing ID
            optimization_data (dict): Optimization data
            
        Returns:
            dict: Recorded optimization history entry
        """
        logger.info(f"Recording optimization for listing {listing_id}")
        
        try:
            # Extract data
            optimization_type = optimization_data.get("type", "full_ai")
            changes_made = optimization_data.get("changes", {})
            algorithm_version = optimization_data.get("algorithm_version", "ai_seo_optimizer_v1")
            performance_metrics = optimization_data.get("metrics", {})
            
            # Add optimization history
            history_entry = self.db.add_optimization_history(
                listing_id,
                optimization_type,
                changes_made,
                algorithm_version,
                performance_metrics
            )
            
            return history_entry
        except Exception as e:
            logger.error(f"Error recording optimization: {str(e)}")
            return None
    
    def update_performance(self, listing_id, performance_data):
        """Update performance metrics for an optimization.
        
        Args:
            listing_id (int): Listing ID
            performance_data (dict): Performance data
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"Updating performance for listing {listing_id}")
        
        try:
            # Get the latest optimization history entry
            history = self.db.get_optimization_history(listing_id)
            
            if not history:
                logger.error(f"No optimization history found for listing {listing_id}")
                return False
            
            latest_entry = history[0]
            
            # Update performance metrics
            current_metrics = latest_entry.get("performance_metrics", {})
            updated_metrics = {**current_metrics, **performance_data}
            
            # Add optimization history with updated metrics
            self.db.add_optimization_history(
                listing_id,
                latest_entry.get("optimization_type", "full_ai"),
                latest_entry.get("changes_made", {}),
                latest_entry.get("algorithm_version", "ai_seo_optimizer_v1"),
                updated_metrics
            )
            
            return True
        except Exception as e:
            logger.error(f"Error updating performance: {str(e)}")
            return False
    
    def get_optimization_performance(self, listing_id):
        """Get performance data for a listing.
        
        Args:
            listing_id (int): Listing ID
            
        Returns:
            dict: Performance data
        """
        logger.info(f"Getting optimization performance for listing {listing_id}")
        
        try:
            # Get optimization history
            history = self.db.get_optimization_history(listing_id)
            
            if not history:
                logger.error(f"No optimization history found for listing {listing_id}")
                return {}
            
            # Extract performance metrics from all entries
            performance_data = {
                "history": [
                    {
                        "date": entry.get("optimization_date"),
                        "type": entry.get("optimization_type"),
                        "metrics": entry.get("performance_metrics", {})
                    }
                    for entry in history
                ]
            }
            
            # Add latest metrics
            if history and "performance_metrics" in history[0]:
                performance_data["latest_metrics"] = history[0]["performance_metrics"]
            
            return performance_data
        except Exception as e:
            logger.error(f"Error getting optimization performance: {str(e)}")
            return {}
    
    def analyze_performance_trends(self, days=30, min_optimizations=5):
        """Analyze performance trends across all optimized listings.
        
        Args:
            days (int): Number of days to analyze
            min_optimizations (int): Minimum number of optimizations required
            
        Returns:
            dict: Performance trends
        """
        logger.info(f"Analyzing performance trends for the last {days} days")
        
        try:
            # Get all listings with status 'optimized' or 'approved'
            optimized_listings = self.db.get_listings(status='optimized')
            approved_listings = self.db.get_listings(status='approved')
            
            all_listings = optimized_listings + approved_listings
            
            # Filter listings optimized within the specified time period
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            recent_listings = [
                listing for listing in all_listings
                if listing.get("optimization_date", "") >= cutoff_date
            ]
            
            if len(recent_listings) < min_optimizations:
                logger.warning(f"Not enough recent optimizations ({len(recent_listings)}) for meaningful analysis")
                return {
                    "status": "insufficient_data",
                    "message": f"Need at least {min_optimizations} optimizations in the last {days} days for analysis",
                    "count": len(recent_listings)
                }
            
            # Collect performance metrics
            metrics = []
            for listing in recent_listings:
                if listing.get("id"):
                    performance = self.get_optimization_performance(listing["id"])
                    if performance and "latest_metrics" in performance:
                        metrics.append({
                            "listing_id": listing["id"],
                            "etsy_listing_id": listing.get("etsy_listing_id"),
                            "optimization_date": listing.get("optimization_date"),
                            "metrics": performance["latest_metrics"]
                        })
            
            # Calculate average metrics
            avg_metrics = {}
            for metric_name in ["optimization_score", "views", "favorites", "sales"]:
                values = [m["metrics"].get(metric_name, 0) for m in metrics if metric_name in m["metrics"]]
                if values:
                    avg_metrics[metric_name] = sum(values) / len(values)
            
            # Identify top performing listings
            top_listings = sorted(
                metrics,
                key=lambda m: m["metrics"].get("optimization_score", 0),
                reverse=True
            )[:5]
            
            return {
                "status": "success",
                "total_optimizations": len(recent_listings),
                "analyzed_optimizations": len(metrics),
                "average_metrics": avg_metrics,
                "top_performing_listings": top_listings
            }
        except Exception as e:
            logger.error(f"Error analyzing performance trends: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }