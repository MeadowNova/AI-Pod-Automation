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
import re

# Set up logging
from pod_automation.config.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Import components
from agents.trend_forecaster import TrendForecaster
from agents.prompt_optimizer import PromptOptimizer
from agents.stable_diffusion import create_stable_diffusion_client

def build_design_filename(theme, concept, variant, version, date=None, ext="png"):
    """
    Build a filename according to the naming convention:
    [Theme]-[Concept]-[Variant]-[Version]-[Date].ext
    """
    if not date:
        date = datetime.now().strftime("%Y%m%d")
    # Sanitize fields for filesystem
    def clean(s):
        return re.sub(r'[^A-Za-z0-9]', '', s)
    theme = clean(theme)
    concept = clean(concept)
    variant = clean(variant)
    version = f"v{int(version)}" if not str(version).startswith("v") else str(version)
    return f"{theme}-{concept}-{variant}-{version}-{date}.{ext}"

class DesignGenerationPipeline:
    """Pipeline for generating cat-themed designs based on trends."""
    
    def __init__(self, config=None):
        """Initialize design generation pipeline.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Set up output directories
        self.output_dir = self.config.get('output_dir', 'data/designs/drafts')
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
            
            # Example: Extract theme/concept/variant/version from prompt or config
            # For demonstration, use placeholders or parse from prompt if possible
            theme = self.config.get("theme", "CatTheme")
            concept = self.config.get("concept", "Concept")
            variant = self.config.get("variant", "White")  # Could be "Dark" or "White"
            version = i
            # Use Mistral MCP to generate the filename from the prompt
            from mistral_mcp_client import get_filename_from_prompt
            filename = get_filename_from_prompt(prompt)
            output_path = os.path.join(self.output_dir, filename)

            # Generate image (no output_path param)
            success, result = self.stable_diffusion.generate_image(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=1024,
                height=1024,
                num_inference_steps=50,
                guidance_scale=7.5
            )

            if success:
                # result is the path to the generated file
                try:
                    os.rename(result, output_path)
                    logger.info(f"Design {i} generated and renamed to: {output_path}")
                    generated_designs.append(output_path)
                except Exception as e:
                    logger.error(f"Failed to rename generated file: {result} to {output_path}: {e}")
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

    # ... (rest of the class unchanged) ...

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
        'stable_diffusion_api_key': api_key,
        # Optionally set theme/concept/variant here for testing
        'theme': 'CatMeme',
        'concept': 'BusinessCat',
        'variant': 'White'
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
