"""
Database access layer for the SEO module.

This module provides functions for interacting with the SEO database tables in Supabase.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Union

import supabase
from pod_automation.config import get_config

logger = logging.getLogger(__name__)

class SEODatabase:
    """Database access layer for the SEO module."""
    
    def __init__(self, supabase_url=None, supabase_key=None):
        """Initialize the SEO database client.
        
        Args:
            supabase_url (str, optional): Supabase URL. If not provided, will be loaded from config.
            supabase_key (str, optional): Supabase API key. If not provided, will be loaded from config.
        """
        config = get_config()
        self.supabase_url = supabase_url or config.get("supabase.url")
        self.supabase_key = supabase_key or config.get("supabase.key")
        
        if not self.supabase_url or not self.supabase_key:
            logger.warning("Supabase URL or key not set. Database functionality will be limited.")
            self.client = None
        else:
            try:
                self.client = supabase.create_client(self.supabase_url, self.supabase_key)
                logger.info("Connected to Supabase database")
            except Exception as e:
                logger.error(f"Failed to connect to Supabase: {str(e)}")
                self.client = None
    
    def is_connected(self) -> bool:
        """Check if connected to the database.
        
        Returns:
            bool: True if connected, False otherwise
        """
        return self.client is not None
    
    # Listing operations
    
    def get_listing(self, etsy_listing_id: int) -> Optional[Dict[str, Any]]:
        """Get a listing by Etsy listing ID.
        
        Args:
            etsy_listing_id (int): Etsy listing ID
            
        Returns:
            dict: Listing data or None if not found
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return None
        
        try:
            response = self.client.table('seo_listings').select('*').eq('etsy_listing_id', etsy_listing_id).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error getting listing {etsy_listing_id}: {str(e)}")
            return None
    
    def get_listings(self, status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get listings with optional filtering by status.
        
        Args:
            status (str, optional): Filter by status (pending, optimized, approved, rejected, updated)
            limit (int, optional): Maximum number of results to return
            offset (int, optional): Offset for pagination
            
        Returns:
            list: List of listing data
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return []
        
        try:
            query = self.client.table('seo_listings').select('*').order('created_at', desc=True).limit(limit).offset(offset)
            
            if status:
                query = query.eq('status', status)
            
            response = query.execute()
            
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting listings: {str(e)}")
            return []
    
    def create_or_update_listing(self, etsy_listing_id: int, listing_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create or update a listing.
        
        Args:
            etsy_listing_id (int): Etsy listing ID
            listing_data (dict): Listing data
            
        Returns:
            dict: Created or updated listing data or None if failed
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return None
        
        try:
            # Check if listing exists
            existing = self.get_listing(etsy_listing_id)
            
            # Prepare data
            data = {
                'etsy_listing_id': etsy_listing_id,
                'updated_at': datetime.now().isoformat()
            }
            data.update(listing_data)
            
            if existing:
                # Update existing listing
                response = self.client.table('seo_listings').update(data).eq('id', existing['id']).execute()
            else:
                # Create new listing
                response = self.client.table('seo_listings').insert(data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error creating/updating listing {etsy_listing_id}: {str(e)}")
            return None
    
    def update_listing_status(self, etsy_listing_id: int, status: str, user_id: Optional[str] = None) -> bool:
        """Update a listing's status.
        
        Args:
            etsy_listing_id (int): Etsy listing ID
            status (str): New status (pending, optimized, approved, rejected, updated)
            user_id (str, optional): User ID who made the change
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return False
        
        try:
            data = {
                'status': status,
                'updated_at': datetime.now().isoformat()
            }
            
            if status == 'approved' or status == 'rejected':
                data['approval_date'] = datetime.now().isoformat()
                if user_id:
                    data['user_id'] = user_id
            
            response = self.client.table('seo_listings').update(data).eq('etsy_listing_id', etsy_listing_id).execute()
            
            return response.data is not None and len(response.data) > 0
        except Exception as e:
            logger.error(f"Error updating listing status {etsy_listing_id}: {str(e)}")
            return False
    
    # Optimization history operations
    
    def add_optimization_history(self, listing_id: int, optimization_type: str, changes_made: Dict[str, Any], 
                                algorithm_version: Optional[str] = None, 
                                performance_metrics: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Add an optimization history entry.
        
        Args:
            listing_id (int): Listing ID (from seo_listings table)
            optimization_type (str): Type of optimization (tags, title, description, full)
            changes_made (dict): Changes made during optimization
            algorithm_version (str, optional): Version of optimization algorithm used
            performance_metrics (dict, optional): Performance metrics
            
        Returns:
            dict: Created history entry or None if failed
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return None
        
        try:
            data = {
                'listing_id': listing_id,
                'optimization_type': optimization_type,
                'changes_made': changes_made,
                'optimization_date': datetime.now().isoformat()
            }
            
            if algorithm_version:
                data['algorithm_version'] = algorithm_version
            
            if performance_metrics:
                data['performance_metrics'] = performance_metrics
            
            response = self.client.table('seo_optimization_history').insert(data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error adding optimization history for listing {listing_id}: {str(e)}")
            return None
    
    def get_optimization_history(self, listing_id: int) -> List[Dict[str, Any]]:
        """Get optimization history for a listing.
        
        Args:
            listing_id (int): Listing ID (from seo_listings table)
            
        Returns:
            list: List of optimization history entries
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return []
        
        try:
            response = self.client.table('seo_optimization_history').select('*').eq('listing_id', listing_id).order('optimization_date', desc=True).execute()
            
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting optimization history for listing {listing_id}: {str(e)}")
            return []
    
    # Keyword operations
    
    def get_keywords(self, category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get keywords with optional filtering by category.
        
        Args:
            category (str, optional): Filter by category
            limit (int, optional): Maximum number of results to return
            
        Returns:
            list: List of keyword data
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return []
        
        try:
            query = self.client.table('seo_keywords').select('*').limit(limit)
            
            if category:
                query = query.eq('category', category)
            
            response = query.execute()
            
            return response.data or []
        except Exception as e:
            logger.error(f"Error getting keywords: {str(e)}")
            return []
    
    def add_or_update_keyword(self, keyword: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Add or update a keyword.
        
        Args:
            keyword (str): Keyword
            data (dict): Keyword data
            
        Returns:
            dict: Created or updated keyword data or None if failed
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return None
        
        try:
            # Check if keyword exists
            response = self.client.table('seo_keywords').select('*').eq('keyword', keyword).execute()
            existing = response.data[0] if response.data and len(response.data) > 0 else None
            
            # Prepare data
            keyword_data = {
                'keyword': keyword,
                'last_updated': datetime.now().isoformat()
            }
            keyword_data.update(data)
            
            if existing:
                # Update existing keyword
                response = self.client.table('seo_keywords').update(keyword_data).eq('id', existing['id']).execute()
            else:
                # Create new keyword
                response = self.client.table('seo_keywords').insert(keyword_data).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            return None
        except Exception as e:
            logger.error(f"Error adding/updating keyword {keyword}: {str(e)}")
            return None
    
    # Settings operations
    
    def get_setting(self, setting_name: str) -> Optional[str]:
        """Get a setting value.
        
        Args:
            setting_name (str): Setting name
            
        Returns:
            str: Setting value or None if not found
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return None
        
        try:
            response = self.client.table('seo_settings').select('setting_value').eq('setting_name', setting_name).execute()
            
            if response.data and len(response.data) > 0:
                return response.data[0]['setting_value']
            return None
        except Exception as e:
            logger.error(f"Error getting setting {setting_name}: {str(e)}")
            return None
    
    def set_setting(self, setting_name: str, setting_value: str, description: Optional[str] = None) -> bool:
        """Set a setting value.
        
        Args:
            setting_name (str): Setting name
            setting_value (str): Setting value
            description (str, optional): Setting description
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to database")
            return False
        
        try:
            # Check if setting exists
            response = self.client.table('seo_settings').select('*').eq('setting_name', setting_name).execute()
            existing = response.data[0] if response.data and len(response.data) > 0 else None
            
            # Prepare data
            data = {
                'setting_name': setting_name,
                'setting_value': setting_value,
                'updated_at': datetime.now().isoformat()
            }
            
            if description:
                data['description'] = description
            
            if existing:
                # Update existing setting
                response = self.client.table('seo_settings').update(data).eq('id', existing['id']).execute()
            else:
                # Create new setting
                response = self.client.table('seo_settings').insert(data).execute()
            
            return response.data is not None and len(response.data) > 0
        except Exception as e:
            logger.error(f"Error setting {setting_name}: {str(e)}")
            return False


# Initialize database client
seo_db = SEODatabase()

# Convenience functions

def get_listing(etsy_listing_id: int) -> Optional[Dict[str, Any]]:
    """Get a listing by Etsy listing ID."""
    return seo_db.get_listing(etsy_listing_id)

def get_listings(status: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """Get listings with optional filtering by status."""
    return seo_db.get_listings(status, limit, offset)

def create_or_update_listing(etsy_listing_id: int, listing_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Create or update a listing."""
    return seo_db.create_or_update_listing(etsy_listing_id, listing_data)

def update_listing_status(etsy_listing_id: int, status: str, user_id: Optional[str] = None) -> bool:
    """Update a listing's status."""
    return seo_db.update_listing_status(etsy_listing_id, status, user_id)

def add_optimization_history(listing_id: int, optimization_type: str, changes_made: Dict[str, Any],
                           algorithm_version: Optional[str] = None,
                           performance_metrics: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """Add an optimization history entry."""
    return seo_db.add_optimization_history(listing_id, optimization_type, changes_made, algorithm_version, performance_metrics)

def get_optimization_history(listing_id: int) -> List[Dict[str, Any]]:
    """Get optimization history for a listing."""
    return seo_db.get_optimization_history(listing_id)

def get_keywords(category: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
    """Get keywords with optional filtering by category."""
    return seo_db.get_keywords(category, limit)

def add_or_update_keyword(keyword: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Add or update a keyword."""
    return seo_db.add_or_update_keyword(keyword, data)

def get_setting(setting_name: str) -> Optional[str]:
    """Get a setting value."""
    return seo_db.get_setting(setting_name)

def set_setting(setting_name: str, setting_value: str, description: Optional[str] = None) -> bool:
    """Set a setting value."""
    return seo_db.set_setting(setting_name, setting_value, description)