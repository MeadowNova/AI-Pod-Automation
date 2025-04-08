"""
Design Generation Pipeline for POD Automation System.
Integrates Trend Forecasting, Prompt Optimization, and Stable Diffusion
to generate cat-themed designs based on trending keywords.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from pathlib import Path
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("design_generation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import components
from pod_automation.agents.trend_forecaster import TrendForecaster
from pod_automation.agents.prompt_optimizer import PromptOptimizer
from pod_automation.agents.stable_diffusion import create_stable_diffusion_client

class DesignGenerationPipeline:
    """Pipeline for generating cat-themed designs based on trends."""
    
    def __init__(self, config=None):
        """Initialize design generation pipeline.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Set up output directories
        self.output_dir = self.config.get('output_dir', 'data/designs')
        self.trend_dir = self.config.get('trend_dir', 'data/trends')
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.trend_dir, exist_ok=True)
        
        # Initialize components
        self.trend_forecaster = TrendForecaster(config={'data_dir': self.trend_dir})
        self.prompt_optimizer = PromptOptimizer()
        
        # Initialize Stable Diffusion client
        use_api = self.config.get('use_stable_diffusion_api', True)
        api_key = self.config.get('stable_diffusion_api_key') or os.environ.get('OPENROUTER_API_KEY')
        api_url = self.config.get('stable_diffusion_api_url')
        model_path = self.config.get('stable_diffusion_model_path')
        
        self.stable_diffusion = create_stable_diffusion_client(
            use_api=use_api,
            api_key=api_key,
            api_url=api_url,
            model_path=model_path,
            config={'output_dir': self.output_dir}
        )
    
    def run_pipeline(self, keywords=None, num_designs=5, analyze_trends=True):
        """Run the complete design generation pipeline.
        
        Args:
            keywords (list, optional): List of keywords to use
            num_designs (int, optional): Number of designs to generate
            analyze_trends (bool, optional): Whether to run trend analysis
            
        Returns:
            list: List of generated design paths
        """
        logger.info("Starting design generation pipeline")
        
        # Step 1: Run trend analysis if requested
        if analyze_trends:
            logger.info("Running trend analysis")
            trend_report_path = self.trend_forecaster.run_trend_analysis(keywords)
            
            if trend_report_path:
                logger.info(f"Trend analysis completed. Report saved to: {trend_report_path}")
            else:
                logger.warning("Trend analysis failed. Using provided keywords.")
        else:
            trend_report_path = None
            logger.info("Skipping trend analysis")
        
        # Step 2: Generate optimized prompts
        logger.info("Generating optimized prompts")
        
        if trend_report_path:
            # Generate prompts from trend report
            optimized_prompts = self.prompt_optimizer.optimize_from_trend_report(trend_report_path)
        elif keywords:
            # Generate prompts from provided keywords
            optimized_prompts = self.prompt_optimizer.optimize_from_keywords(keywords, num_prompts=num_designs)
        else:
            # Use default cat-themed keywords
            default_keywords = ["cat t-shirt", "funny cat", "cute cat", "cat lover", "cat design"]
            optimized_prompts = self.prompt_optimizer.optimize_from_keywords(default_keywords, num_prompts=num_designs)
        
        logger.info(f"Generated {len(optimized_prompts)} optimized prompts")
        
        # Step 3: Generate designs using Stable Diffusion
        logger.info("Generating designs using Stable Diffusion")
        
        generated_designs = []
        for i, (prompt, negative_prompt) in enumerate(optimized_prompts, 1):
            logger.info(f"Generating design {i}/{len(optimized_prompts)}")
            
            # Generate image
            success, result = self.stable_diffusion.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=1024,
                height=1024,
                num_inference_steps=50,
                guidance_scale=7.5
            )
            
            if success:
                logger.info(f"Design {i} generated successfully: {result}")
                generated_designs.append(result)
            else:
                logger.error(f"Design {i} generation failed: {result}")
            
            # Add a small delay between generations to avoid rate limiting
            time.sleep(2)
        
        # Step 4: Save pipeline results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_path = os.path.join(self.output_dir, f"pipeline_results_{timestamp}.json")
        
        with open(results_path, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'trend_report': trend_report_path,
                'prompts': [prompt for prompt, _ in optimized_prompts],
                'negative_prompts': [negative for _, negative in optimized_prompts],
                'generated_designs': generated_designs,
                'success_rate': f"{len(generated_designs)}/{len(optimized_prompts)}"
            }, f, indent=2)
        
        logger.info(f"Pipeline results saved to: {results_path}")
        logger.info(f"Generated {len(generated_designs)} designs out of {len(optimized_prompts)} attempts")
        
        return generated_designs
    
    def generate_design_variations(self, base_prompt, num_variations=3):
        """Generate variations of a design.
        
        Args:
            base_prompt (str): Base prompt for the design
            num_variations (int, optional): Number of variations to generate
            
        Returns:
            list: List of generated design paths
        """
        logger.info(f"Generating {num_variations} variations of design with prompt: {base_prompt}")
        
        # Generate prompt variations
        prompt_variations = self.prompt_optimizer.generate_prompt_variations(
            base_prompt, 
            num_variations=num_variations
        )
        
        # Generate designs for each prompt variation
        generated_designs = []
        for i, (prompt, negative_prompt) in enumerate(prompt_variations, 1):
            logger.info(f"Generating variation {i}/{num_variations}")
            
            # Generate image
            success, result = self.stable_diffusion.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=1024,
                height=1024,
                num_inference_steps=50,
                guidance_scale=7.5
            )
            
            if success:
                logger.info(f"Variation {i} generated successfully: {result}")
                generated_designs.append(result)
            else:
                logger.error(f"Variation {i} generation failed: {result}")
            
            # Add a small delay between generations to avoid rate limiting
            time.sleep(2)
        
        return generated_designs
    
    def generate_themed_collection(self, theme, num_designs=5):
        """Generate a collection of designs around a specific theme.
        
        Args:
            theme (str): Theme for the collection
            num_designs (int, optional): Number of designs to generate
            
        Returns:
            list: List of generated design paths
        """
        logger.info(f"Generating themed collection: {theme} ({num_designs} designs)")
        
        # Create base prompts for the theme
        base_prompts = [
            f"cat {theme}",
            f"cute cat with {theme}",
            f"funny cat {theme}",
            f"{theme} cat illustration",
            f"cat lover {theme}",
            f"{theme} cat character",
            f"cat wearing {theme}",
            f"cat playing with {theme}",
            f"{theme} cat design"
        ]
        
        # Select random prompts from the base prompts
        selected_prompts = random.sample(base_prompts, min(num_designs, len(base_prompts)))
        
        # If we need more prompts, add variations of existing ones
        while len(selected_prompts) < num_designs:
            base = random.choice(base_prompts)
            selected_prompts.append(f"{base} {random.choice(['cartoon', 'illustration', 'design', 'art'])}")
        
        # Optimize prompts
        optimized_prompts = [
            self.prompt_optimizer.optimize_prompt(prompt)
            for prompt in selected_prompts
        ]
        
        # Generate designs
        generated_designs = []
        for i, (prompt, negative_prompt) in enumerate(optimized_prompts, 1):
            logger.info(f"Generating design {i}/{num_designs} for theme: {theme}")
            
            # Generate image
            success, result = self.stable_diffusion.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=1024,
                height=1024,
                num_inference_steps=50,
                guidance_scale=7.5
            )
            
            if success:
                logger.info(f"Design {i} generated successfully: {result}")
                generated_designs.append(result)
            else:
                logger.error(f"Design {i} generation failed: {result}")
            
            # Add a small delay between generations to avoid rate limiting
            time.sleep(2)
        
        # Save collection results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        results_path = os.path.join(self.output_dir, f"collection_{theme}_{timestamp}.json")
        
        with open(results_path, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'theme': theme,
                'prompts': [prompt for prompt, _ in optimized_prompts],
                'negative_prompts': [negative for _, negative in optimized_prompts],
                'generated_designs': generated_designs,
                'success_rate': f"{len(generated_designs)}/{num_designs}"
            }, f, indent=2)
        
        logger.info(f"Collection results saved to: {results_path}")
        
        return generated_designs

def main():
    """Main function to test design generation pipeline."""
    logger.info("Testing Design Generation Pipeline")
    
    # Check if API key is set
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if not api_key:
        logger.error("API key not set. Please set OPENROUTER_API_KEY environment variable.")
        return
    
    # Create design generation pipeline
    pipeline = DesignGenerationPipeline(config={
        'use_stable_diffusion_api': True,
        'stable_diffusion_api_key': api_key
    })
    
    # Run pipeline with default settings
    generated_designs = pipeline.run_pipeline(
        keywords=["cat t-shirt", "funny cat", "cute cat", "cat lover"],
        num_designs=2,
        analyze_trends=False  # Set to True to run trend analysis
    )
    
    if generated_designs:
        logger.info(f"Pipeline test completed successfully. Generated {len(generated_designs)} designs.")
    else:
        logger.error("Pipeline test failed. No designs were generated.")

if __name__ == "__main__":
    main()
