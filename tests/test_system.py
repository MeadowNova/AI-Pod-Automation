"""
Test script for POD Automation System.
Tests all components to ensure they work together correctly.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
import unittest
from unittest.mock import patch, MagicMock

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("system_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import system
from pod_automation_system import PODAutomationSystem
from pod_automation.config import Config

class TestPODAutomationSystem(unittest.TestCase):
    """Test case for POD Automation System."""
    
    def setUp(self):
        """Set up test environment."""
        # Create test config
        self.test_config = {
            'data_dir': 'test_data',
            'printify.api_key': 'test_printify_api_key',
            'printify.shop_id': 'test_printify_shop_id',
            'etsy.api_key': 'test_etsy_api_key',
            'etsy.api_secret': 'test_etsy_api_secret',
            'etsy.shop_id': 'test_etsy_shop_id',
            'stable_diffusion.api_key': 'test_sd_api_key',
            'default_product_types': ['t-shirt', 'poster']
        }
        
        # Create test directories
        self.test_dirs = [
            'test_data',
            'test_data/designs',
            'test_data/mockups',
            'test_data/trends',
            'test_data/seo',
            'test_data/published'
        ]
        
        for directory in self.test_dirs:
            os.makedirs(directory, exist_ok=True)
        
        # Create test config file
        with open('test_config.json', 'w') as f:
            json.dump(self.test_config, f)
        
        # Create system with test config
        self.system = PODAutomationSystem(config_path='test_config.json')
        
        # Mock components
        self.mock_components()
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test config file
        if os.path.exists('test_config.json'):
            os.remove('test_config.json')
        
        # Remove test directories
        for directory in reversed(self.test_dirs):
            if os.path.exists(directory):
                # Remove files in directory
                for file in os.listdir(directory):
                    file_path = os.path.join(directory, file)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                
                # Remove directory
                os.rmdir(directory)
    
    def mock_components(self):
        """Mock system components."""
        # Mock trend forecaster
        self.system.trend_forecaster = MagicMock()
        self.system.trend_forecaster.run_trend_analysis.return_value = 'test_data/trends/trend_report_test.md'
        
        # Mock prompt optimizer
        self.system.prompt_optimizer = MagicMock()
        self.system.prompt_optimizer.optimize_prompt.return_value = ('optimized prompt', 'negative prompt')
        
        # Mock stable diffusion
        self.system.stable_diffusion = MagicMock()
        self.system.stable_diffusion.generate_image.return_value = (True, 'test_data/designs/test_design.png')
        
        # Mock design pipeline
        self.system.design_pipeline = MagicMock()
        self.system.design_pipeline.run_pipeline.return_value = [
            'test_data/designs/test_design1.png',
            'test_data/designs/test_design2.png'
        ]
        
        # Mock mockup generator
        self.system.mockup_generator = MagicMock()
        self.system.mockup_generator.create_mockups_for_design.return_value = [
            'test_data/mockups/test_mockup1.png',
            'test_data/mockups/test_mockup2.png'
        ]
        
        # Mock publishing agent
        self.system.publishing_agent = MagicMock()
        self.system.publishing_agent.validate_api_connections.return_value = {
            'printify': {'connected': True, 'shop_info': {'id': '123', 'title': 'Test Shop'}},
            'etsy': {'connected': True, 'shop_info': {'shop_id': '456', 'shop_name': 'Test Etsy Shop'}}
        }
        self.system.publishing_agent.publish_design.return_value = {
            'design': 'test_data/designs/test_design1.png',
            'title': 'Test Title',
            'description': 'Test Description',
            'printify_products': [{'product_id': '789', 'product_type': 't-shirt', 'title': 'Test T-Shirt'}],
            'etsy_listings': [{'listing_id': '101112', 'title': 'Test Etsy Listing'}]
        }
        
        # Mock SEO optimizer
        self.system.seo_optimizer = MagicMock()
        self.system.seo_optimizer.optimize_listing.return_value = {
            'base_keyword': 'cat lover',
            'product_type': 't-shirt',
            'tags': ['cat', 'cat lover', 'cat t-shirt', 'cat gift', 'funny cat'],
            'title': 'Cat Lover T-Shirt - Perfect Gift for Cat Lovers',
            'description': 'Test description'
        }
    
    def test_initialization(self):
        """Test system initialization."""
        # Check if system was initialized correctly
        self.assertIsNotNone(self.system)
        self.assertEqual(self.system.data_dir, 'test_data')
        self.assertEqual(self.system.designs_dir, 'test_data/designs')
        self.assertEqual(self.system.mockups_dir, 'test_data/mockups')
        self.assertEqual(self.system.trends_dir, 'test_data/trends')
        self.assertEqual(self.system.seo_dir, 'test_data/seo')
        self.assertEqual(self.system.output_dir, 'test_data/published')
    
    def test_validate_api_connections(self):
        """Test API connection validation."""
        # Run validation
        validation = self.system.validate_api_connections()
        
        # Check results
        self.assertTrue(validation['printify'])
        self.assertTrue(validation['etsy'])
        self.assertTrue(validation['stable_diffusion'])
        
        # Verify publishing agent method was called
        self.system.publishing_agent.validate_api_connections.assert_called_once()
    
    def test_setup_api_keys(self):
        """Test API key setup."""
        # Mock input function
        with patch('builtins.input', side_effect=[
            'new_printify_api_key',
            'new_printify_shop_id',
            'new_etsy_api_key',
            'new_etsy_api_secret',
            'new_etsy_shop_id',
            'new_sd_api_key'
        ]):
            # Run setup with interactive=False to avoid actual input
            result = self.system.setup_api_keys(interactive=False)
        
        # Check result
        self.assertTrue(result)
    
    def test_run_full_pipeline(self):
        """Test running the full pipeline."""
        # Run pipeline
        results = self.system.run_full_pipeline(
            keyword='cat lover',
            product_types=['t-shirt', 'poster'],
            publish=True
        )
        
        # Check results
        self.assertEqual(results['keyword'], 'cat lover')
        self.assertEqual(results['product_types'], ['t-shirt', 'poster'])
        self.assertEqual(results['trend_analysis'], 'test_data/trends/trend_report_test.md')
        self.assertEqual(len(results['designs']), 2)
        self.assertEqual(len(results['mockups']), 2)
        self.assertIsNotNone(results['seo_optimization'])
        self.assertEqual(len(results['published_products']), 2)
        
        # Verify component methods were called
        self.system.trend_forecaster.run_trend_analysis.assert_called_once()
        self.system.design_pipeline.run_pipeline.assert_called_once()
        self.assertEqual(self.system.mockup_generator.create_mockups_for_design.call_count, 2)
        self.system.seo_optimizer.optimize_listing.assert_called_once()
        self.assertEqual(self.system.publishing_agent.publish_design.call_count, 2)
    
    def test_run_full_pipeline_no_publish(self):
        """Test running the full pipeline without publishing."""
        # Run pipeline without publishing
        results = self.system.run_full_pipeline(
            keyword='cat lover',
            product_types=['t-shirt', 'poster'],
            publish=False
        )
        
        # Check results
        self.assertEqual(results['keyword'], 'cat lover')
        self.assertEqual(results['product_types'], ['t-shirt', 'poster'])
        self.assertEqual(results['trend_analysis'], 'test_data/trends/trend_report_test.md')
        self.assertEqual(len(results['designs']), 2)
        self.assertEqual(len(results['mockups']), 2)
        self.assertIsNotNone(results['seo_optimization'])
        self.assertEqual(len(results['published_products']), 0)
        
        # Verify publishing agent method was not called
        self.system.publishing_agent.publish_design.assert_not_called()
    
    def test_run_dashboard(self):
        """Test running the dashboard."""
        # Mock dashboard
        with patch('pod_automation.dashboard.Dashboard') as mock_dashboard:
            # Mock dashboard instance
            mock_dashboard_instance = MagicMock()
            mock_dashboard.return_value = mock_dashboard_instance
            
            # Run dashboard
            result = self.system.run_dashboard()
        
        # Check result
        self.assertTrue(result)
        
        # Verify dashboard was created and run
        mock_dashboard.assert_called_once()
        mock_dashboard_instance.run_dashboard.assert_called_once()

class TestIntegration(unittest.TestCase):
    """Integration tests for POD Automation System."""
    
    def setUp(self):
        """Set up test environment."""
        # Create test config
        self.test_config = {
            'data_dir': 'integration_test_data',
            'printify.api_key': os.environ.get('PRINTIFY_API_KEY', ''),
            'printify.shop_id': os.environ.get('PRINTIFY_SHOP_ID', ''),
            'etsy.api_key': os.environ.get('ETSY_API_KEY', ''),
            'etsy.api_secret': os.environ.get('ETSY_API_SECRET', ''),
            'etsy.shop_id': os.environ.get('ETSY_SHOP_ID', ''),
            'stable_diffusion.api_key': os.environ.get('OPENROUTER_API_KEY', ''),
            'default_product_types': ['t-shirt', 'poster']
        }
        
        # Create test directories
        self.test_dirs = [
            'integration_test_data',
            'integration_test_data/designs',
            'integration_test_data/mockups',
            'integration_test_data/trends',
            'integration_test_data/seo',
            'integration_test_data/published'
        ]
        
        for directory in self.test_dirs:
            os.makedirs(directory, exist_ok=True)
        
        # Create test config file
        with open('integration_test_config.json', 'w') as f:
            json.dump(self.test_config, f)
        
        # Create system with test config
        self.system = PODAutomationSystem(config_path='integration_test_config.json')
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove test config file
        if os.path.exists('integration_test_config.json'):
            os.remove('integration_test_config.json')
        
        # Keep test directories for inspection
    
    @unittest.skipIf(not os.environ.get('RUN_INTEGRATION_TESTS'), "Integration tests disabled")
    def test_api_validation(self):
        """Test API validation with real credentials."""
        # Run validation
        validation = self.system.validate_api_connections()
        
        # Log results
        logger.info(f"API validation results: {validation}")
        
        # Check if at least one API is connected
        self.assertTrue(any(validation.values()), "No APIs connected. Check environment variables.")
    
    @unittest.skipIf(not os.environ.get('RUN_INTEGRATION_TESTS'), "Integration tests disabled")
    def test_trend_forecasting(self):
        """Test trend forecasting with real API."""
        # Run trend analysis
        report_path = self.system.trend_forecaster.run_trend_analysis(['cat lover'])
        
        # Check if report was created
        self.assertIsNotNone(report_path)
        self.assertTrue(os.path.exists(report_path))
    
    @unittest.skipIf(not os.environ.get('RUN_INTEGRATION_TESTS'), "Integration tests disabled")
    def test_design_generation(self):
        """Test design generation with real API."""
        # Skip if no Stable Diffusion API key
        if not os.environ.get('OPENROUTER_API_KEY'):
            self.skipTest("No Stable Diffusion API key provided")
        
        # Run design generation
        designs = self.system.design_pipeline.run_pipeline(
            analyze_trends=False,
            base_keyword='cat lover',
            num_designs=1
        )
        
        # Check if designs were created
        self.assertIsNotNone(designs)
        self.assertTrue(len(designs) > 0)
        self.assertTrue(os.path.exists(designs[0]))
    
    @unittest.skipIf(not os.environ.get('RUN_INTEGRATION_TESTS'), "Integration tests disabled")
    def test_seo_optimization(self):
        """Test SEO optimization."""
        # Run SEO optimization
        optimized_listing = self.system.seo_optimizer.optimize_listing('cat lover', 't-shirt')
        
        # Check if listing was optimized
        self.assertIsNotNone(optimized_listing)
        self.assertEqual(optimized_listing['base_keyword'], 'cat lover')
        self.assertEqual(optimized_listing['product_type'], 't-shirt')
        self.assertTrue(len(optimized_listing['tags']) > 0)
        self.assertTrue(len(optimized_listing['title']) > 0)
        self.assertTrue(len(optimized_listing['description']) > 0)

def run_tests():
    """Run all tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add unit tests
    suite.addTest(unittest.makeSuite(TestPODAutomationSystem))
    
    # Add integration tests if enabled
    if os.environ.get('RUN_INTEGRATION_TESTS'):
        suite.addTest(unittest.makeSuite(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == "__main__":
    # Set environment variable to enable integration tests
    # os.environ['RUN_INTEGRATION_TESTS'] = '1'
    
    # Run tests
    run_tests()
