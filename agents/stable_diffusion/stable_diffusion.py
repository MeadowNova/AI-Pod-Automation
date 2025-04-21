"""
Stable Diffusion integration for POD Automation System.
Handles connection to Stable Diffusion API for design generation.
"""

import os
import sys
import logging
import json
import time
import requests
import base64
from io import BytesIO
from PIL import Image
from pathlib import Path
import random

# Set up logging
from pod_automation.config.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

class StableDiffusionAPI:
    """Client for interacting with Stable Diffusion API."""
    
    def __init__(self, api_key=None, api_url=None, config=None):
        """Initialize Stable Diffusion API client.
        
        Args:
            api_key (str, optional): API key for Stable Diffusion service
            api_url (str, optional): URL for Stable Diffusion API
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Get API key and URL from config if not provided
        self.api_key = api_key or self.config.get('api_key') or os.environ.get('OPENROUTER_API_KEY')
        self.api_url = api_url or self.config.get('api_url') or "http://192.168.1.13:7860/sdapi/v1/txt2img"
        
        # Set up output directory
        self.output_dir = self.config.get('output_dir', 'data/designs')
        os.makedirs(self.output_dir, exist_ok=True)
        
        if not self.api_url.startswith("http://127.0.0.1"):
            if not self.api_key:
                logger.warning("No API key provided for Stable Diffusion. Please set OPENROUTER_API_KEY environment variable or provide in config.")
    
    def generate_image(self, prompt, negative_prompt=None, width=1024, height=1024, num_inference_steps=50, guidance_scale=7.5, seed=None, model="stability-ai/sdxl"):
        """Generate an image using Stable Diffusion.
        
        Args:
            prompt (str): Text prompt for image generation
            negative_prompt (str, optional): Negative prompt to guide what not to generate
            width (int, optional): Image width
            height (int, optional): Image height
            num_inference_steps (int, optional): Number of denoising steps
            guidance_scale (float, optional): Scale for classifier-free guidance
            seed (int, optional): Random seed for reproducibility
            model (str, optional): Model to use for generation
            
        Returns:
            tuple: (success, image_path or error_message)
        """
        if not (self.api_url.startswith("http://127.0.0.1") or self.api_url.startswith("http://192.168.1.13")):
            if not self.api_key:
                return False, "API key not set. Please set OPENROUTER_API_KEY environment variable or provide in config."
        
        logger.info(f"Generating image with prompt: {prompt}")
        
        try:
            # Set random seed if not provided
            if seed is None:
                seed = random.randint(0, 2147483647)
            
            # Prepare request payload for Automatic1111 API
            payload = {
                "prompt": prompt,
                "negative_prompt": negative_prompt or "",
                "width": width,
                "height": height,
                "steps": num_inference_steps,
                "cfg_scale": guidance_scale,
                "seed": seed,
                "sampler_name": "Euler a",
                "batch_size": 1,
                "n_iter": 1
            }
            
            # Prepare headers
            headers = {
                "Content-Type": "application/json"
            }
            
            # Make API request
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            
            # Check for successful response
            if response.status_code == 200:
                response_data = response.json()
                
                # Extract image data
                if 'images' in response_data and response_data['images']:
                    image_data = response_data['images'][0]
                    
                    # Decode base64 image
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(BytesIO(image_bytes))
                    
                    # Save image
                    timestamp = int(time.time())
                    safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30])
                    image_path = os.path.join(self.output_dir, f"{safe_prompt}_{timestamp}_{seed}.png")
                    image.save(image_path)
                    
                    logger.info(f"Image generated successfully and saved to {image_path}")
                    
                    # Save metadata
                    metadata_path = os.path.join(self.output_dir, f"{safe_prompt}_{timestamp}_{seed}_metadata.json")
                    with open(metadata_path, 'w') as f:
                        json.dump({
                            'prompt': prompt,
                            'negative_prompt': negative_prompt,
                            'width': width,
                            'height': height,
                            'num_inference_steps': num_inference_steps,
                            'guidance_scale': guidance_scale,
                            'seed': seed,
                            'model': model,
                            'timestamp': timestamp
                        }, f, indent=2)
                    
                    return True, image_path
                else:
                    error_msg = "No image data in response"
                    logger.error(error_msg)
                    return False, error_msg
            else:
                error_msg = f"API request failed with status code {response.status_code}: {response.text}"
                logger.error(error_msg)
                return False, error_msg
        
        except Exception as e:
            error_msg = f"Error generating image: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def batch_generate_images(self, prompts, **kwargs):
        """Generate multiple images using a list of prompts.
        
        Args:
            prompts (list): List of text prompts for image generation
            **kwargs: Additional arguments to pass to generate_image
            
        Returns:
            list: List of (success, image_path or error_message) tuples
        """
        logger.info(f"Batch generating {len(prompts)} images")
        
        results = []
        for prompt in prompts:
            # Add a small delay between requests to avoid rate limiting
            time.sleep(1)
            
            result = self.generate_image(prompt, **kwargs)
            results.append(result)
        
        # Count successes and failures
        successes = sum(1 for success, _ in results if success)
        logger.info(f"Batch generation completed. {successes}/{len(prompts)} images generated successfully.")
        
        return results
    
    def generate_variations(self, base_prompt, variations=3, **kwargs):
        """Generate variations of a base prompt.
        
        Args:
            base_prompt (str): Base text prompt for image generation
            variations (int, optional): Number of variations to generate
            **kwargs: Additional arguments to pass to generate_image
            
        Returns:
            list: List of (success, image_path or error_message) tuples
        """
        logger.info(f"Generating {variations} variations of prompt: {base_prompt}")
        
        results = []
        for i in range(variations):
            # Use different seeds for each variation
            seed = random.randint(0, 2147483647)
            
            # Add variation number to prompt
            prompt = f"{base_prompt} (variation {i+1})"
            
            # Generate image
            result = self.generate_image(prompt, seed=seed, **kwargs)
            results.append(result)
            
            # Add a small delay between requests to avoid rate limiting
            time.sleep(1)
        
        # Count successes and failures
        successes = sum(1 for success, _ in results if success)
        logger.info(f"Variation generation completed. {successes}/{variations} images generated successfully.")
        
        return results

class StableDiffusionLocal:
    """Client for interacting with a local Stable Diffusion installation."""
    
    def __init__(self, model_path=None, config=None):
        """Initialize local Stable Diffusion client.
        
        Args:
            model_path (str, optional): Path to Stable Diffusion model
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Get model path from config if not provided
        self.model_path = model_path or self.config.get('model_path')
        
        # Set up output directory
        self.output_dir = self.config.get('output_dir', 'data/designs')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize model
        self.model = None
        self.pipe = None
        
        logger.info("Note: Local Stable Diffusion requires additional setup. Please install diffusers and transformers packages.")
    
    def load_model(self):
        """Load Stable Diffusion model.
        
        Returns:
            bool: True if model loaded successfully, False otherwise
        """
        try:
            # Import required packages
            from diffusers import StableDiffusionPipeline
            import torch
            
            # Load model
            logger.info(f"Loading Stable Diffusion model from {self.model_path}")
            
            self.pipe = StableDiffusionPipeline.from_pretrained(
                self.model_path,
                torch_dtype=torch.float16
            )
            
            # Move model to GPU if available
            if torch.cuda.is_available():
                self.pipe = self.pipe.to("cuda")
                logger.info("Model loaded on GPU")
            else:
                logger.warning("GPU not available. Model will run on CPU, which is much slower.")
            
            logger.info("Stable Diffusion model loaded successfully")
            return True
        
        except ImportError:
            logger.error("Required packages not installed. Please install diffusers and transformers packages.")
            return False
        
        except Exception as e:
            logger.error(f"Error loading Stable Diffusion model: {str(e)}")
            return False
    
    def generate_image(self, prompt, negative_prompt=None, width=512, height=512, num_inference_steps=50, guidance_scale=7.5, seed=None):
        """Generate an image using local Stable Diffusion.
        
        Args:
            prompt (str): Text prompt for image generation
            negative_prompt (str, optional): Negative prompt to guide what not to generate
            width (int, optional): Image width
            height (int, optional): Image height
            num_inference_steps (int, optional): Number of denoising steps
            guidance_scale (float, optional): Scale for classifier-free guidance
            seed (int, optional): Random seed for reproducibility
            
        Returns:
            tuple: (success, image_path or error_message)
        """
        if self.pipe is None:
            success = self.load_model()
            if not success:
                return False, "Failed to load Stable Diffusion model"
        
        logger.info(f"Generating image with prompt: {prompt}")
        
        try:
            import torch
            
            # Set random seed if provided
            if seed is not None:
                torch.manual_seed(seed)
                generator = torch.Generator().manual_seed(seed)
            else:
                generator = None
                seed = random.randint(0, 2147483647)
            
            # Generate image
            image = self.pipe(
                prompt=prompt,
                negative_prompt=negative_prompt,
                width=width,
                height=height,
                num_inference_steps=num_inference_steps,
                guidance_scale=guidance_scale,
                generator=generator
            ).images[0]
            
            # Save image
            timestamp = int(time.time())
            safe_prompt = "".join(c if c.isalnum() else "_" for c in prompt[:30])
            image_path = os.path.join(self.output_dir, f"{safe_prompt}_{timestamp}_{seed}.png")
            image.save(image_path)
            
            logger.info(f"Image generated successfully and saved to {image_path}")
            
            # Save metadata
            metadata_path = os.path.join(self.output_dir, f"{safe_prompt}_{timestamp}_{seed}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump({
                    'prompt': prompt,
                    'negative_prompt': negative_prompt,
                    'width': width,
                    'height': height,
                    'num_inference_steps': num_inference_steps,
                    'guidance_scale': guidance_scale,
                    'seed': seed,
                    'timestamp': timestamp
                }, f, indent=2)
            
            return True, image_path
        
        except Exception as e:
            error_msg = f"Error generating image: {str(e)}"
            logger.error(error_msg)
            return False, error_msg
    
    def batch_generate_images(self, prompts, **kwargs):
        """Generate multiple images using a list of prompts.
        
        Args:
            prompts (list): List of text prompts for image generation
            **kwargs: Additional arguments to pass to generate_image
            
        Returns:
            list: List of (success, image_path or error_message) tuples
        """
        logger.info(f"Batch generating {len(prompts)} images")
        
        results = []
        for prompt in prompts:
            result = self.generate_image(prompt, **kwargs)
            results.append(result)
        
        # Count successes and failures
        successes = sum(1 for success, _ in results if success)
        logger.info(f"Batch generation completed. {successes}/{len(prompts)} images generated successfully.")
        
        return results
    
    def generate_variations(self, base_prompt, variations=3, **kwargs):
        """Generate variations of a base prompt.
        
        Args:
            base_prompt (str): Base text prompt for image generation
            variations (int, optional): Number of variations to generate
            **kwargs: Additional arguments to pass to generate_image
            
        Returns:
            list: List of (success, image_path or error_message) tuples
        """
        logger.info(f"Generating {variations} variations of prompt: {base_prompt}")
        
        results = []
        for i in range(variations):
            # Use different seeds for each variation
            seed = random.randint(0, 2147483647)
            
            # Add variation number to prompt
            prompt = f"{base_prompt} (variation {i+1})"
            
            # Generate image
            result = self.generate_image(prompt, seed=seed, **kwargs)
            results.append(result)
        
        # Count successes and failures
        successes = sum(1 for success, _ in results if success)
        logger.info(f"Variation generation completed. {successes}/{variations} images generated successfully.")
        
        return results

