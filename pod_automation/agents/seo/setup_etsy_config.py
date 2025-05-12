"""
Setup Etsy API configuration for the SEO module.

This script helps set up the Etsy API configuration required for the SEO module.
"""

import os
import json
import logging
import sys

from pod_automation.core.config import get_config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def setup_etsy_config():
    """Set up Etsy API configuration."""
    # Check if config file exists at default location
    default_config_path = os.path.join(os.path.expanduser("~"), ".pod_automation", "config.json")
    alt_config_path = os.path.join(os.path.expanduser("~"), ".pod_automation_config.json")
    
    config_path = default_config_path
    if not os.path.exists(default_config_path) and os.path.exists(alt_config_path):
        logger.info(f"Using alternative config path: {alt_config_path}")
        config_path = alt_config_path
    
    config = get_config(config_path)
    
    # Get current Etsy API configuration
    api_key = config.get("api.etsy.api_key")
    api_secret = config.get("api.etsy.api_secret")
    access_token = config.get("api.etsy.access_token")
    refresh_token = config.get("api.etsy.refresh_token")
    shop_id = config.get("api.etsy.shop_id")
    
    # Display current configuration
    print("\n=== Current Etsy API Configuration ===")
    print(f"API Key: {api_key or 'Not set'}")
    print(f"API Secret: {'*****' if api_secret else 'Not set'}")
    print(f"Access Token: {'*****' if access_token else 'Not set'}")
    print(f"Refresh Token: {'*****' if refresh_token else 'Not set'}")
    print(f"Shop ID: {shop_id or 'Not set'}")
    
    # Ask if user wants to update configuration
    update = input("\nDo you want to update the Etsy API configuration? (y/n): ")
    if update.lower() != 'y':
        return
    
    # Update API key
    new_api_key = input(f"Enter Etsy API Key [{api_key or ''}]: ")
    if new_api_key:
        config.set("api.etsy.api_key", new_api_key)
    
    # Update API secret
    new_api_secret = input(f"Enter Etsy API Secret [{api_secret and '*****' or ''}]: ")
    if new_api_secret:
        config.set("api.etsy.api_secret", new_api_secret)
    
    # Update access token
    new_access_token = input(f"Enter Etsy Access Token [{access_token and '*****' or ''}]: ")
    if new_access_token:
        config.set("api.etsy.access_token", new_access_token)
    
    # Update refresh token
    new_refresh_token = input(f"Enter Etsy Refresh Token [{refresh_token and '*****' or ''}]: ")
    if new_refresh_token:
        config.set("api.etsy.refresh_token", new_refresh_token)
    
    # Update shop ID
    new_shop_id = input(f"Enter Etsy Shop ID [{shop_id or ''}]: ")
    if new_shop_id:
        config.set("api.etsy.shop_id", new_shop_id)
    
    # Save configuration
    if config.save_config():
        print("\nEtsy API configuration updated successfully.")
    else:
        print("\nFailed to save Etsy API configuration.")

if __name__ == "__main__":
    setup_etsy_config()