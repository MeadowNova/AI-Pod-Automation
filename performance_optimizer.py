"""
Performance optimization for POD Automation System.
Improves system efficiency and resource usage.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
import traceback
import cProfile
import pstats
import io
import multiprocessing
import threading
import functools
import gc
import psutil
from typing import Dict, List, Any, Callable, Optional, Tuple, Union

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("performance_optimization.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import system
from pod_automation.pod_automation_system import PODAutomationSystem
from pod_automation.config import Config

class PerformanceOptimizer:
    """Optimizer for improving POD Automation System performance."""
    
    def __init__(self, system=None, config_path=None):
        """Initialize performance optimizer.
        
        Args:
            system (PODAutomationSystem, optional): System to optimize
            config_path (str, optional): Path to configuration file
        """
        # Initialize system if not provided
        if system is None:
            self.system = PODAutomationSystem(config_path=config_path)
        else:
            self.system = system
        
        # Set up optimization directory
        self.optimization_dir = os.path.join(self.system.data_dir, 'optimization')
        os.makedirs(self.optimization_dir, exist_ok=True)
        
        # Default optimization settings
        self.settings = {
            'enable_caching': True,
            'cache_ttl': 3600,  # 1 hour
            'parallel_processing': True,
            'max_workers': multiprocessing.cpu_count(),
            'batch_size': 10,
            'memory_limit': 1024 * 1024 * 1024,  # 1 GB
            'api_rate_limiting': True,
            'api_rate_limit': {
                'printify': 60,  # requests per minute
                'etsy': 30,      # requests per minute
                'stable_diffusion': 10  # requests per minute
            },
            'lazy_loading': True,
            'compression': True,
            'log_level': 'INFO'
        }
        
        # Load settings from config if available
        self._load_settings()
    
    def _load_settings(self):
        """Load optimization settings from config."""
        try:
            # Get optimization settings from config
            config_settings = self.system.config.get('optimization', {})
            
            # Update settings with config values
            for key, value in config_settings.items():
                if key in self.settings:
                    self.settings[key] = value
            
            logger.info("Loaded optimization settings from config")
        except Exception as e:
            logger.error(f"Error loading optimization settings: {str(e)}")
    
    def save_settings(self):
        """Save optimization settings to config."""
        try:
            # Save settings to config
            self.system.config.set('optimization', self.settings)
            self.system.config.save_config()
            
            logger.info("Saved optimization settings to config")
            return True
        except Exception as e:
            logger.error(f"Error saving optimization settings: {str(e)}")
            return False
    
    def profile_function(self, func, *args, **kwargs):
        """Profile a function to identify performance bottlenecks.
        
        Args:
            func (callable): Function to profile
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            tuple: (function result, profile stats)
        """
        logger.info(f"Profiling function: {func.__name__}")
        
        # Create profiler
        profiler = cProfile.Profile()
        
        # Start profiling
        profiler.enable()
        
        # Call function
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in profiled function: {str(e)}")
            result = None
        
        # Stop profiling
        profiler.disable()
        
        # Get stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Print top 20 functions by cumulative time
        
        # Save profile results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.optimization_dir, f"profile_{func.__name__}_{timestamp}.txt")
        
        try:
            with open(file_path, 'w') as f:
                f.write(s.getvalue())
            
            logger.info(f"Profile results saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving profile results: {str(e)}")
        
        return result, s.getvalue()
    
    def profile_system(self):
        """Profile the entire system to identify performance bottlenecks.
        
        Returns:
            dict: Profile results
        """
        logger.info("Profiling system")
        
        # Initialize results
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'components': {},
            'overall': None
        }
        
        # Profile each component
        components = {
            'trend_forecaster': self.system.trend_forecaster.run_trend_analysis if self.system.trend_forecaster else None,
            'prompt_optimizer': self.system.prompt_optimizer.optimize_prompt if self.system.prompt_optimizer else None,
            'seo_optimizer': self.system.seo_optimizer.optimize_listing if self.system.seo_optimizer else None,
            'mockup_generator': self.system.mockup_generator.create_mockups_for_design if self.system.mockup_generator else None,
            'publishing_agent': self.system.publishing_agent.validate_api_connections if self.system.publishing_agent else None
        }
        
        for name, func in components.items():
            if func is not None:
                try:
                    if name == 'trend_forecaster':
                        _, profile = self.profile_function(func, ['cat lover'])
                    elif name == 'prompt_optimizer':
                        _, profile = self.profile_function(func, 'cat lover t-shirt')
                    elif name == 'seo_optimizer':
                        _, profile = self.profile_function(func, 'cat lover', 't-shirt')
                    elif name == 'mockup_generator':
                        # Find a design to use
                        designs = [f for f in os.listdir(self.system.designs_dir) 
                                  if f.endswith('.png') or f.endswith('.jpg')]
                        
                        if designs:
                            design_path = os.path.join(self.system.designs_dir, designs[0])
                            _, profile = self.profile_function(func, design_path, ['t-shirt'])
                        else:
                            logger.warning(f"No designs found for profiling {name}")
                            profile = "No designs found for profiling"
                    else:
                        _, profile = self.profile_function(func)
                    
                    results['components'][name] = profile
                except Exception as e:
                    logger.error(f"Error profiling {name}: {str(e)}")
                    results['components'][name] = f"Error: {str(e)}"
        
        # Profile full pipeline
        try:
            _, profile = self.profile_function(
                self.system.run_full_pipeline,
                keyword='cat lover',
                product_types=['t-shirt'],
                publish=False
            )
            
            results['overall'] = profile
        except Exception as e:
            logger.error(f"Error profiling full pipeline: {str(e)}")
            results['overall'] = f"Error: {str(e)}"
        
        # Save profile results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.optimization_dir, f"system_profile_{timestamp}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"System profile results saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving system profile results: {str(e)}")
        
        return results
    
    def measure_memory_usage(self, func, *args, **kwargs):
        """Measure memory usage of a function.
        
        Args:
            func (callable): Function to measure
            *args: Arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            tuple: (function result, memory usage in bytes)
        """
        logger.info(f"Measuring memory usage of function: {func.__name__}")
        
        # Get current process
        process = psutil.Process(os.getpid())
        
        # Collect garbage to get accurate baseline
        gc.collect()
        
        # Get memory usage before
        memory_before = process.memory_info().rss
        
        # Call function
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in measured function: {str(e)}")
            result = None
        
        # Collect garbage again
        gc.collect()
        
        # Get memory usage after
        memory_after = process.memory_info().rss
        
        # Calculate memory used
        memory_used = memory_after - memory_before
        
        logger.info(f"Memory usage of {func.__name__}: {memory_used / (1024 * 1024):.2f} MB")
        
        return result, memory_used
    
    def optimize_caching(self):
        """Implement caching for expensive operations.
        
        Returns:
            bool: True if optimization was successful, False otherwise
        """
        logger.info("Optimizing caching")
        
        if not self.settings['enable_caching']:
            logger.info("Caching is disabled in settings")
            return False
        
        try:
            # Create cache decorator
            def cache_result(ttl=None):
                """Decorator to cache function results.
                
                Args:
                    ttl (int, optional): Time-to-live in seconds
                """
                if ttl is None:
                    ttl = self.settings['cache_ttl']
                
                cache = {}
                
                def decorator(func):
                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        # Create cache key
                        key = str(args) + str(sorted(kwargs.items()))
                        
                        # Check if result is in cache and not expired
                        if key in cache:
                            result, timestamp = cache[key]
                            if time.time() - timestamp < ttl:
                                return result
                        
                        # Call function
                        result = func(*args, **kwargs)
                        
                        # Cache result
                        cache[key] = (result, time.time())
                        
                        return result
                    
                    return wrapper
                
                return decorator
            
            # Apply caching to expensive operations
            if self.system.trend_forecaster:
                self.system.trend_forecaster.run_trend_analysis = cache_result(3600)(self.system.trend_forecaster.run_trend_analysis)
            
            if self.system.seo_optimizer:
                self.system.seo_optimizer.analyze_competitor_listings = cache_result(3600)(self.system.seo_optimizer.analyze_competitor_listings)
            
            if self.system.publishing_agent:
                self.system.publishing_agent.validate_api_connections = cache_result(300)(self.system.publishing_agent.validate_api_connections)
            
            logger.info("Caching optimization applied")
            return True
        
        except Exception as e:
            logger.error(f"Error optimizing caching: {str(e)}")
            return False
    
    def optimize_parallel_processing(self):
        """Implement parallel processing for independent operations.
        
        Returns:
            bool: True if optimization was successful, False otherwise
        """
        logger.info("Optimizing parallel processing")
        
        if not self.settings['parallel_processing']:
            logger.info("Parallel processing is disabled in settings")
            return False
        
        try:
            # Create parallel executor
            from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
            
            # Use ThreadPoolExecutor for I/O-bound operations
            thread_executor = ThreadPoolExecutor(max_workers=self.settings['max_workers'])
            
            # Use ProcessPoolExecutor for CPU-bound operations
            process_executor = ProcessPoolExecutor(max_workers=self.settings['max_workers'])
            
            # Apply parallel processing to suitable operations
            if self.system.mockup_generator:
                original_create_mockups = self.system.mockup_generator.create_mockups_for_designs
                
                def parallel_create_mockups(design_paths, product_types=None, colors=None):
                    """Create mockups for multiple designs in parallel."""
                    # Submit tasks to thread executor
                    futures = []
                    for design_path in design_paths:
                        future = thread_executor.submit(
                            self.system.mockup_generator.create_mockups_for_design,
                            design_path,
                            product_types,
                            colors
                        )
                        futures.append((design_path, future))
                    
                    # Collect results
                    mockups_by_design = {}
                    for design_path, future in futures:
                        try:
                            mockups = future.result()
                            mockups_by_design[design_path] = mockups
                        except Exception as e:
                            logger.error(f"Error creating mockups for {design_path}: {str(e)}")
                            mockups_by_design[design_path] = []
                    
                    return mockups_by_design
                
                self.system.mockup_generator.create_mockups_for_designs = parallel_create_mockups
            
            if self.system.design_pipeline:
                # Store reference to original method
                original_run_pipeline = self.system.design_pipeline.run_pipeline
                
                def parallel_run_pipeline(analyze_trends=True, base_keyword=None, num_designs=3):
                    """Run design generation pipeline with parallel processing."""
                    if num_designs <= 1:
                        # Use original method for single design
                        return original_run_pipeline(analyze_trends, base_keyword, num_designs)
                    
                    # For multiple designs, use parallel processing
                    if analyze_trends:
                        # Run trend analysis first
                        trend_results = self.system.trend_forecaster.run_trend_analysis([base_keyword] if base_keyword else None)
                        
                        # Extract keywords from trend results
                        # This is a simplified implementation; in a real system, you would parse the trend report
                        keywords = [base_keyword] if base_keyword else ['cat lover', 'cat t-shirt', 'funny cat']
                    else:
                        keywords = [base_keyword] if base_keyword else ['cat lover', 'cat t-shirt', 'funny cat']
                    
                    # Generate prompts
                    prompts = []
                    for i in range(num_designs):
                        keyword = keywords[i % len(keywords)]
                        optimized_prompt, neg_prompt = self.system.prompt_optimizer.optimize_prompt(keyword)
                        prompts.append((optimized_prompt, neg_prompt))
                    
                    # Generate designs in parallel
                    futures = []
                    for prompt, neg_prompt in prompts:
                        future = process_executor.submit(
                            self.system.stable_diffusion.generate_image,
                            prompt=prompt,
                            negative_prompt=neg_prompt,
                            width=1024,
                            height=1024,
                            num_inference_steps=50,
                            guidance_scale=7.5
                        )
                        futures.append(future)
                    
                    # Collect results
                    designs = []
                    for future in futures:
                        try:
                            success, result = future.result()
                            if success:
                                designs.append(result)
                        except Exception as e:
                            logger.error(f"Error generating design: {str(e)}")
                    
                    return designs
                
                self.system.design_pipeline.run_pipeline = parallel_run_pipeline
            
            logger.info("Parallel processing optimization applied")
            return True
        
        except Exception as e:
            logger.error(f"Error optimizing parallel processing: {str(e)}")
            return False
    
    def optimize_api_rate_limiting(self):
        """Implement API rate limiting to prevent hitting API limits.
        
        Returns:
            bool: True if optimization was successful, False otherwise
        """
        logger.info("Optimizing API rate limiting")
        
        if not self.settings['api_rate_limiting']:
            logger.info("API rate limiting is disabled in settings")
            return False
        
        try:
            # Create rate limiter
            class RateLimiter:
                """Rate limiter for API calls."""
                
                def __init__(self, calls_per_minute):
                    """Initialize rate limiter.
                    
                    Args:
                        calls_per_minute (int): Maximum calls per minute
                    """
                    self.calls_per_minute = calls_per_minute
                    self.interval = 60.0 / calls_per_minute
                    self.last_call = 0
                    self.lock = threading.Lock()
                
                def __call__(self, func):
                    """Decorate function with rate limiting.
                    
                    Args:
                        func (callable): Function to decorate
                    """
                    @functools.wraps(func)
                    def wrapper(*args, **kwargs):
                        with self.lock:
                            # Calculate time since last call
                            elapsed = time.time() - self.last_call
                            
                            # If not enough time has passed, sleep
                            if elapsed < self.interval:
                                time.sleep(self.interval - elapsed)
                            
                            # Update last call time
                            self.last_call = time.time()
                        
                        # Call function
                        return func(*args, **kwargs)
                    
                    return wrapper
            
            # Apply rate limiting to API calls
            if self.system.publishing_agent:
                # Rate limit Printify API calls
                printify_rate_limit = self.settings['api_rate_limit']['printify']
                printify_limiter = RateLimiter(printify_rate_limit)
                
                if hasattr(self.system.publishing_agent, 'printify') and self.system.publishing_agent.printify:
                    for method_name in ['get_shop', 'create_product', 'publish_product', 'upload_image']:
                        if hasattr(self.system.publishing_agent.printify, method_name):
                            original_method = getattr(self.system.publishing_agent.printify, method_name)
                            setattr(self.system.publishing_agent.printify, method_name, printify_limiter(original_method))
                
                # Rate limit Etsy API calls
                etsy_rate_limit = self.settings['api_rate_limit']['etsy']
                etsy_limiter = RateLimiter(etsy_rate_limit)
                
                if hasattr(self.system.publishing_agent, 'etsy') and self.system.publishing_agent.etsy:
                    for method_name in ['get_shop', 'create_listing', 'create_draft_listing', 'upload_listing_image']:
                        if hasattr(self.system.publishing_agent.etsy, method_name):
                            original_method = getattr(self.system.publishing_agent.etsy, method_name)
                            setattr(self.system.publishing_agent.etsy, method_name, etsy_limiter(original_method))
            
            # Rate limit Stable Diffusion API calls
            if self.system.stable_diffusion:
                sd_rate_limit = self.settings['api_rate_limit']['stable_diffusion']
                sd_limiter = RateLimiter(sd_rate_limit)
                
                if hasattr(self.system.stable_diffusion, 'generate_image'):
                    original_method = self.system.stable_diffusion.generate_image
                    self.system.stable_diffusion.generate_image = sd_limiter(original_method)
            
            logger.info("API rate limiting optimization applied")
            return True
        
        except Exception as e:
            logger.error(f"Error optimizing API rate limiting: {str(e)}")
            return False
    
    def optimize_lazy_loading(self):
        """Implement lazy loading for components.
        
        Returns:
            bool: True if optimization was successful, False otherwise
        """
        logger.info("Optimizing lazy loading")
        
        if not self.settings['lazy_loading']:
            logger.info("Lazy loading is disabled in settings")
            return False
        
        try:
            # Create lazy loading decorator
            def lazy_load(func):
                """Decorator to lazy load a component."""
                loaded = [False]
                result = [None]
                
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    if not loaded[0]:
                        result[0] = func(*args, **kwargs)
                        loaded[0] = True
                    return result[0]
                
                return wrapper
            
            # Apply lazy loading to component initialization
            original_initialize_components = self.system.initialize_components
            
            def lazy_initialize_components():
                """Initialize components only when needed."""
                # Don't initialize components yet
                logger.info("Components will be lazy loaded when needed")
            
            # Replace initialize_components with lazy version
            self.system.initialize_components = lazy_initialize_components
            
            # Create lazy loading properties for components
            class LazyProperty:
                """Descriptor for lazy loading properties."""
                
                def __init__(self, func):
                    """Initialize lazy property.
                    
                    Args:
                        func (callable): Function to create property
                    """
                    self.func = func
                    self.name = func.__name__
                
                def __get__(self, instance, owner):
                    """Get property value, creating it if needed."""
                    if instance is None:
                        return self
                    
                    value = self.func(instance)
                    setattr(instance, self.name, value)
                    return value
            
            # Apply lazy loading to components
            if not hasattr(self.system, '_original_trend_forecaster'):
                self.system._original_trend_forecaster = self.system.trend_forecaster
                self.system.trend_forecaster = None
            
            if not hasattr(self.system, '_original_prompt_optimizer'):
                self.system._original_prompt_optimizer = self.system.prompt_optimizer
                self.system.prompt_optimizer = None
            
            if not hasattr(self.system, '_original_stable_diffusion'):
                self.system._original_stable_diffusion = self.system.stable_diffusion
                self.system.stable_diffusion = None
            
            if not hasattr(self.system, '_original_design_pipeline'):
                self.system._original_design_pipeline = self.system.design_pipeline
                self.system.design_pipeline = None
            
            if not hasattr(self.system, '_original_mockup_generator'):
                self.system._original_mockup_generator = self.system.mockup_generator
                self.system.mockup_generator = None
            
            if not hasattr(self.system, '_original_publishing_agent'):
                self.system._original_publishing_agent = self.system.publishing_agent
                self.system.publishing_agent = None
            
            if not hasattr(self.system, '_original_seo_optimizer'):
                self.system._original_seo_optimizer = self.system.seo_optimizer
                self.system.seo_optimizer = None
            
            # Add lazy loading properties
            def get_trend_forecaster(self):
                """Lazy load trend forecaster."""
                if self._original_trend_forecaster is not None:
                    return self._original_trend_forecaster
                
                from pod_automation.agents.trend_forecaster import TrendForecaster
                return TrendForecaster(config={'data_dir': self.trends_dir})
            
            def get_prompt_optimizer(self):
                """Lazy load prompt optimizer."""
                if self._original_prompt_optimizer is not None:
                    return self._original_prompt_optimizer
                
                from pod_automation.agents.prompt_optimizer import PromptOptimizer
                return PromptOptimizer()
            
            def get_stable_diffusion(self):
                """Lazy load stable diffusion."""
                if self._original_stable_diffusion is not None:
                    return self._original_stable_diffusion
                
                from pod_automation.agents.stable_diffusion import create_stable_diffusion_client
                api_key = self.config.get('stable_diffusion.api_key') or os.environ.get('OPENROUTER_API_KEY')
                return create_stable_diffusion_client(
                    use_api=True,
                    api_key=api_key,
                    config={'output_dir': self.designs_dir}
                )
            
            def get_design_pipeline(self):
                """Lazy load design pipeline."""
                if self._original_design_pipeline is not None:
                    return self._original_design_pipeline
                
                from pod_automation.agents.design_generation import DesignGenerationPipeline
                return DesignGenerationPipeline(config={
                    'output_dir': self.designs_dir,
                    'trend_dir': self.trends_dir,
                    'use_stable_diffusion_api': True,
                    'stable_diffusion_api_key': self.config.get('stable_diffusion.api_key') or os.environ.get('OPENROUTER_API_KEY')
                })
            
            def get_mockup_generator(self):
                """Lazy load mockup generator."""
                if self._original_mockup_generator is not None:
                    return self._original_mockup_generator
                
                from pod_automation.agents.mockup_generator import MockupGenerator
                return MockupGenerator(config={
                    'designs_dir': self.designs_dir,
                    'output_dir': self.mockups_dir
                })
            
            def get_publishing_agent(self):
                """Lazy load publishing agent."""
                if self._original_publishing_agent is not None:
                    return self._original_publishing_agent
                
                from pod_automation.agents.publishing_agent import PublishingAgent
                return PublishingAgent(config={
                    'designs_dir': self.designs_dir,
                    'mockups_dir': self.mockups_dir,
                    'output_dir': self.output_dir,
                    'printify_api_key': self.config.get('printify.api_key') or os.environ.get('PRINTIFY_API_KEY'),
                    'printify_shop_id': self.config.get('printify.shop_id') or os.environ.get('PRINTIFY_SHOP_ID'),
                    'etsy_api_key': self.config.get('etsy.api_key') or os.environ.get('ETSY_API_KEY'),
                    'etsy_api_secret': self.config.get('etsy.api_secret') or os.environ.get('ETSY_API_SECRET'),
                    'etsy_shop_id': self.config.get('etsy.shop_id') or os.environ.get('ETSY_SHOP_ID')
                })
            
            def get_seo_optimizer(self):
                """Lazy load SEO optimizer."""
                if self._original_seo_optimizer is not None:
                    return self._original_seo_optimizer
                
                from pod_automation.agents.seo_optimizer import SEOOptimizer
                return SEOOptimizer(config={
                    'data_dir': self.seo_dir
                })
            
            # Add properties to system class
            PODAutomationSystem.trend_forecaster = property(get_trend_forecaster)
            PODAutomationSystem.prompt_optimizer = property(get_prompt_optimizer)
            PODAutomationSystem.stable_diffusion = property(get_stable_diffusion)
            PODAutomationSystem.design_pipeline = property(get_design_pipeline)
            PODAutomationSystem.mockup_generator = property(get_mockup_generator)
            PODAutomationSystem.publishing_agent = property(get_publishing_agent)
            PODAutomationSystem.seo_optimizer = property(get_seo_optimizer)
            
            logger.info("Lazy loading optimization applied")
            return True
        
        except Exception as e:
            logger.error(f"Error optimizing lazy loading: {str(e)}")
            return False
    
    def optimize_compression(self):
        """Implement compression for data storage and transfer.
        
        Returns:
            bool: True if optimization was successful, False otherwise
        """
        logger.info("Optimizing compression")
        
        if not self.settings['compression']:
            logger.info("Compression is disabled in settings")
            return False
        
        try:
            import gzip
            import shutil
            from PIL import Image
            
            # Create compression decorator for file operations
            def compress_file(func):
                """Decorator to compress files after creation."""
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    # Call original function
                    result = func(*args, **kwargs)
                    
                    # Check if result is a file path
                    if isinstance(result, str) and os.path.isfile(result):
                        # Check file type
                        if result.endswith('.json'):
                            # Compress JSON files
                            compressed_path = result + '.gz'
                            with open(result, 'rb') as f_in:
                                with gzip.open(compressed_path, 'wb') as f_out:
                                    shutil.copyfileobj(f_in, f_out)
                            
                            # Remove original file
                            os.remove(result)
                            
                            # Update result
                            result = compressed_path
                        elif result.endswith(('.png', '.jpg', '.jpeg')):
                            # Optimize image files
                            try:
                                img = Image.open(result)
                                img.save(result, optimize=True, quality=85)
                            except Exception as e:
                                logger.error(f"Error optimizing image {result}: {str(e)}")
                    
                    return result
                
                return wrapper
            
            # Apply compression to file operations
            if self.system.trend_forecaster:
                if hasattr(self.system.trend_forecaster, 'save_trend_report'):
                    self.system.trend_forecaster.save_trend_report = compress_file(self.system.trend_forecaster.save_trend_report)
            
            if self.system.seo_optimizer:
                if hasattr(self.system.seo_optimizer, 'generate_seo_report'):
                    self.system.seo_optimizer.generate_seo_report = compress_file(self.system.seo_optimizer.generate_seo_report)
            
            if self.system.publishing_agent:
                if hasattr(self.system.publishing_agent, 'publish_design'):
                    self.system.publishing_agent.publish_design = compress_file(self.system.publishing_agent.publish_design)
            
            # Create function to read compressed files
            def read_compressed_file(file_path):
                """Read a potentially compressed file.
                
                Args:
                    file_path (str): Path to file
                    
                Returns:
                    str: File contents
                """
                if file_path.endswith('.gz'):
                    with gzip.open(file_path, 'rt') as f:
                        return f.read()
                else:
                    with open(file_path, 'r') as f:
                        return f.read()
            
            # Add read_compressed_file to system
            self.system.read_compressed_file = read_compressed_file
            
            logger.info("Compression optimization applied")
            return True
        
        except Exception as e:
            logger.error(f"Error optimizing compression: {str(e)}")
            return False
    
    def optimize_memory_usage(self):
        """Optimize memory usage to prevent memory leaks.
        
        Returns:
            bool: True if optimization was successful, False otherwise
        """
        logger.info("Optimizing memory usage")
        
        try:
            # Create memory monitor
            class MemoryMonitor:
                """Monitor and limit memory usage."""
                
                def __init__(self, limit_bytes):
                    """Initialize memory monitor.
                    
                    Args:
                        limit_bytes (int): Memory limit in bytes
                    """
                    self.limit_bytes = limit_bytes
                    self.process = psutil.Process(os.getpid())
                
                def check_memory(self):
                    """Check current memory usage.
                    
                    Returns:
                        int: Current memory usage in bytes
                    """
                    return self.process.memory_info().rss
                
                def is_over_limit(self):
                    """Check if memory usage is over limit.
                    
                    Returns:
                        bool: True if over limit, False otherwise
                    """
                    return self.check_memory() > self.limit_bytes
                
                def reduce_memory(self):
                    """Reduce memory usage.
                    
                    Returns:
                        int: Memory freed in bytes
                    """
                    before = self.check_memory()
                    
                    # Force garbage collection
                    gc.collect()
                    
                    after = self.check_memory()
                    return before - after
            
            # Create memory monitor
            memory_monitor = MemoryMonitor(self.settings['memory_limit'])
            
            # Create memory-aware decorator
            def memory_aware(func):
                """Decorator to make function memory-aware."""
                @functools.wraps(func)
                def wrapper(*args, **kwargs):
                    # Check memory before
                    if memory_monitor.is_over_limit():
                        # Try to reduce memory
                        freed = memory_monitor.reduce_memory()
                        logger.info(f"Memory over limit before {func.__name__}, freed {freed / (1024 * 1024):.2f} MB")
                    
                    # Call function
                    result = func(*args, **kwargs)
                    
                    # Check memory after
                    if memory_monitor.is_over_limit():
                        # Try to reduce memory
                        freed = memory_monitor.reduce_memory()
                        logger.info(f"Memory over limit after {func.__name__}, freed {freed / (1024 * 1024):.2f} MB")
                    
                    return result
                
                return wrapper
            
            # Apply memory-aware decorator to memory-intensive operations
            if self.system.stable_diffusion:
                if hasattr(self.system.stable_diffusion, 'generate_image'):
                    self.system.stable_diffusion.generate_image = memory_aware(self.system.stable_diffusion.generate_image)
            
            if self.system.mockup_generator:
                if hasattr(self.system.mockup_generator, 'create_mockup'):
                    self.system.mockup_generator.create_mockup = memory_aware(self.system.mockup_generator.create_mockup)
            
            # Add memory monitor to system
            self.system.memory_monitor = memory_monitor
            
            logger.info("Memory usage optimization applied")
            return True
        
        except Exception as e:
            logger.error(f"Error optimizing memory usage: {str(e)}")
            return False
    
    def apply_all_optimizations(self):
        """Apply all optimizations.
        
        Returns:
            dict: Optimization results
        """
        logger.info("Applying all optimizations")
        
        # Initialize results
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'optimizations': {}
        }
        
        # Apply optimizations
        optimizations = {
            'caching': self.optimize_caching,
            'parallel_processing': self.optimize_parallel_processing,
            'api_rate_limiting': self.optimize_api_rate_limiting,
            'lazy_loading': self.optimize_lazy_loading,
            'compression': self.optimize_compression,
            'memory_usage': self.optimize_memory_usage
        }
        
        for name, func in optimizations.items():
            try:
                success = func()
                results['optimizations'][name] = success
            except Exception as e:
                logger.error(f"Error applying {name} optimization: {str(e)}")
                results['optimizations'][name] = False
        
        # Save optimization results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.optimization_dir, f"optimization_results_{timestamp}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Optimization results saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving optimization results: {str(e)}")
        
        return results
    
    def benchmark_system(self):
        """Benchmark system performance before and after optimization.
        
        Returns:
            dict: Benchmark results
        """
        logger.info("Benchmarking system performance")
        
        # Initialize results
        results = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'before': {},
            'after': {},
            'improvement': {}
        }
        
        # Define benchmark functions
        benchmark_functions = {
            'trend_analysis': lambda: self.system.trend_forecaster.run_trend_analysis(['cat lover']),
            'design_generation': lambda: self.system.design_pipeline.run_pipeline(
                analyze_trends=False,
                base_keyword='cat lover',
                num_designs=1
            ),
            'seo_optimization': lambda: self.system.seo_optimizer.optimize_listing('cat lover', 't-shirt'),
            'full_pipeline': lambda: self.system.run_full_pipeline(
                keyword='cat lover',
                product_types=['t-shirt'],
                publish=False
            )
        }
        
        # Run benchmarks before optimization
        logger.info("Running benchmarks before optimization")
        
        for name, func in benchmark_functions.items():
            try:
                start_time = time.time()
                func()
                end_time = time.time()
                
                results['before'][name] = {
                    'time': end_time - start_time,
                    'memory': psutil.Process(os.getpid()).memory_info().rss
                }
                
                logger.info(f"Benchmark {name} before optimization: {results['before'][name]['time']:.2f} seconds")
            except Exception as e:
                logger.error(f"Error benchmarking {name} before optimization: {str(e)}")
                results['before'][name] = {
                    'time': None,
                    'memory': None,
                    'error': str(e)
                }
        
        # Apply optimizations
        self.apply_all_optimizations()
        
        # Run benchmarks after optimization
        logger.info("Running benchmarks after optimization")
        
        for name, func in benchmark_functions.items():
            try:
                start_time = time.time()
                func()
                end_time = time.time()
                
                results['after'][name] = {
                    'time': end_time - start_time,
                    'memory': psutil.Process(os.getpid()).memory_info().rss
                }
                
                logger.info(f"Benchmark {name} after optimization: {results['after'][name]['time']:.2f} seconds")
            except Exception as e:
                logger.error(f"Error benchmarking {name} after optimization: {str(e)}")
                results['after'][name] = {
                    'time': None,
                    'memory': None,
                    'error': str(e)
                }
        
        # Calculate improvement
        for name in benchmark_functions:
            if (name in results['before'] and name in results['after'] and
                results['before'][name].get('time') is not None and
                results['after'][name].get('time') is not None):
                
                time_before = results['before'][name]['time']
                time_after = results['after'][name]['time']
                time_improvement = (time_before - time_after) / time_before * 100
                
                memory_before = results['before'][name]['memory']
                memory_after = results['after'][name]['memory']
                memory_improvement = (memory_before - memory_after) / memory_before * 100
                
                results['improvement'][name] = {
                    'time': time_improvement,
                    'memory': memory_improvement
                }
                
                logger.info(f"Improvement for {name}: Time: {time_improvement:.2f}%, Memory: {memory_improvement:.2f}%")
        
        # Save benchmark results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_path = os.path.join(self.optimization_dir, f"benchmark_results_{timestamp}.json")
        
        try:
            with open(file_path, 'w') as f:
                json.dump(results, f, indent=2)
            
            logger.info(f"Benchmark results saved to {file_path}")
        except Exception as e:
            logger.error(f"Error saving benchmark results: {str(e)}")
        
        return results

def main():
    """Main function for performance optimization."""
    import argparse
    
    # Parse arguments
    parser = argparse.ArgumentParser(description="Optimize POD Automation System performance")
    parser.add_argument('--config', type=str, help='Path to configuration file')
    parser.add_argument('--profile', action='store_true', help='Profile system performance')
    parser.add_argument('--optimize', action='store_true', help='Apply optimizations')
    parser.add_argument('--benchmark', action='store_true', help='Benchmark system performance')
    parser.add_argument('--all', action='store_true', help='Run all optimization steps')
    
    args = parser.parse_args()
    
    # Create system and optimizer
    system = PODAutomationSystem(config_path=args.config)
    optimizer = PerformanceOptimizer(system)
    
    # Process commands
    if args.profile:
        results = optimizer.profile_system()
        print("\n=== Profile Results ===")
        print("Profile results saved to optimization directory")
    
    elif args.optimize:
        results = optimizer.apply_all_optimizations()
        print("\n=== Optimization Results ===")
        for name, success in results['optimizations'].items():
            print(f"{name}: {'Success' if success else 'Failed'}")
    
    elif args.benchmark:
        results = optimizer.benchmark_system()
        print("\n=== Benchmark Results ===")
        for name, improvement in results['improvement'].items():
            print(f"{name}: Time: {improvement['time']:.2f}%, Memory: {improvement['memory']:.2f}%")
    
    elif args.all:
        # Run all steps
        print("\n=== Running All Optimization Steps ===")
        
        print("\n1. Profiling System")
        optimizer.profile_system()
        
        print("\n2. Applying Optimizations")
        optimization_results = optimizer.apply_all_optimizations()
        for name, success in optimization_results['optimizations'].items():
            print(f"{name}: {'Success' if success else 'Failed'}")
        
        print("\n3. Benchmarking System")
        benchmark_results = optimizer.benchmark_system()
        for name, improvement in benchmark_results['improvement'].items():
            print(f"{name}: Time: {improvement['time']:.2f}%, Memory: {improvement['memory']:.2f}%")
    
    else:
        # Default to applying optimizations
        results = optimizer.apply_all_optimizations()
        print("\n=== Optimization Results ===")
        for name, success in results['optimizations'].items():
            print(f"{name}: {'Success' if success else 'Failed'}")

if __name__ == "__main__":
    main()
