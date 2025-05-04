"""
Main integration module for POD Automation System.
Ensures all components work together seamlessly.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from pathlib import Path
import argparse

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

# Import components
from pod_automation.agents.trend.trend_forecaster import TrendForecaster
from pod_automation.agents.prompt_optimizer import PromptOptimizer
from pod_automation.agents.stable_diffusion import create_stable_diffusion_client
from pod_automation.agents.design.design_generation import DesignGenerationPipeline
from pod_automation.agents.mockup.mockup_generator import MockupGenerator
from pod_automation.agents.publishing.publishing_agent import PublishingAgent
from pod_automation.agents.seo.seo_optimizer import SEOOptimizer
from pod_automation.config import get_config, Config

class PODAutomationSystem:
    """Main class for POD Automation System integration."""
    
    def __init__(self, config_path=None):
        """Initialize POD Automation System.
        
        Args:
            config_path (str, optional): Path to configuration file
        """
        # Load configuration
        if config_path:
            self.config = Config(config_path)
        else:
            self.config = get_config()
        
        # Set up directories
        self.data_dir = self.config.get('data_dir', 'data')
        self.designs_dir = os.path.join(self.data_dir, 'designs')
        self.mockups_dir = os.path.join(self.data_dir, 'mockups')
        self.trends_dir = os.path.join(self.data_dir, 'trends')
        self.seo_dir = os.path.join(self.data_dir, 'seo')
        self.output_dir = os.path.join(self.data_dir, 'published')
        
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.designs_dir, exist_ok=True)
        os.makedirs(self.mockups_dir, exist_ok=True)
        os.makedirs(self.trends_dir, exist_ok=True)
        os.makedirs(self.seo_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize components
        self.trend_forecaster = None
        self.prompt_optimizer = None
        self.stable_diffusion = None
        self.design_pipeline = None
        self.mockup_generator = None
        self.publishing_agent = None
        self.seo_optimizer = None
        
        # Initialize all components
        self.initialize_components()
    
    def initialize_components(self):
        """Initialize all components."""
        logger.info("Initializing all components")
        
        # Initialize trend forecaster
        if self.trend_forecaster is None:
            self.trend_forecaster = TrendForecaster(config={'data_dir': self.trends_dir})
            logger.info("Trend Forecaster initialized")
        
        # Initialize prompt optimizer
        if self.prompt_optimizer is None:
            self.prompt_optimizer = PromptOptimizer()
            logger.info("Prompt Optimizer initialized")
        
        # Initialize stable diffusion
        if self.stable_diffusion is None:
            api_key = self.config.get('stable_diffusion.api_key') or os.environ.get('OPENROUTER_API_KEY')
            self.stable_diffusion = create_stable_diffusion_client(
                use_api=True,
                api_key=api_key,
                config={'output_dir': os.path.join(self.designs_dir, 'drafts')}
            )
            logger.info("Stable Diffusion client initialized")
        
        # Initialize design pipeline
        if self.design_pipeline is None:
            self.design_pipeline = DesignGenerationPipeline(config={
                'output_dir': os.path.join(self.designs_dir, 'drafts'),
                'trend_dir': self.trends_dir,
                'use_stable_diffusion_api': True,
                'stable_diffusion_api_key': self.config.get('stable_diffusion.api_key') or os.environ.get('OPENROUTER_API_KEY')
            })
            logger.info("Design Generation Pipeline initialized")
        
        # Initialize mockup generator
        if self.mockup_generator is None:
            self.mockup_generator = MockupGenerator(config={
                'designs_dir': self.designs_dir,
                'output_dir': self.mockups_dir
            })
            logger.info("Mockup Generator initialized")
        
        # Initialize publishing agent
        if self.publishing_agent is None:
            self.publishing_agent = PublishingAgent(config={
                'designs_dir': self.designs_dir,
                'mockups_dir': self.mockups_dir,
                'output_dir': self.output_dir,
                'printify_api_key': self.config.get('printify.api_key') or os.environ.get('PRINTIFY_API_KEY'),
                'printify_shop_id': self.config.get('printify.shop_id') or os.environ.get('PRINTIFY_SHOP_ID'),
                'etsy_api_key': self.config.get('etsy.api_key') or os.environ.get('ETSY_API_KEY'),
                'etsy_api_secret': self.config.get('etsy.api_secret') or os.environ.get('ETSY_API_SECRET'),
                'etsy_shop_id': self.config.get('etsy.shop_id') or os.environ.get('ETSY_SHOP_ID')
            })
            logger.info("Publishing Agent initialized")
        
        # Initialize SEO optimizer
        if self.seo_optimizer is None:
            self.seo_optimizer = SEOOptimizer(config={
                'data_dir': self.seo_dir
            })
            logger.info("SEO Optimizer initialized")
    
    def validate_api_connections(self):
        """Validate API connections.
        
        Returns:
            dict: Validation results
        """
        logger.info("Validating API connections")
        
        results = {
            'printify': False,
            'etsy': False,
            'stable_diffusion': False
        }
        
        # Validate Printify and Etsy connections
        if self.publishing_agent:
            try:
                validation = self.publishing_agent.validate_api_connections()
                results['printify'] = validation['printify']['connected']
                results['etsy'] = validation['etsy']['connected']
            except Exception as e:
                logger.error(f"Error validating Printify/Etsy API connections: {str(e)}")
        
        # Validate Stable Diffusion connection
        if self.stable_diffusion:
            try:
                api_key = self.config.get('stable_diffusion.api_key') or os.environ.get('OPENROUTER_API_KEY')
                results['stable_diffusion'] = bool(api_key)
            except Exception as e:
                logger.error(f"Error validating Stable Diffusion API connection: {str(e)}")
        
        logger.info(f"API validation results: {results}")
        
        return results
    
    def setup_api_keys(self, interactive=True):
        """Set up API keys.
        
        Args:
            interactive (bool, optional): Whether to prompt for input interactively
            
        Returns:
            bool: True if setup was successful, False otherwise
        """
        logger.info("Setting up API keys")
        
        try:
            if interactive:
                print("\n=== POD Automation System API Setup ===\n")
                
                # Printify API
                print("\n--- Printify API ---")
                printify_api_key = input("Enter Printify API Key: ").strip()
                printify_shop_id = input("Enter Printify Shop ID: ").strip()
                
                # Etsy API
                print("\n--- Etsy API ---")
                etsy_api_key = input("Enter Etsy API Key: ").strip()
                etsy_api_secret = input("Enter Etsy API Secret: ").strip()
                etsy_shop_id = input("Enter Etsy Shop ID (optional): ").strip()
                
                # Stable Diffusion API
                print("\n--- Stable Diffusion API ---")
                stable_diffusion_api_key = input("Enter OpenRouter API Key: ").strip()
                
                # Save API keys to config
                self.config.set('printify.api_key', printify_api_key)
                self.config.set('printify.shop_id', printify_shop_id)
                self.config.set('etsy.api_key', etsy_api_key)
                self.config.set('etsy.api_secret', etsy_api_secret)
                self.config.set('etsy.shop_id', etsy_shop_id)
                self.config.set('stable_diffusion.api_key', stable_diffusion_api_key)
                
                # Save config
                self.config.save_config()
                
                print("\nAPI keys saved successfully!")
            
            # Reinitialize components
            self.initialize_components()
            
            # Validate API connections
            validation = self.validate_api_connections()
            
            if interactive:
                print("\n--- API Connection Validation ---")
                print(f"Printify API: {'Connected' if validation['printify'] else 'Not Connected'}")
                print(f"Etsy API: {'Connected' if validation['etsy'] else 'Not Connected'}")
                print(f"Stable Diffusion API: {'Connected' if validation['stable_diffusion'] else 'Not Connected'}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error setting up API keys: {str(e)}")
            if interactive:
                print(f"\nError setting up API keys: {str(e)}")
            return False
    
    def run_full_pipeline(self, keyword="cat lover", product_types=None, publish=False):
        """Run the full POD automation pipeline.
        
        Args:
            keyword (str, optional): Base keyword for trend analysis and design generation
            product_types (list, optional): List of product types to create
            publish (bool, optional): Whether to publish products
            
        Returns:
            dict: Pipeline results
        """
        logger.info(f"Running full pipeline for keyword: {keyword}")
        
        # Use default product types if none specified
        if product_types is None:
            product_types = self.config.get('default_product_types', ['t-shirt', 'poster'])
        
        # Initialize results
        results = {
            'keyword': keyword,
            'product_types': product_types,
            'trend_analysis': None,
            'designs': [],
            'mockups': {},
            'seo_optimization': None,
            'published_products': []
        }
        
        try:
            # Step 1: Trend Analysis
            logger.info("Step 1: Running trend analysis")
            trend_report = self.trend_forecaster.run_trend_analysis([keyword])
            results['trend_analysis'] = trend_report
            
            # Step 2: Design Generation
            logger.info("Step 2: Generating designs")
            designs = self.design_pipeline.run_pipeline(
                analyze_trends=False,
                base_keyword=keyword,
                num_designs=3
            )
            results['designs'] = designs
            
            if not designs:
                logger.error("Design generation failed. Stopping pipeline.")
                return results
            
            # Step 3: Mockup Creation
            logger.info("Step 3: Creating mockups")
            for design_path in designs:
                mockups = self.mockup_generator.create_mockups_for_design(
                    design_path,
                    product_types=product_types
                )
                results['mockups'][design_path] = mockups
            
            # Step 4: SEO Optimization
            logger.info("Step 4: Optimizing SEO")
            optimized_listing = self.seo_optimizer.optimize_listing(keyword, product_types[0])
            results['seo_optimization'] = optimized_listing
            
            # Step 5: Publishing (if requested)
            if publish:
                logger.info("Step 5: Publishing products")
                for design_path, mockup_paths in results['mockups'].items():
                    if mockup_paths:
                        published = self.publishing_agent.publish_design(
                            design_path=design_path,
                            title=optimized_listing['title'],
                            description=optimized_listing['description'],
                            product_types=product_types,
                            tags=optimized_listing['tags'],
                            mockup_paths=mockup_paths
                        )
                        
                        if published:
                            results['published_products'].append(published)
            
            logger.info("Full pipeline completed successfully")
            
            return results
        
        except Exception as e:
            logger.error(f"Error running full pipeline: {str(e)}")
            return results
    
    def run_dashboard(self):
        """Run the interactive dashboard."""
        logger.info("Starting interactive dashboard")
        
        try:
            # Import dashboard module
            from pod_automation.dashboard import Dashboard
            
            # Create and run dashboard
            dashboard = Dashboard()
            dashboard.run_dashboard()
            
            return True
        
        except Exception as e:
            logger.error(f"Error running dashboard: {str(e)}")
            return False

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
        # Default to running dashboard
        system.run_dashboard()

if __name__ == "__main__":
    main()
