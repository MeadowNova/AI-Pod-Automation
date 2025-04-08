"""
Unit tests for individual components of the POD Automation System.
Enhances test coverage as recommended in the audit.
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock
import json
import tempfile
import shutil

# Add parent directory to path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import components to test
from pod_automation.agents.trend_forecaster import TrendForecaster
from pod_automation.agents.prompt_optimizer import PromptOptimizer
from pod_automation.agents.seo_optimizer import SEOOptimizer
from pod_automation.agents.mockup_generator import MockupGenerator
from pod_automation.config.config import Config

class TestTrendForecaster(unittest.TestCase):
    """Test case for Trend Forecaster component."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.config = {'data_dir': self.test_dir}
        self.forecaster = TrendForecaster(config=self.config)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test initialization of trend forecaster."""
        self.assertEqual(self.forecaster.data_dir, self.test_dir)
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_get_trending_keywords(self):
        """Test getting trending keywords."""
        # Test with default category
        keywords = self.forecaster.get_trending_keywords()
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) > 0)
        
        # Test with custom category
        keywords = self.forecaster.get_trending_keywords(category="dog")
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) > 0)
        self.assertTrue(any("dog" in keyword.lower() for keyword in keywords))
    
    def test_analyze_keyword(self):
        """Test keyword analysis."""
        # Test with valid keyword
        analysis = self.forecaster.analyze_keyword("cat lover")
        self.assertIsInstance(analysis, dict)
        self.assertEqual(analysis['keyword'], "cat lover")
        self.assertIn('popularity', analysis)
        self.assertIn('competition', analysis)
        self.assertIn('trend_direction', analysis)
        self.assertIn('related_keywords', analysis)
        
        # Test with empty keyword
        analysis = self.forecaster.analyze_keyword("")
        self.assertIsInstance(analysis, dict)
        self.assertIn('error', analysis)
    
    def test_generate_trend_report(self):
        """Test trend report generation."""
        # Create test trend data
        trend_data = {
            'cat lover': {
                'keyword': 'cat lover',
                'popularity': 85,
                'competition': 70,
                'trend_direction': 'up',
                'related_keywords': ['cat enthusiast', 'feline lover'],
                'timestamp': '2025-04-08 11:30:00'
            },
            'funny cat': {
                'keyword': 'funny cat',
                'popularity': 90,
                'competition': 80,
                'trend_direction': 'up',
                'related_keywords': ['hilarious cat', 'cat humor'],
                'timestamp': '2025-04-08 11:30:00'
            }
        }
        
        # Generate report
        report_path = self.forecaster.generate_trend_report(trend_data)
        
        # Check report was created
        self.assertTrue(os.path.exists(report_path))
        
        # Check report content
        with open(report_path, 'r') as f:
            content = f.read()
            self.assertIn('# Cat-Themed Design Trend Report', content)
            self.assertIn('## Keyword Analysis', content)
            self.assertIn('### cat lover', content)
            self.assertIn('### funny cat', content)
            self.assertIn('## Design Recommendations', content)
    
    def test_run_trend_analysis(self):
        """Test running trend analysis."""
        # Test with provided keywords
        report_path = self.forecaster.run_trend_analysis(['cat lover', 'funny cat'])
        self.assertTrue(os.path.exists(report_path))
        
        # Test with no keywords (should use trending keywords)
        report_path = self.forecaster.run_trend_analysis()
        self.assertTrue(os.path.exists(report_path))
    
    @patch('requests.request')
    def test_external_data_source_handling(self, mock_request):
        """Test handling of external data sources."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'results': [{'title': 'cat lover'}]}
        mock_request.return_value = mock_response
        
        # Test successful request
        source_config = {
            'url': 'https://example.com/api',
            'method': 'GET',
            'headers': {},
            'params': {},
            'timeout': 5,
            'retry_count': 1,
            'retry_delay': 0
        }
        result = self.forecaster._fetch_from_external_source('test_source', source_config, 'cat')
        self.assertEqual(result, {'results': [{'title': 'cat lover'}]})
        
        # Mock failed response
        mock_response.status_code = 404
        
        # Test failed request
        result = self.forecaster._fetch_from_external_source('test_source', source_config, 'cat')
        self.assertIsNone(result)
        
        # Mock timeout
        mock_request.side_effect = unittest.mock.Mock(side_effect=TimeoutError("Request timed out"))
        
        # Test timeout handling
        result = self.forecaster._fetch_from_external_source('test_source', source_config, 'cat')
        self.assertIn('error', result)