def create_stable_diffusion_client(use_api=True, api_key=None, api_url=None, model_path=None, config=None):
    """Create a Stable Diffusion client.
    
    Args:
        use_api (bool, optional): Whether to use the API or local installation
        api_key (str, optional): API key for Stable Diffusion service
        api_url (str, optional): URL for Stable Diffusion API
        model_path (str, optional): Path to local Stable Diffusion model
        config (dict, optional): Configuration dictionary
        
    Returns:
        object: Stable Diffusion client
    """
    if use_api:
        return StableDiffusionAPI(api_key=api_key, api_url=api_url, config=config)
    else:
        return StableDiffusionLocal(model_path=model_path, config=config)

def main():
    """Main function to test Stable Diffusion integration."""
    logger.info("Testing Stable Diffusion integration")
    
    # Create Stable Diffusion client pointing to local Automatic1111
    sd_client = create_stable_diffusion_client(
        use_api=True,
        api_url="http://192.168.1.13:7860/sdapi/v1/txt2img"
    )
    
    # Test image generation
    prompt = "A modern t-shirt design with a colorful abstract pattern"
    success, result = sd_client.generate_image(prompt)
    
    if success:
        logger.info(f"Image generated successfully: {result}")
    else:
        logger.error(f"Image generation failed: {result}")

if __name__ == "__main__":
    main()
