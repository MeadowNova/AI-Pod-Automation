"""
Prompt Optimizer for POD Automation System.
Enhances prompts for Stable Diffusion to generate high-quality cat-themed designs.
"""

import os
import sys
import logging
import json
import random
from pathlib import Path

# Set up logging
from pod_automation.config.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

class PromptOptimizer:
    """Optimizer for enhancing Stable Diffusion prompts."""
    
    def __init__(self, config=None):
        """Initialize prompt optimizer.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Load prompt enhancement components
        self.styles = self._load_component('styles')
        self.artists = self._load_component('artists')
        self.modifiers = self._load_component('modifiers')
        self.colors = self._load_component('colors')
        self.techniques = self._load_component('techniques')
        self.cat_breeds = self._load_component('cat_breeds')
        self.cat_poses = self._load_component('cat_poses')
        self.cat_expressions = self._load_component('cat_expressions')
        self.cat_accessories = self._load_component('cat_accessories')
        
        # Load negative prompt components
        self.negative_modifiers = self._load_component('negative_modifiers')
    
    def _load_component(self, component_name):
        """Load prompt component from file or use default.
        
        Args:
            component_name (str): Name of the component to load
            
        Returns:
            list: List of component values
        """
        # Check if component file exists
        component_file = Path(__file__).parent / f"prompt_components/{component_name}.json"
        
        if component_file.exists():
            try:
                with open(component_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading {component_name} from file: {str(e)}")
        
        # Use default components if file doesn't exist or loading fails
        return self._get_default_component(component_name)
    
    def _get_default_component(self, component_name):
        """Get default values for prompt component.
        
        Args:
            component_name (str): Name of the component
            
        Returns:
            list: List of default component values
        """
        defaults = {
            'styles': [
                "digital art", "illustration", "cartoon", "watercolor", "vector art",
                "minimalist", "pop art", "flat design", "pixel art", "comic book style",
                "3D render", "concept art", "anime style", "manga style", "chibi style",
                "realistic", "photorealistic", "surrealism", "abstract", "geometric"
            ],
            'artists': [
                "Disney style", "Pixar style", "Studio Ghibli style", "Hayao Miyazaki style",
                "Lisa Frank style", "Takashi Murakami style", "Banksy style", "Keith Haring style",
                "Tim Burton style", "Dr. Seuss style", "Beatrix Potter style", "Yoshitomo Nara style"
            ],
            'modifiers': [
                "vibrant", "colorful", "cute", "adorable", "funny", "whimsical",
                "playful", "charming", "elegant", "stylized", "detailed", "simple",
                "bold", "pastel", "high contrast", "soft", "sharp", "clean lines"
            ],
            'colors': [
                "vibrant colors", "pastel colors", "monochromatic", "black and white",
                "rainbow colors", "neon colors", "muted colors", "primary colors",
                "complementary colors", "warm colors", "cool colors", "earth tones"
            ],
            'techniques': [
                "high detail", "smooth gradients", "sharp lines", "soft edges",
                "high contrast", "low contrast", "dynamic lighting", "ambient lighting",
                "dramatic shadows", "no shadows", "textured", "flat color"
            ],
            'cat_breeds': [
                "tabby cat", "calico cat", "siamese cat", "persian cat", "maine coon",
                "bengal cat", "sphynx cat", "ragdoll cat", "scottish fold", "british shorthair",
                "black cat", "white cat", "orange cat", "gray cat", "tuxedo cat"
            ],
            'cat_poses': [
                "sitting", "standing", "lying down", "stretching", "pouncing",
                "playing", "sleeping", "grooming", "jumping", "running",
                "curled up", "loafing", "stalking", "climbing", "hiding"
            ],
            'cat_expressions': [
                "happy", "curious", "sleepy", "alert", "relaxed",
                "playful", "surprised", "content", "mischievous", "grumpy",
                "excited", "focused", "yawning", "smiling", "wide-eyed"
            ],
            'cat_accessories': [
                "wearing a t-shirt", "wearing a hat", "wearing glasses", "wearing a bow tie",
                "wearing a scarf", "wearing a bandana", "wearing a collar", "wearing a crown",
                "wearing a sweater", "wearing a costume", "with a toy", "with a ball of yarn",
                "with a mouse toy", "with a fish", "with a bird"
            ],
            'negative_modifiers': [
                "deformed", "blurry", "bad anatomy", "disfigured", "poorly drawn face",
                "mutation", "mutated", "extra limb", "ugly", "poorly drawn hands",
                "missing limb", "floating limbs", "disconnected limbs", "malformed limbs",
                "out of frame", "cut off", "low contrast", "underexposed", "overexposed",
                "bad art", "beginner", "amateur", "distorted face", "low quality", "low resolution"
            ]
        }
        
        return defaults.get(component_name, [])
    
    def save_components(self):
        """Save all prompt components to files."""
        # Create components directory if it doesn't exist
        components_dir = Path(__file__).parent / "prompt_components"
        os.makedirs(components_dir, exist_ok=True)
        
        # Save each component
        components = {
            'styles': self.styles,
            'artists': self.artists,
            'modifiers': self.modifiers,
            'colors': self.colors,
            'techniques': self.techniques,
            'cat_breeds': self.cat_breeds,
            'cat_poses': self.cat_poses,
            'cat_expressions': self.cat_expressions,
            'cat_accessories': self.cat_accessories,
            'negative_modifiers': self.negative_modifiers
        }
        
        for name, component in components.items():
            try:
                with open(components_dir / f"{name}.json", 'w') as f:
                    json.dump(component, f, indent=2)
                logger.info(f"Saved {name} component to file")
            except Exception as e:
                logger.error(f"Error saving {name} component to file: {str(e)}")
    
    def add_component_item(self, component_name, item):
        """Add an item to a prompt component.
        
        Args:
            component_name (str): Name of the component
            item (str): Item to add
            
        Returns:
            bool: True if item was added, False otherwise
        """
        if hasattr(self, component_name):
            component = getattr(self, component_name)
            if item not in component:
                component.append(item)
                logger.info(f"Added '{item}' to {component_name}")
                return True
            else:
                logger.info(f"'{item}' already exists in {component_name}")
                return False
        else:
            logger.error(f"Component {component_name} does not exist")
            return False
    
    def remove_component_item(self, component_name, item):
        """Remove an item from a prompt component.
        
        Args:
            component_name (str): Name of the component
            item (str): Item to remove
            
        Returns:
            bool: True if item was removed, False otherwise
        """
        if hasattr(self, component_name):
            component = getattr(self, component_name)
            if item in component:
                component.remove(item)
                logger.info(f"Removed '{item}' from {component_name}")
                return True
            else:
                logger.info(f"'{item}' does not exist in {component_name}")
                return False
        else:
            logger.error(f"Component {component_name} does not exist")
            return False
    
    def optimize_prompt(self, base_prompt, style_weight=1.0, artist_weight=0.5, modifier_weight=0.8, 
                        color_weight=0.7, technique_weight=0.6, cat_detail_weight=0.9):
        """Optimize a prompt for Stable Diffusion.
        
        Args:
            base_prompt (str): Base prompt to optimize
            style_weight (float, optional): Weight for style components
            artist_weight (float, optional): Weight for artist components
            modifier_weight (float, optional): Weight for modifier components
            color_weight (float, optional): Weight for color components
            technique_weight (float, optional): Weight for technique components
            cat_detail_weight (float, optional): Weight for cat detail components
            
        Returns:
            tuple: (optimized_prompt, negative_prompt)
        """
        logger.info(f"Optimizing prompt: {base_prompt}")
        
        # Determine if prompt already contains cat breed, pose, expression, or accessories
        has_cat_breed = any(breed.lower() in base_prompt.lower() for breed in self.cat_breeds)
        has_cat_pose = any(pose.lower() in base_prompt.lower() for pose in self.cat_poses)
        has_cat_expression = any(expr.lower() in base_prompt.lower() for expr in self.cat_expressions)
        has_cat_accessory = any(acc.lower() in base_prompt.lower() for acc in self.cat_accessories)
        
        # Add components based on weights and randomness
        components = []
        
        # Add style if probability check passes
        if random.random() < style_weight:
            components.append(random.choice(self.styles))
        
        # Add artist if probability check passes
        if random.random() < artist_weight:
            components.append(random.choice(self.artists))
        
        # Add modifiers (1-2 based on weight)
        if random.random() < modifier_weight:
            num_modifiers = 1 + int(random.random() < 0.5)
            selected_modifiers = random.sample(self.modifiers, min(num_modifiers, len(self.modifiers)))
            components.extend(selected_modifiers)
        
        # Add color if probability check passes
        if random.random() < color_weight:
            components.append(random.choice(self.colors))
        
        # Add technique if probability check passes
        if random.random() < technique_weight:
            components.append(random.choice(self.techniques))
        
        # Add cat details if not already in prompt and probability check passes
        if random.random() < cat_detail_weight:
            if not has_cat_breed:
                components.append(random.choice(self.cat_breeds))
            
            if not has_cat_pose:
                components.append(random.choice(self.cat_poses))
            
            if not has_cat_expression:
                components.append(random.choice(self.cat_expressions))
            
            if not has_cat_accessory and random.random() < 0.7:  # 70% chance to add accessory
                components.append(random.choice(self.cat_accessories))
        
        # Combine base prompt with components
        optimized_prompt = base_prompt
        if components:
            optimized_prompt += ", " + ", ".join(components)
        
        # Generate negative prompt
        num_negative = random.randint(5, 10)
        negative_prompt = ", ".join(random.sample(self.negative_modifiers, min(num_negative, len(self.negative_modifiers))))
        
        logger.info(f"Optimized prompt: {optimized_prompt}")
        logger.info(f"Negative prompt: {negative_prompt}")
        
        return optimized_prompt, negative_prompt
    
    def generate_prompt_variations(self, base_prompt, num_variations=3, **kwargs):
        """Generate variations of a base prompt.
        
        Args:
            base_prompt (str): Base prompt to generate variations for
            num_variations (int, optional): Number of variations to generate
            **kwargs: Additional arguments to pass to optimize_prompt
            
        Returns:
            list: List of (optimized_prompt, negative_prompt) tuples
        """
        logger.info(f"Generating {num_variations} variations of prompt: {base_prompt}")
        
        variations = []
        for i in range(num_variations):
            variation = self.optimize_prompt(base_prompt, **kwargs)
            variations.append(variation)
        
        return variations
    
    def optimize_from_keywords(self, keywords, num_prompts=3):
        """Generate optimized prompts from keywords.
        
        Args:
            keywords (list): List of keywords to use
            num_prompts (int, optional): Number of prompts to generate
            
        Returns:
            list: List of (optimized_prompt, negative_prompt) tuples
        """
        logger.info(f"Generating {num_prompts} optimized prompts from keywords: {keywords}")
        
        prompts = []
        for i in range(num_prompts):
            # Select 1-3 random keywords
            num_keywords = random.randint(1, min(3, len(keywords)))
            selected_keywords = random.sample(keywords, num_keywords)
            
            # Create base prompt
            base_prompt = "cat " + " ".join(selected_keywords)
            
            # Optimize prompt
            optimized_prompt, negative_prompt = self.optimize_prompt(base_prompt)
            prompts.append((optimized_prompt, negative_prompt))
        
        return prompts
    
    def optimize_from_trend_report(self, trend_report_path):
        """Generate optimized prompts from a trend report.
        
        Args:
            trend_report_path (str): Path to trend report file
            
        Returns:
            list: List of (optimized_prompt, negative_prompt) tuples
        """
        logger.info(f"Generating optimized prompts from trend report: {trend_report_path}")
        
        try:
            # Read trend report
            with open(trend_report_path, 'r') as f:
                report_content = f.read()
            
            # Extract keywords from report
            keywords = []
            
            # Look for top keywords section
            top_keywords_section = report_content.split("## Top Trending Keywords")[1].split("##")[0]
            for line in top_keywords_section.split("\n"):
                if line.strip().startswith("*") or line.strip().startswith("-") or (". **" in line and "**" in line):
                    # Extract keyword from bullet point or numbered list
                    keyword_match = line.split("**")[1].split("**")[0]
                    keywords.append(keyword_match)
            
            # If no keywords found, use some default cat-themed keywords
            if not keywords:
                keywords = ["cat t-shirt", "funny cat", "cute cat", "cat lover", "cat design"]
            
            # Generate prompts from keywords
            return self.optimize_from_keywords(keywords, num_prompts=5)
        
        except Exception as e:
            logger.error(f"Error generating prompts from trend report: {str(e)}")
            
            # Fallback to some default cat-themed keywords
            default_keywords = ["cat t-shirt", "funny cat", "cute cat", "cat lover", "cat design"]
            return self.optimize_from_keywords(default_keywords, num_prompts=3)