class TestPromptOptimizer(unittest.TestCase):
    """Test case for Prompt Optimizer component."""
    
    def setUp(self):
        """Set up test environment."""
        self.optimizer = PromptOptimizer()
    
    def test_optimize_prompt(self):
        """Test prompt optimization."""
        # Test with simple prompt
        prompt, negative_prompt = self.optimizer.optimize_prompt("cat lover")
        self.assertIsInstance(prompt, str)
        self.assertIsInstance(negative_prompt, str)
        self.assertIn("cat", prompt.lower())
        
        # Test with more specific prompt
        prompt, negative_prompt = self.optimizer.optimize_prompt("funny cat t-shirt design")
        self.assertIsInstance(prompt, str)
        self.assertIsInstance(negative_prompt, str)
        self.assertIn("cat", prompt.lower())
        self.assertIn("t-shirt", prompt.lower())
        
        # Test with empty prompt
        prompt, negative_prompt = self.optimizer.optimize_prompt("")
        self.assertIsInstance(prompt, str)
        self.assertIsInstance(negative_prompt, str)
    
    def test_generate_variations(self):
        """Test generating prompt variations."""
        # Test with default count
        variations = self.optimizer.generate_variations("cat lover")
        self.assertIsInstance(variations, list)
        self.assertEqual(len(variations), 3)
        
        # Test with custom count
        variations = self.optimizer.generate_variations("cat lover", count=5)
        self.assertIsInstance(variations, list)
        self.assertEqual(len(variations), 5)
        
        # Test with empty prompt
        variations = self.optimizer.generate_variations("")
        self.assertIsInstance(variations, list)
        self.assertTrue(len(variations) > 0)
    
    def test_evaluate_prompt(self):
        """Test prompt evaluation."""
        # Test with good prompt
        score = self.optimizer.evaluate_prompt("cute cat with big eyes, detailed fur, playful pose, high quality, 4k")
        self.assertIsInstance(score, float)
        self.assertTrue(0 <= score <= 100)
        
        # Test with basic prompt
        score = self.optimizer.evaluate_prompt("cat")
        self.assertIsInstance(score, float)
        self.assertTrue(0 <= score <= 100)
        
        # Test with empty prompt
        score = self.optimizer.evaluate_prompt("")
        self.assertIsInstance(score, float)
        self.assertTrue(0 <= score <= 100)

