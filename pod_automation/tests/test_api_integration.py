"""
Main module for API integration testing.
Tests Printify and Etsy API connections.
"""

import os
import sys
import logging
import json
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from pod_automation.api import PrintifyAPI, EtsyAPI, PinterestAPI
from pod_automation.config import get_config

# Set up logging
from pod_automation.utils.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

def test_printify_api():
    """Test Printify API connection and functionality."""
    logger.info("Testing Printify API connection...")

    # Get configuration
    config = get_config()
    api_key = config.get("api.printify.api_key")
    shop_id = config.get("api.printify.shop_id")

    if not api_key:
        api_key = input("Enter your Printify API key: ")
        config.set("api.printify.api_key", api_key)
        config.save_config()

    if not shop_id:
        shop_id = input("Enter your Printify shop ID: ")
        config.set("api.printify.shop_id", shop_id)
        config.save_config()

    # Initialize API client
    printify = PrintifyAPI(api_key=api_key, shop_id=shop_id)

    # Test connection
    try:
        shop_info = printify.get_shop()
        logger.info(f"Successfully connected to Printify shop: {shop_info.get('title', 'Unknown')}")
        logger.info(f"Shop ID: {shop_info.get('id', 'Unknown')}")

        # Test catalog access
        catalog = printify.get_catalog(limit=5)
        if isinstance(catalog, list):
            logger.info(f"Successfully retrieved catalog. Total blueprints: {len(catalog)}")
        elif isinstance(catalog, dict) and 'total' in catalog:
            logger.info(f"Successfully retrieved catalog. Total blueprints: {catalog.get('total', 0)}")
        else:
            logger.info("Successfully retrieved catalog.")

        # Test products access
        products = printify.get_products(limit=5)
        logger.info(f"Successfully retrieved products. Total products: {products.get('total', 0)}")

        # Print print providers for reference
        logger.info("Print providers for reference:")
        logger.info("Monster Digital - For T-Shirts and Sweatshirts")
        logger.info("Sensaria - For Posters")
        logger.info("MWW - For pillow cases")

        return True
    except Exception as e:
        logger.error(f"Failed to test Printify API: {str(e)}")
        return False

def test_etsy_api():
    """Test Etsy API connection and functionality."""
    logger.info("Testing Etsy API connection...")

    # Get configuration
    config = get_config()
    api_key = config.get("api.etsy.api_key")
    api_secret = config.get("api.etsy.api_secret")
    access_token = config.get("api.etsy.access_token")
    shop_id = config.get("api.etsy.shop_id")

    if not api_key:
        api_key = input("Enter your Etsy API key: ")
        config.set("api.etsy.api_key", api_key)
        config.save_config()

    if not api_secret:
        api_secret = input("Enter your Etsy API secret: ")
        config.set("api.etsy.api_secret", api_secret)
        config.save_config()

    # Initialize API client
    etsy = EtsyAPI(api_key=api_key, api_secret=api_secret, access_token=access_token, shop_id=shop_id)

    # Check if we need to authenticate
    if not access_token:
        logger.info("No access token found. Starting OAuth flow...")
        if etsy.start_oauth_flow():
            logger.info("Authentication successful.")
            access_token = etsy.access_token
        else:
            logger.error("Authentication failed.")
            return False

    # Test connection
    try:
        if not shop_id:
            # Get user info first
            user_info = etsy.get_user()
            logger.info(f"Successfully connected to Etsy as user: {user_info.get('user', {}).get('login_name', 'Unknown')}")

            # Get shop info
            shops = user_info.get('shops', [])
            if shops:
                shop_id = shops[0].get('shop_id')
                config.set("api.etsy.shop_id", shop_id)
                config.save_config()
                etsy.shop_id = shop_id
            else:
                shop_id = input("Enter your Etsy shop ID: ")
                config.set("api.etsy.shop_id", shop_id)
                config.save_config()
                etsy.shop_id = shop_id

        # Get shop info
        shop_info = etsy.get_shop()
        logger.info(f"Successfully connected to Etsy shop: {shop_info.get('shop_name', 'Unknown')}")
        logger.info(f"Shop ID: {shop_info.get('shop_id', 'Unknown')}")

        # Test listings access
        listings = etsy.get_listings(limit=5)
        logger.info(f"Successfully retrieved listings. Total listings: {listings.get('count', 0)}")

        return True
    except Exception as e:
        logger.error(f"Failed to test Etsy API: {str(e)}")
        return False

def test_pinterest_api():
    """Test Pinterest API connection and functionality."""
    logger.info("Testing Pinterest API connection...")

    try:
        pinterest = PinterestAPI()
        profile = pinterest.get_user_profile()
        logger.info(f"Successfully connected to Pinterest user: {profile.get('username', 'Unknown')}")
        boards = pinterest.get_boards()
        logger.info(f"Successfully retrieved {len(boards.get('items', []))} boards.")
        return True
    except Exception as e:
        logger.error(f"Failed to test Pinterest API: {str(e)}")
        return False


def main():
    """Main function to test API connections."""
    logger.info("Starting API integration tests...")

    # Test Printify API
    printify_success = test_printify_api()

    # Test Etsy API
    etsy_success = test_etsy_api()

    # Test Pinterest API
    pinterest_success = test_pinterest_api()

    # Print summary
    logger.info("\n=== API Integration Test Summary ===")
    logger.info(f"Printify API: {'SUCCESS' if printify_success else 'FAILED'}")
    logger.info(f"Etsy API: {'SUCCESS' if etsy_success else 'FAILED'}")
    logger.info(f"Pinterest API: {'SUCCESS' if pinterest_success else 'FAILED'}")

    if printify_success and etsy_success and pinterest_success:
        logger.info("All API integrations are working correctly!")
    else:
        logger.warning("Some API integrations failed. Please check the logs for details.")

if __name__ == "__main__":
    main()
