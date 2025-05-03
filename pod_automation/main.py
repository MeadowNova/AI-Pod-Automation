"""
Main entry point for POD Automation System.
"""

import os
import sys
import argparse
import logging

# Set up path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import utilities
from pod_automation.utils.logging_config import setup_logging, get_logger

# Set up logging
setup_logging(log_file="pod_automation.log")
logger = get_logger(__name__)

# Import core components
from pod_automation.core.system import PODAutomationSystem

def main():
    """Main function for POD Automation System."""
    parser = argparse.ArgumentParser(description="POD Automation System")
    
    # Add arguments
    parser.add_argument('--setup', action='store_true', help='Set up API keys')
    parser.add_argument('--validate', action='store_true', help='Validate API connections')
    parser.add_argument('--run', action='store_true', help='Run full pipeline')
    parser.add_argument('--dashboard', action='store_true', help='Run interactive dashboard')
    parser.add_argument('--keyword', type=str, default='cat lover', help='Base keyword for pipeline')
    parser.add_argument('--products', type=str, default='t-shirt,poster', help='Product types (comma-separated)')
    parser.add_argument('--publish', action='store_true', help='Publish products')
    parser.add_argument('--config', type=str, help='Path to configuration file')
    
    # Parse arguments
    args = parser.parse_args()
    
    logger.info("Starting POD Automation System...")
    
    # Create POD Automation System
    system = PODAutomationSystem(config_path=args.config)
    
    # Process commands
    if args.setup:
        system.setup_api_keys()
    
    elif args.validate:
        validation = system.validate_api_connections()
        
        print("\n--- API Connection Validation ---")
        print(f"Printify API: {'Connected' if validation['printify'] else 'Not Connected'}")
        print(f"Etsy API: {'Connected' if validation['etsy'] else 'Not Connected'}")
        print(f"Stable Diffusion API: {'Connected' if validation['stable_diffusion'] else 'Not Connected'}")
    
    elif args.run:
        product_types = args.products.split(',')
        results = system.run_full_pipeline(
            keyword=args.keyword,
            product_types=product_types,
            publish=args.publish
        )
        
        print("\n--- Pipeline Results ---")
        print(f"Keyword: {results['keyword']}")
        print(f"Product Types: {', '.join(results['product_types'])}")
        print(f"Designs Generated: {len(results['designs'])}")
        
        total_mockups = sum(len(mockups) for mockups in results['mockups'].values())
        print(f"Mockups Created: {total_mockups}")
        
        if args.publish:
            print(f"Products Published: {len(results['published_products'])}")
    
    elif args.dashboard:
        system.run_dashboard()
    
    else:
        # Default to showing help
        parser.print_help()

if __name__ == "__main__":
    main()
