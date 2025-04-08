"""
Main module for POD Automation System.
Entry point for the application.
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pod_automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from pod_automation.api import PrintifyAPI, EtsyAPI
from pod_automation.config import get_config

def setup_api_connections(args):
    """Set up API connections with user-provided keys.
    
    Args:
        args: Command line arguments
        
    Returns:
        tuple: (PrintifyAPI, EtsyAPI) instances
    """
    config = get_config()
    
    # Printify setup
    printify_api_key = args.printify_key or config.get("api.printify.api_key")
    printify_shop_id = args.printify_shop or config.get("api.printify.shop_id")
    
    if not printify_api_key:
        printify_api_key = input("Enter your Printify API key: ")
        config.set("api.printify.api_key", printify_api_key)
    
    if not printify_shop_id:
        printify_shop_id = input("Enter your Printify shop ID: ")
        config.set("api.printify.shop_id", printify_shop_id)
    
    # Etsy setup
    etsy_api_key = args.etsy_key or config.get("api.etsy.api_key")
    etsy_api_secret = args.etsy_secret or config.get("api.etsy.api_secret")
    etsy_shop_id = args.etsy_shop or config.get("api.etsy.shop_id")
    
    if not etsy_api_key:
        etsy_api_key = input("Enter your Etsy API key: ")
        config.set("api.etsy.api_key", etsy_api_key)
    
    if not etsy_api_secret:
        etsy_api_secret = input("Enter your Etsy API secret: ")
        config.set("api.etsy.api_secret", etsy_api_secret)
    
    if not etsy_shop_id:
        etsy_shop_id = input("Enter your Etsy shop ID (leave blank to detect automatically): ")
        if etsy_shop_id:
            config.set("api.etsy.shop_id", etsy_shop_id)
    
    # Save config
    config.save_config()
    
    # Initialize API clients
    printify = PrintifyAPI(api_key=printify_api_key, shop_id=printify_shop_id)
    etsy = EtsyAPI(api_key=etsy_api_key, api_secret=etsy_api_secret, shop_id=etsy_shop_id)
    
    return printify, etsy

def validate_api_connections(printify, etsy):
    """Validate API connections.
    
    Args:
        printify: PrintifyAPI instance
        etsy: EtsyAPI instance
        
    Returns:
        tuple: (bool, bool) indicating success of Printify and Etsy connections
    """
    # Test Printify connection
    printify_success = False
    try:
        shop_info = printify.get_shop()
        logger.info(f"Successfully connected to Printify shop: {shop_info.get('title', 'Unknown')}")
        printify_success = True
    except Exception as e:
        logger.error(f"Failed to connect to Printify API: {str(e)}")
    
    # Test Etsy connection
    etsy_success = False
    try:
        # Check if we need to authenticate
        if not etsy.access_token:
            logger.info("No Etsy access token found. Starting OAuth flow...")
            if etsy.start_oauth_flow():
                logger.info("Etsy authentication successful.")
            else:
                logger.error("Etsy authentication failed.")
                return printify_success, False
        
        # Get user info
        user_info = etsy.get_user()
        logger.info(f"Successfully connected to Etsy as user: {user_info.get('user', {}).get('login_name', 'Unknown')}")
        
        # Get shop info if needed
        if not etsy.shop_id:
            shops = user_info.get('shops', [])
            if shops:
                shop_id = shops[0].get('shop_id')
                config = get_config()
                config.set("api.etsy.shop_id", shop_id)
                config.save_config()
                etsy.shop_id = shop_id
                logger.info(f"Detected Etsy shop ID: {shop_id}")
        
        # Get shop info
        if etsy.shop_id:
            shop_info = etsy.get_shop()
            logger.info(f"Successfully connected to Etsy shop: {shop_info.get('shop_name', 'Unknown')}")
        
        etsy_success = True
    except Exception as e:
        logger.error(f"Failed to connect to Etsy API: {str(e)}")
    
    return printify_success, etsy_success

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="POD Automation System")
    
    # API connection arguments
    parser.add_argument("--printify-key", help="Printify API key")
    parser.add_argument("--printify-shop", help="Printify shop ID")
    parser.add_argument("--etsy-key", help="Etsy API key")
    parser.add_argument("--etsy-secret", help="Etsy API secret")
    parser.add_argument("--etsy-shop", help="Etsy shop ID")
    
    # Action arguments
    parser.add_argument("--validate", action="store_true", help="Validate API connections")
    parser.add_argument("--setup", action="store_true", help="Set up API connections")
    
    args = parser.parse_args()
    
    logger.info("Starting POD Automation System...")
    
    if args.setup or args.validate:
        # Set up API connections
        printify, etsy = setup_api_connections(args)
        
        # Validate connections if requested
        if args.validate:
            printify_success, etsy_success = validate_api_connections(printify, etsy)
            
            # Print summary
            logger.info("\n=== API Connection Summary ===")
            logger.info(f"Printify API: {'SUCCESS' if printify_success else 'FAILED'}")
            logger.info(f"Etsy API: {'SUCCESS' if etsy_success else 'FAILED'}")
            
            if printify_success and etsy_success:
                logger.info("All API connections are working correctly!")
            else:
                logger.warning("Some API connections failed. Please check the logs for details.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