class TestSEOOptimizer(unittest.TestCase):
    """Test case for SEO Optimizer component."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test data
        self.test_dir = tempfile.mkdtemp()
        self.config = {'data_dir': self.test_dir}
        self.optimizer = SEOOptimizer(config=self.config)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory
        shutil.rmtree(self.test_dir)
    
    def test_initialization(self):
        """Test initialization of SEO optimizer."""
        self.assertEqual(self.optimizer.data_dir, self.test_dir)
        self.assertTrue(os.path.exists(self.test_dir))
    
    def test_optimize_tags(self):
        """Test tag optimization."""
        # Test with valid inputs
        tags = self.optimizer.optimize_tags("cat lover", "t-shirt")
        self.assertIsInstance(tags, list)
        self.assertTrue(len(tags) > 0)
        self.assertTrue(len(tags) <= 13)  # Etsy limit
        
        # Test with custom count
        tags = self.optimizer.optimize_tags("cat lover", "t-shirt", count=5)
        self.assertIsInstance(tags, list)
        self.assertEqual(len(tags), 5)
        
        # Test with empty inputs
        tags = self.optimizer.optimize_tags("", "")
        self.assertIsInstance(tags, list)
        self.assertTrue(len(tags) > 0)
    
    def test_optimize_title(self):
        """Test title optimization."""
        # Test with valid inputs
        title = self.optimizer.optimize_title("cat lover", "t-shirt")
        self.assertIsInstance(title, str)
        self.assertTrue(len(title) > 0)
        self.assertIn("cat", title.lower())
        self.assertIn("t-shirt", title.lower())
        
        # Test with tags
        tags = ["cat lover", "funny cat", "cat gift"]
        title = self.optimizer.optimize_title("cat lover", "t-shirt", tags=tags)
        self.assertIsInstance(title, str)
        self.assertTrue(len(title) > 0)
        
        # Test with empty inputs
        title = self.optimizer.optimize_title("", "")
        self.assertIsInstance(title, str)
        self.assertTrue(len(title) > 0)
    
    def test_optimize_description(self):
        """Test description optimization."""
        # Test with valid inputs
        description = self.optimizer.optimize_description("cat lover", "t-shirt")
        self.assertIsInstance(description, str)
        self.assertTrue(len(description) > 0)
        self.assertIn("cat", description.lower())
        
        # Test with tags
        tags = ["cat lover", "funny cat", "cat gift"]
        description = self.optimizer.optimize_description("cat lover", "t-shirt", tags=tags)
        self.assertIsInstance(description, str)
        self.assertTrue(len(description) > 0)
        
        # Test with empty inputs
        description = self.optimizer.optimize_description("", "")
        self.assertIsInstance(description, str)
        self.assertTrue(len(description) > 0)
    
    def test_optimize_listing(self):
        """Test listing optimization."""
        # Test with valid inputs
        listing = self.optimizer.optimize_listing("cat lover", "t-shirt")
        self.assertIsInstance(listing, dict)
        self.assertEqual(listing['base_keyword'], "cat lover")
        self.assertEqual(listing['product_type'], "t-shirt")
        self.assertIn('tags', listing)
        self.assertIn('title', listing)
        self.assertIn('description', listing)
        
        # Test with empty inputs
        listing = self.optimizer.optimize_listing("", "")
        self.assertIsInstance(listing, dict)
        self.assertIn('tags', listing)
        self.assertIn('title', listing)
        self.assertIn('description', listing)

class TestMockupGenerator(unittest.TestCase):
    """Test case for Mockup Generator component."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary directories for test data
        self.designs_dir = tempfile.mkdtemp()
        self.output_dir = tempfile.mkdtemp()
        
        # Create a test design image
        from PIL import Image, ImageDraw
        self.test_design_path = os.path.join(self.designs_dir, "test_design.png")
        img = Image.new('RGB', (800, 800), color='white')
        draw = ImageDraw.Draw(img)
        draw.rectangle([(200, 200), (600, 600)], fill='black')
        img.save(self.test_design_path)
        
        # Initialize mockup generator
        self.config = {
            'designs_dir': self.designs_dir,
            'output_dir': self.output_dir
        }
        self.generator = MockupGenerator(config=self.config)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directories
        shutil.rmtree(self.designs_dir)
        shutil.rmtree(self.output_dir)
    
    def test_initialization(self):
        """Test initialization of mockup generator."""
        self.assertEqual(self.generator.designs_dir, self.designs_dir)
        self.assertEqual(self.generator.output_dir, self.output_dir)
        self.assertTrue(os.path.exists(self.designs_dir))
        self.assertTrue(os.path.exists(self.output_dir))
    
    def test_create_mockup(self):
        """Test creating a mockup."""
        # Test with valid inputs
        mockup_path = self.generator.create_mockup(self.test_design_path, "t-shirt")
        self.assertIsInstance(mockup_path, str)
        self.assertTrue(os.path.exists(mockup_path))
        
        # Test with color
        mockup_path = self.generator.create_mockup(self.test_design_path, "t-shirt", color="black")
        self.assertIsInstance(mockup_path, str)
        self.assertTrue(os.path.exists(mockup_path))
        
        # Test with variation
        mockup_path = self.generator.create_mockup(self.test_design_path, "t-shirt", variation="v-neck")
        self.assertIsInstance(mockup_path, str)
        self.assertTrue(os.path.exists(mockup_path))
        
        # Test with invalid product type
        mockup_path = self.generator.create_mockup(self.test_design_path, "invalid_product")
        self.assertIsInstance(mockup_path, str)
        self.assertTrue(os.path.exists(mockup_path))
    
    def test_create_mockups_for_design(self):
        """Test creating mockups for a design."""
        # Test with default product types
        mockups = self.generator.create_mockups_for_design(self.test_design_path)
        self.assertIsInstance(mockups, list)
        self.assertTrue(len(mockups) > 0)
        for mockup in mockups:
            self.assertTrue(os.path.exists(mockup))
        
        # Test with specific product types
        product_types = ["t-shirt", "poster", "pillow_case"]
        mockups = self.generator.create_mockups_for_design(self.test_design_path, product_types=product_types)
        self.assertIsInstance(mockups, list)
        self.assertEqual(len(mockups), len(product_types))
        for mockup in mockups:
            self.assertTrue(os.path.exists(mockup))
        
        # Test with colors
        colors = ["black", "white", "blue"]
        mockups = self.generator.create_mockups_for_design(self.test_design_path, product_types=["t-shirt"], colors=colors)
        self.assertIsInstance(mockups, list)
        self.assertEqual(len(mockups), len(colors))
        for mockup in mockups:
            self.assertTrue(os.path.exists(mockup))
    
    def test_create_mockups_for_designs(self):
        """Test creating mockups for multiple designs."""
        # Create another test design
        second_design_path = os.path.join(self.designs_dir, "test_design2.png")
        from PIL import Image, ImageDraw
        img = Image.new('RGB', (800, 800), color='white')
        draw = ImageDraw.Draw(img)
        draw.ellipse([(200, 200), (600, 600)], fill='black')
        img.save(second_design_path)
        
        # Test with multiple designs
        design_paths = [self.test_design_path, second_design_path]
        mockups = self.generator.create_mockups_for_designs(design_paths, product_types=["t-shirt"])
        self.assertIsInstance(mockups, dict)
        self.assertEqual(len(mockups), len(design_paths))
        for design_path, design_mockups in mockups.items():
            self.assertIsInstance(design_mockups, list)
            self.assertTrue(len(design_mockups) > 0)
            for mockup in design_mockups:
                self.assertTrue(os.path.exists(mockup))

class TestConfig(unittest.TestCase):
    """Test case for Config component."""
    
    def setUp(self):
        """Set up test environment."""
        # Create temporary file for config
        self.config_file = tempfile.mktemp(suffix='.json')
        self.config = Config(config_file=self.config_file)
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary file
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
    
    def test_initialization(self):
        """Test initialization of config."""
        self.assertEqual(self.config.config_file, self.config_file)
    
    def test_create_default_config(self):
        """Test creating default config."""
        self.config.create_default_config()
        self.assertTrue(os.path.exists(self.config_file))
        
        # Check config content
        with open(self.config_file, 'r') as f:
            config_data = json.load(f)
            self.assertIn('api', config_data)
            self.assertIn('data_dir', config_data)
    
    def test_get_set_save(self):
        """Test getting, setting, and saving config values."""
        # Set a value
        self.config.set('test_key', 'test_value')
        
        # Get the value
        value = self.config.get('test_key')
        self.assertEqual(value, 'test_value')
        
        # Save the config
        self.config.save_config()
        
        # Create a new config instance and check the value
        new_config = Config(config_file=self.config_file)
        value = new_config.get('test_key')
        self.assertEqual(value, 'test_value')
    
    def test_nested_get_set(self):
        """Test getting and setting nested config values."""
        # Set nested values
        self.config.set('parent.child', 'test_value')
        
        # Get the value
        value = self.config.get('parent.child')
        self.assertEqual(value, 'test_value')
        
        # Get parent
        parent = self.config.get('parent')
        self.assertIsInstance(parent, dict)
        self.assertEqual(parent['child'], 'test_value')
    
    def test_default_value(self):
        """Test getting default value for non-existent key."""
        # Get non-existent key
        value = self.config.get('non_existent')
        self.assertIsNone(value)
        
        # Get non-existent key with default
        value = self.config.get('non_existent', 'default_value')
        self.assertEqual(value, 'default_value')

def run_tests():
    """Run all tests."""
    # Create test suite
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTest(unittest.makeSuite(TestTrendForecaster))
    suite.addTest(unittest.makeSuite(TestPromptOptimizer))
    suite.addTest(unittest.makeSuite(TestSEOOptimizer))
    suite.addTest(unittest.makeSuite(TestMockupGenerator))
    suite.addTest(unittest.makeSuite(TestConfig))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result

if __name__ == "__main__":
    run_tests()
