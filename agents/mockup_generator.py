"""
Enhanced mockup generator with additional templates as recommended in the audit.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple, Union
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("mockup_generator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MockupGenerator:
    """Mockup Generation System for creating product mockups with designs."""
    
    def __init__(self, config=None):
        """Initialize the mockup generator.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        self.designs_dir = self.config.get('designs_dir', 'data/designs')
        self.output_dir = self.config.get('output_dir', 'data/mockups')
        self.templates_dir = self.config.get('templates_dir', 'data/templates')
        
        # Create directories if they don't exist
        os.makedirs(self.designs_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
        
        # Define print providers and their products
        self.print_providers = {
            'monster_digital': {
                't-shirt': {
                    'template': 'monster_digital_tshirt.png',
                    'design_area': (300, 200, 700, 600),  # x1, y1, x2, y2
                    'colors': ['white', 'black', 'navy', 'gray', 'red'],
                    'variations': ['crew-neck', 'v-neck', 'long-sleeve']
                },
                'sweatshirt': {
                    'template': 'monster_digital_sweatshirt.png',
                    'design_area': (300, 200, 700, 600),
                    'colors': ['white', 'black', 'navy', 'gray'],
                    'variations': ['hoodie', 'crewneck', 'zip-up']
                },
                'tank-top': {
                    'template': 'monster_digital_tanktop.png',
                    'design_area': (300, 200, 700, 550),
                    'colors': ['white', 'black', 'navy', 'gray'],
                    'variations': ['standard', 'racerback']
                }
            },
            'sensaria': {
                'poster': {
                    'template': 'sensaria_poster.png',
                    'design_area': (100, 100, 900, 1300),
                    'colors': ['white'],
                    'variations': ['standard', 'framed', 'canvas']
                },
                'art-print': {
                    'template': 'sensaria_artprint.png',
                    'design_area': (100, 100, 900, 1300),
                    'colors': ['white', 'cream', 'black'],
                    'variations': ['standard', 'premium', 'matte']
                },
                'wall-art': {
                    'template': 'sensaria_wallart.png',
                    'design_area': (100, 100, 900, 900),
                    'colors': ['white'],
                    'variations': ['canvas', 'metal', 'wood']
                }
            },
            'mww': {
                'pillow_case': {
                    'template': 'mww_pillowcase.png',
                    'design_area': (200, 200, 800, 800),
                    'colors': ['white', 'cream', 'gray'],
                    'variations': ['standard', 'throw', 'floor']
                },
                'tote-bag': {
                    'template': 'mww_totebag.png',
                    'design_area': (300, 300, 700, 700),
                    'colors': ['white', 'black', 'natural'],
                    'variations': ['standard', 'large', 'beach']
                },
                'mug': {
                    'template': 'mww_mug.png',
                    'design_area': (300, 200, 700, 400),
                    'colors': ['white', 'black'],
                    'variations': ['standard', 'travel', 'large']
                }
            }
        }
        
        # Create default templates if they don't exist
        self._create_default_templates()
    
    def _create_default_templates(self):
        """Create default mockup templates if they don't exist."""
        for provider, products in self.print_providers.items():
            for product, details in products.items():
                template_path = os.path.join(self.templates_dir, details['template'])
                if not os.path.exists(template_path):
                    logger.info(f"Creating default template for {provider} {product}")
                    self._create_template(template_path, product, provider)
    
    def _create_template(self, template_path, product_type, provider):
        """Create a basic mockup template.
        
        Args:
            template_path (str): Path to save the template
            product_type (str): Type of product
            provider (str): Print provider
        """
        # Create a basic template based on product type
        width, height = 1000, 1500
        
        if product_type in ['t-shirt', 'sweatshirt', 'tank-top']:
            # Create a t-shirt like template
            img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a basic t-shirt shape
            if product_type == 't-shirt':
                # Crew neck t-shirt
                draw.rectangle([(250, 200), (750, 800)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(250, 200), (750, 300)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(250, 300), (350, 600)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(650, 300), (750, 600)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            elif product_type == 'sweatshirt':
                # Sweatshirt
                draw.rectangle([(250, 200), (750, 900)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(250, 200), (750, 300)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(250, 300), (350, 700)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(650, 300), (750, 700)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            elif product_type == 'tank-top':
                # Tank top
                draw.rectangle([(300, 200), (700, 800)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(300, 200), (700, 250)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(300, 250), (350, 400)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(650, 250), (700, 400)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            
            # Add provider name
            font = self._get_default_font(20)
            if font:
                draw.text((500, 1400), f"{provider}", fill=(0, 0, 0, 255), font=font, anchor="mm")
        
        elif product_type in ['poster', 'art-print', 'wall-art']:
            # Create a poster like template
            img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            # Draw a basic poster shape
            draw.rectangle([(100, 100), (900, 1300)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            
            # Add provider name
            font = self._get_default_font(20)
            if font:
                draw.text((500, 1400), f"{provider}", fill=(0, 0, 0, 255), font=font, anchor="mm")
        
        elif product_type in ['pillow_case', 'tote-bag', 'mug']:
            # Create templates for other products
            img = Image.new('RGBA', (width, height), (255, 255, 255, 0))
            draw = ImageDraw.Draw(img)
            
            if product_type == 'pillow_case':
                # Pillow case
                draw.rectangle([(200, 200), (800, 800)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            elif product_type == 'tote-bag':
                # Tote bag
                draw.rectangle([(300, 300), (700, 900)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(300, 900), (400, 1100)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(600, 900), (700, 1100)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            elif product_type == 'mug':
                # Mug
                draw.rectangle([(300, 300), (700, 600)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
                draw.rectangle([(700, 350), (750, 550)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            
            # Add provider name
            font = self._get_default_font(20)
            if font:
                draw.text((500, 1400), f"{provider}", fill=(0, 0, 0, 255), font=font, anchor="mm")
        
        # Save the template
        os.makedirs(os.path.dirname(template_path), exist_ok=True)
        img.save(template_path)
    
    def _get_default_font(self, size):
        """Get a default font for drawing text.
        
        Args:
            size (int): Font size
            
        Returns:
            ImageFont: Font object or None if not available
        """
        try:
            # Try to use a system font
            return ImageFont.truetype("Arial", size)
        except IOError:
            try:
                # Try to use the default font
                return ImageFont.load_default()
            except:
                # If all else fails, return None
                return None
    
    def create_mockup(self, design_path, product_type, color='white', variation='standard'):
        """Create a mockup for a design.
        
        Args:
            design_path (str): Path to the design image
            product_type (str): Type of product
            color (str, optional): Product color
            variation (str, optional): Product variation
            
        Returns:
            str: Path to the created mockup
        """
        logger.info(f"Creating mockup for {design_path} on {product_type} ({color}, {variation})")
        
        try:
            # Find the appropriate print provider and template
            provider_name = None
            product_details = None
            
            for provider, products in self.print_providers.items():
                if product_type in products:
                    provider_name = provider
                    product_details = products[product_type]
                    break
            
            if not provider_name or not product_details:
                logger.warning(f"No provider found for {product_type}, using default")
                # Use a default if no specific provider is found
                provider_name = list(self.print_providers.keys())[0]
                product_details = list(self.print_providers[provider_name].values())[0]
            
            # Check if color is valid
            if color not in product_details['colors']:
                logger.warning(f"Color {color} not available for {product_type}, using default")
                color = product_details['colors'][0]
            
            # Check if variation is valid
            if variation not in product_details['variations']:
                logger.warning(f"Variation {variation} not available for {product_type}, using default")
                variation = product_details['variations'][0]
            
            # Load the template
            template_path = os.path.join(self.templates_dir, product_details['template'])
            if not os.path.exists(template_path):
                logger.warning(f"Template {template_path} not found, creating default")
                self._create_template(template_path, product_type, provider_name)
            
            template = Image.open(template_path).convert("RGBA")
            
            # Load the design
            design = Image.open(design_path).convert("RGBA")
            
            # Resize design to fit the design area
            design_area = product_details['design_area']
            design_width = design_area[2] - design_area[0]
            design_height = design_area[3] - design_area[1]
            
            # Maintain aspect ratio
            design_aspect = design.width / design.height
            area_aspect = design_width / design_height
            
            if design_aspect > area_aspect:
                # Design is wider than area
                new_width = design_width
                new_height = int(new_width / design_aspect)
            else:
                # Design is taller than area
                new_height = design_height
                new_width = int(new_height * design_aspect)
            
            design = design.resize((new_width, new_height), Image.LANCZOS)
            
            # Create a new image for the mockup
            mockup = template.copy()
            
            # Apply color to the template (for white products, no change needed)
            if color != 'white':
                # Create a colored overlay
                colored_overlay = Image.new('RGBA', mockup.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(colored_overlay)
                
                # Define color RGB values
                color_map = {
                    'black': (0, 0, 0),
                    'navy': (0, 0, 128),
                    'gray': (128, 128, 128),
                    'red': (255, 0, 0),
                    'cream': (255, 253, 208),
                    'natural': (255, 240, 220)
                }
                
                rgb_color = color_map.get(color, (255, 255, 255))
                
                # Draw colored rectangle for the product area
                if product_type in ['t-shirt', 'sweatshirt', 'tank-top']:
                    # For apparel, color the main body
                    draw.rectangle([(250, 200), (750, 800)], fill=rgb_color + (255,))
                elif product_type in ['poster', 'art-print', 'wall-art']:
                    # For posters, color the background
                    draw.rectangle([(100, 100), (900, 1300)], fill=rgb_color + (255,))
                elif product_type == 'pillow_case':
                    # For pillow case
                    draw.rectangle([(200, 200), (800, 800)], fill=rgb_color + (255,))
                elif product_type == 'tote-bag':
                    # For tote bag
                    draw.rectangle([(300, 300), (700, 900)], fill=rgb_color + (255,))
                elif product_type == 'mug':
                    # For mug
                    draw.rectangle([(300, 300), (700, 600)], fill=rgb_color + (255,))
                
                # Composite the colored overlay onto the mockup
                mockup = Image.alpha_composite(mockup, colored_overlay)
            
            # Calculate position to center the design in the design area
            x_pos = design_area[0] + (design_width - new_width) // 2
            y_pos = design_area[1] + (design_height - new_height) // 2
            
            # Paste the design onto the mockup
            mockup.paste(design, (x_pos, y_pos), design)
            
            # Add variation-specific elements
            if product_type == 't-shirt' and variation == 'v-neck':
                # Modify for v-neck
                draw = ImageDraw.Draw(mockup)
                draw.polygon([(450, 300), (500, 350), (550, 300)], fill=(0, 0, 0, 0))
            elif product_type == 'sweatshirt' and variation == 'hoodie':
                # Add hood for hoodie
                draw = ImageDraw.Draw(mockup)
                draw.rectangle([(450, 150), (550, 200)], fill=(255, 255, 255, 255), outline=(0, 0, 0, 255))
            elif product_type == 'poster' and variation == 'framed':
                # Add frame for framed poster
                draw = ImageDraw.Draw(mockup)
                draw.rectangle([(90, 90), (910, 1310)], fill=None, outline=(0, 0, 0, 255), width=10)
            
            # Add product information
            font = self._get_default_font(20)
            if font:
                draw = ImageDraw.Draw(mockup)
                draw.text((500, 1350), f"{product_type.title()} - {color.title()} - {variation.title()}", 
                          fill=(0, 0, 0, 255), font=font, anchor="mm")
            
            # Create output filename
            design_name = os.path.splitext(os.path.basename(design_path))[0]
            output_filename = f"{design_name}_{product_type}_{color}_{variation}.png"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Save the mockup
            mockup.save(output_path)
            
            logger.info(f"Mockup created: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating mockup: {str(e)}")
            # Create a basic error mockup
            try:
                # Create a basic error image
                img = Image.new('RGB', (800, 800), (255, 255, 255))
                draw = ImageDraw.Draw(img)
                
                # Add error message
                font = self._get_default_font(20)
                if font:
                    draw.text((400, 400), f"Error creating mockup: {str(e)}", 
                              fill=(255, 0, 0), font=font, anchor="mm")
                
                # Create output filename
                design_name = os.path.splitext(os.path.basename(design_path))[0]
                output_filename = f"{design_name}_{product_type}_{color}_{variation}_error.png"
                output_path = os.path.join(self.output_dir, output_filename)
                
                # Save the error mockup
                img.save(output_path)
                
                logger.info(f"Error mockup created: {output_path}")
                return output_path
            except Exception as e2:
                logger.error(f"Error creating error mockup: {str(e2)}")
                return None
    
    def create_mockups_for_design(self, design_path, product_types=None, colors=None, variations=None):
        """Create mockups for a design with multiple product types, colors, and variations.
        
        Args:
            design_path (str): Path to the design image
            product_types (list, optional): List of product types
            colors (list, optional): List of colors
            variations (list, optional): List of variations
            
        Returns:
            list: List of paths to created mockups
        """
        logger.info(f"Creating mockups for design: {design_path}")
        
        mockup_paths = []
        
        try:
            # If product types not specified, use all available
            if not product_types:
                product_types = []
                for provider, products in self.print_providers.items():
                    product_types.extend(list(products.keys()))
                product_types = list(set(product_types))  # Remove duplicates
            
            # Process each product type
            for product_type in product_types:
                # Find provider for this product type
                provider_name = None
                product_details = None
                
                for provider, products in self.print_providers.items():
                    if product_type in products:
                        provider_name = provider
                        product_details = products[product_type]
                        break
                
                if not provider_name or not product_details:
                    logger.warning(f"No provider found for {product_type}, skipping")
                    continue
                
                # Use specified colors or default to all available
                product_colors = colors if colors else product_details['colors']
                
                # Use specified variations or default to all available
                product_variations = variations if variations else product_details['variations']
                
                # Create mockups for each combination
                for color in product_colors:
                    for variation in product_variations:
                        try:
                            mockup_path = self.create_mockup(design_path, product_type, color, variation)
                            if mockup_path:
                                mockup_paths.append(mockup_path)
                        except Exception as e:
                            logger.error(f"Error creating mockup for {product_type} {color} {variation}: {str(e)}")
            
            return mockup_paths
        
        except Exception as e:
            logger.error(f"Error creating mockups for design: {str(e)}")
            return mockup_paths
    
    def create_mockups_for_designs(self, design_paths, product_types=None, colors=None, variations=None):
        """Create mockups for multiple designs.
        
        Args:
            design_paths (list): List of paths to design images
            product_types (list, optional): List of product types
            colors (list, optional): List of colors
            variations (list, optional): List of variations
            
        Returns:
            dict: Dictionary mapping design paths to lists of mockup paths
        """
        logger.info(f"Creating mockups for {len(design_paths)} designs")
        
        results = {}
        
        for design_path in design_paths:
            try:
                mockup_paths = self.create_mockups_for_design(design_path, product_types, colors, variations)
                results[design_path] = mockup_paths
            except Exception as e:
                logger.error(f"Error creating mockups for {design_path}: {str(e)}")
                results[design_path] = []
        
        return results
    
    def create_3d_mockup(self, design_path, product_type, color='white', variation='standard', angle='front'):
        """Create a 3D mockup for a design.
        
        Args:
            design_path (str): Path to the design image
            product_type (str): Type of product
            color (str, optional): Product color
            variation (str, optional): Product variation
            angle (str, optional): Viewing angle ('front', 'side', 'perspective')
            
        Returns:
            str: Path to the created 3D mockup
        """
        logger.info(f"Creating 3D mockup for {design_path} on {product_type} ({color}, {variation}, {angle})")
        
        try:
            # First create a standard mockup
            standard_mockup_path = self.create_mockup(design_path, product_type, color, variation)
            
            if not standard_mockup_path:
                logger.error("Failed to create standard mockup for 3D transformation")
                return None
            
            # Load the standard mockup
            mockup = Image.open(standard_mockup_path).convert("RGBA")
            
            # Apply 3D transformation based on angle
            if angle == 'front':
                # Front view - no transformation needed
                transformed = mockup
            elif angle == 'side':
                # Side view - apply perspective transform
                width, height = mockup.size
                
                # Define the transformation (simple side view)
                from_points = [(0, 0), (width, 0), (width, height), (0, height)]
                to_points = [(width//4, 0), (width, 0), (width, height), (width//4, height)]
                
                # Apply perspective transform
                transformed = self._perspective_transform(mockup, from_points, to_points)
            elif angle == 'perspective':
                # Perspective view - apply more dramatic perspective transform
                width, height = mockup.size
                
                # Define the transformation (3/4 view)
                from_points = [(0, 0), (width, 0), (width, height), (0, height)]
                to_points = [(width//5, height//10), (width*4//5, 0), (width, height*4//5), (0, height)]
                
                # Apply perspective transform
                transformed = self._perspective_transform(mockup, from_points, to_points)
            else:
                # Unknown angle, use standard mockup
                logger.warning(f"Unknown angle {angle}, using standard mockup")
                transformed = mockup
            
            # Add shadow for 3D effect
            if angle != 'front':
                # Create a shadow
                shadow = Image.new('RGBA', transformed.size, (0, 0, 0, 0))
                shadow_draw = ImageDraw.Draw(shadow)
                
                # Draw shadow based on product type
                if product_type in ['t-shirt', 'sweatshirt', 'tank-top']:
                    # Shadow for apparel
                    shadow_draw.rectangle([(250, 800), (750, 820)], fill=(0, 0, 0, 100))
                elif product_type in ['poster', 'art-print', 'wall-art']:
                    # Shadow for wall art
                    shadow_draw.rectangle([(100, 1300), (900, 1320)], fill=(0, 0, 0, 100))
                elif product_type == 'pillow_case':
                    # Shadow for pillow
                    shadow_draw.ellipse([(300, 800), (700, 830)], fill=(0, 0, 0, 100))
                elif product_type == 'tote-bag':
                    # Shadow for tote bag
                    shadow_draw.rectangle([(300, 1100), (700, 1120)], fill=(0, 0, 0, 100))
                elif product_type == 'mug':
                    # Shadow for mug
                    shadow_draw.ellipse([(350, 600), (650, 630)], fill=(0, 0, 0, 100))
                
                # Blur the shadow
                shadow = shadow.filter(ImageFilter.GaussianBlur(10))
                
                # Create a new image with white background
                final = Image.new('RGBA', transformed.size, (255, 255, 255, 255))
                
                # Composite shadow and transformed mockup
                final = Image.alpha_composite(final, shadow)
                final = Image.alpha_composite(final, transformed)
                
                transformed = final
            
            # Add 3D label
            font = self._get_default_font(20)
            if font:
                draw = ImageDraw.Draw(transformed)
                draw.text((transformed.width//2, transformed.height - 50), 
                          f"3D View - {angle.title()}", 
                          fill=(0, 0, 0, 255), font=font, anchor="mm")
            
            # Create output filename
            design_name = os.path.splitext(os.path.basename(design_path))[0]
            output_filename = f"{design_name}_{product_type}_{color}_{variation}_3d_{angle}.png"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Save the 3D mockup
            transformed.save(output_path)
            
            logger.info(f"3D mockup created: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating 3D mockup: {str(e)}")
            return None
    
    def _perspective_transform(self, img, from_points, to_points):
        """Apply perspective transform to an image.
        
        Args:
            img (Image): Input image
            from_points (list): List of source points [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
            to_points (list): List of destination points [(x1,y1), (x2,y2), (x3,y3), (x4,y4)]
            
        Returns:
            Image: Transformed image
        """
        try:
            # Try to use the perspective transform from PIL
            import numpy as np
            from PIL import Image
            
            # Convert points to numpy arrays
            src_points = np.float32(from_points)
            dst_points = np.float32(to_points)
            
            # Get transformation matrix
            import cv2
            matrix = cv2.getPerspectiveTransform(src_points, dst_points)
            
            # Convert PIL image to numpy array
            img_array = np.array(img)
            
            # Apply transformation
            result_array = cv2.warpPerspective(
                img_array, 
                matrix, 
                (img.width, img.height), 
                borderMode=cv2.BORDER_CONSTANT, 
                borderValue=(0, 0, 0, 0)
            )
            
            # Convert back to PIL image
            result = Image.fromarray(result_array)
            
            return result
        
        except (ImportError, Exception) as e:
            logger.error(f"Error applying perspective transform: {str(e)}")
            # Return original image if transform fails
            return img
    
    def create_lifestyle_mockup(self, design_path, product_type, scene='generic'):
        """Create a lifestyle mockup showing the product in use.
        
        Args:
            design_path (str): Path to the design image
            product_type (str): Type of product
            scene (str, optional): Type of lifestyle scene
            
        Returns:
            str: Path to the created lifestyle mockup
        """
        logger.info(f"Creating lifestyle mockup for {design_path} on {product_type} (scene: {scene})")
        
        try:
            # Create a standard mockup first
            standard_mockup_path = self.create_mockup(design_path, product_type)
            
            if not standard_mockup_path:
                logger.error("Failed to create standard mockup for lifestyle transformation")
                return None
            
            # Load the standard mockup
            mockup = Image.open(standard_mockup_path).convert("RGBA")
            
            # Create a background scene based on product type and scene
            scene_width, scene_height = 1200, 1800
            scene_img = Image.new('RGBA', (scene_width, scene_height), (255, 255, 255, 255))
            scene_draw = ImageDraw.Draw(scene_img)
            
            # Draw scene elements based on product type and scene
            if product_type in ['t-shirt', 'sweatshirt', 'tank-top']:
                if scene == 'model':
                    # Simulate a person wearing the product
                    # Draw a simple person silhouette
                    scene_draw.ellipse([(500, 200), (700, 400)], fill=(200, 200, 200, 255))  # Head
                    scene_draw.rectangle([(550, 400), (650, 800)], fill=(200, 200, 200, 255))  # Body
                    scene_draw.rectangle([(450, 450), (550, 800)], fill=(200, 200, 200, 255))  # Left arm
                    scene_draw.rectangle([(650, 450), (750, 800)], fill=(200, 200, 200, 255))  # Right arm
                    scene_draw.rectangle([(550, 800), (600, 1200)], fill=(200, 200, 200, 255))  # Left leg
                    scene_draw.rectangle([(600, 800), (650, 1200)], fill=(200, 200, 200, 255))  # Right leg
                else:
                    # Generic scene - hanging on rack
                    scene_draw.line([(300, 200), (900, 200)], fill=(150, 150, 150, 255), width=5)  # Rack
                    scene_draw.line([(600, 100), (600, 200)], fill=(150, 150, 150, 255), width=5)  # Hanger
            
            elif product_type in ['poster', 'art-print', 'wall-art']:
                if scene == 'living_room':
                    # Living room wall
                    scene_draw.rectangle([(0, 0), (scene_width, scene_height*2//3)], fill=(240, 240, 240, 255))  # Wall
                    scene_draw.rectangle([(0, scene_height*2//3), (scene_width, scene_height)], fill=(180, 160, 140, 255))  # Floor
                    # Draw a simple sofa
                    scene_draw.rectangle([(200, scene_height*2//3 - 150), (1000, scene_height*2//3 + 50)], fill=(150, 150, 180, 255))
                else:
                    # Generic scene - gallery wall
                    scene_draw.rectangle([(0, 0), (scene_width, scene_height)], fill=(240, 240, 240, 255))  # Wall
            
            elif product_type == 'pillow_case':
                if scene == 'bedroom':
                    # Bedroom scene
                    scene_draw.rectangle([(0, 0), (scene_width, scene_height*2//3)], fill=(240, 240, 240, 255))  # Wall
                    scene_draw.rectangle([(0, scene_height*2//3), (scene_width, scene_height)], fill=(180, 160, 140, 255))  # Floor
                    # Draw a simple bed
                    scene_draw.rectangle([(200, scene_height*2//3 - 100), (1000, scene_height*2//3 + 200)], fill=(220, 220, 240, 255))
                else:
                    # Generic scene - couch
                    scene_draw.rectangle([(0, 0), (scene_width, scene_height*2//3)], fill=(240, 240, 240, 255))  # Wall
                    scene_draw.rectangle([(0, scene_height*2//3), (scene_width, scene_height)], fill=(180, 160, 140, 255))  # Floor
                    # Draw a simple couch
                    scene_draw.rectangle([(200, scene_height*2//3 - 150), (1000, scene_height*2//3 + 100)], fill=(180, 180, 200, 255))
            
            elif product_type == 'tote-bag':
                if scene == 'outdoor':
                    # Outdoor scene
                    scene_draw.rectangle([(0, 0), (scene_width, scene_height//3)], fill=(135, 206, 235, 255))  # Sky
                    scene_draw.rectangle([(0, scene_height//3), (scene_width, scene_height)], fill=(120, 180, 120, 255))  # Grass
                else:
                    # Generic scene - hanging on hook
                    scene_draw.rectangle([(0, 0), (scene_width, scene_height)], fill=(240, 240, 240, 255))  # Wall
                    scene_draw.rectangle([(595, 200), (605, 250)], fill=(150, 150, 150, 255))  # Hook
            
            elif product_type == 'mug':
                if scene == 'desk':
                    # Desk scene
                    scene_draw.rectangle([(0, 0), (scene_width, scene_height*2//3)], fill=(240, 240, 240, 255))  # Wall
                    scene_draw.rectangle([(0, scene_height*2//3), (scene_width, scene_height)], fill=(160, 140, 120, 255))  # Desk
                    # Draw a simple laptop
                    scene_draw.rectangle([(700, scene_height*2//3 - 100), (1000, scene_height*2//3)], fill=(80, 80, 80, 255))
                else:
                    # Generic scene - kitchen counter
                    scene_draw.rectangle([(0, 0), (scene_width, scene_height*2//3)], fill=(240, 240, 240, 255))  # Wall
                    scene_draw.rectangle([(0, scene_height*2//3), (scene_width, scene_height)], fill=(200, 200, 200, 255))  # Counter
            
            # Resize the mockup to fit in the scene
            mockup_width, mockup_height = mockup.size
            scale_factor = 0.5  # Adjust as needed
            new_width = int(mockup_width * scale_factor)
            new_height = int(mockup_height * scale_factor)
            mockup_resized = mockup.resize((new_width, new_height), Image.LANCZOS)
            
            # Position the mockup in the scene
            if product_type in ['t-shirt', 'sweatshirt', 'tank-top']:
                if scene == 'model':
                    # Position on the model's torso
                    x_pos = (scene_width - new_width) // 2
                    y_pos = 400
                else:
                    # Position hanging on rack
                    x_pos = (scene_width - new_width) // 2
                    y_pos = 250
            
            elif product_type in ['poster', 'art-print', 'wall-art']:
                # Position on wall
                x_pos = (scene_width - new_width) // 2
                y_pos = scene_height // 4
            
            elif product_type == 'pillow_case':
                if scene == 'bedroom':
                    # Position on bed
                    x_pos = (scene_width - new_width) // 2
                    y_pos = scene_height*2//3 - 50
                else:
                    # Position on couch
                    x_pos = (scene_width - new_width) // 2
                    y_pos = scene_height*2//3 - 100
            
            elif product_type == 'tote-bag':
                if scene == 'outdoor':
                    # Position in outdoor scene
                    x_pos = (scene_width - new_width) // 2
                    y_pos = scene_height // 2
                else:
                    # Position hanging on hook
                    x_pos = (scene_width - new_width) // 2
                    y_pos = 300
            
            elif product_type == 'mug':
                if scene == 'desk':
                    # Position on desk next to laptop
                    x_pos = 500
                    y_pos = scene_height*2//3 - 150
                else:
                    # Position on counter
                    x_pos = (scene_width - new_width) // 2
                    y_pos = scene_height*2//3 - 100
            
            else:
                # Default position
                x_pos = (scene_width - new_width) // 2
                y_pos = (scene_height - new_height) // 2
            
            # Paste the mockup onto the scene
            scene_img.paste(mockup_resized, (x_pos, y_pos), mockup_resized)
            
            # Add scene label
            font = self._get_default_font(20)
            if font:
                scene_draw = ImageDraw.Draw(scene_img)
                scene_draw.text((scene_width//2, scene_height - 50), 
                                f"Lifestyle Mockup - {scene.replace('_', ' ').title()}", 
                                fill=(0, 0, 0, 255), font=font, anchor="mm")
            
            # Create output filename
            design_name = os.path.splitext(os.path.basename(design_path))[0]
            output_filename = f"{design_name}_{product_type}_lifestyle_{scene}.png"
            output_path = os.path.join(self.output_dir, output_filename)
            
            # Save the lifestyle mockup
            scene_img.save(output_path)
            
            logger.info(f"Lifestyle mockup created: {output_path}")
            return output_path
        
        except Exception as e:
            logger.error(f"Error creating lifestyle mockup: {str(e)}")
            return None
    
    def create_all_mockup_types(self, design_path, product_type, color='white', variation='standard'):
        """Create all types of mockups for a design (standard, 3D, lifestyle).
        
        Args:
            design_path (str): Path to the design image
            product_type (str): Type of product
            color (str, optional): Product color
            variation (str, optional): Product variation
            
        Returns:
            dict: Dictionary of mockup paths by type
        """
        logger.info(f"Creating all mockup types for {design_path} on {product_type}")
        
        results = {
            'standard': None,
            '3d': {},
            'lifestyle': {}
        }
        
        try:
            # Create standard mockup
            standard_mockup = self.create_mockup(design_path, product_type, color, variation)
            results['standard'] = standard_mockup
            
            # Create 3D mockups
            for angle in ['front', 'side', 'perspective']:
                try:
                    mockup_3d = self.create_3d_mockup(design_path, product_type, color, variation, angle)
                    results['3d'][angle] = mockup_3d
                except Exception as e:
                    logger.error(f"Error creating 3D mockup ({angle}): {str(e)}")
            
            # Create lifestyle mockups
            scenes = []
            if product_type in ['t-shirt', 'sweatshirt', 'tank-top']:
                scenes = ['generic', 'model']
            elif product_type in ['poster', 'art-print', 'wall-art']:
                scenes = ['generic', 'living_room']
            elif product_type == 'pillow_case':
                scenes = ['generic', 'bedroom']
            elif product_type == 'tote-bag':
                scenes = ['generic', 'outdoor']
            elif product_type == 'mug':
                scenes = ['generic', 'desk']
            
            for scene in scenes:
                try:
                    lifestyle_mockup = self.create_lifestyle_mockup(design_path, product_type, scene)
                    results['lifestyle'][scene] = lifestyle_mockup
                except Exception as e:
                    logger.error(f"Error creating lifestyle mockup ({scene}): {str(e)}")
            
            return results
        
        except Exception as e:
            logger.error(f"Error creating all mockup types: {str(e)}")
            return results

# For testing
if __name__ == "__main__":
    # Create a test design
    test_dir = "test_mockups"
    os.makedirs(test_dir, exist_ok=True)
    
    # Create a simple test design
    test_design_path = os.path.join(test_dir, "test_design.png")
    img = Image.new('RGBA', (800, 800), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(200, 200), (600, 600)], fill=(255, 0, 0, 255))
    draw.text((400, 400), "Test Design", fill=(255, 255, 255, 255))
    img.save(test_design_path)
    
    # Initialize mockup generator
    config = {
        'designs_dir': test_dir,
        'output_dir': test_dir,
        'templates_dir': os.path.join(test_dir, 'templates')
    }
    generator = MockupGenerator(config=config)
    
    # Create mockups
    mockup_path = generator.create_mockup(test_design_path, 't-shirt')
    print(f"Created mockup: {mockup_path}")
    
    mockup_paths = generator.create_mockups_for_design(test_design_path)
    print(f"Created {len(mockup_paths)} mockups")
    
    mockup_3d = generator.create_3d_mockup(test_design_path, 't-shirt')
    print(f"Created 3D mockup: {mockup_3d}")
    
    lifestyle_mockup = generator.create_lifestyle_mockup(test_design_path, 't-shirt')
    print(f"Created lifestyle mockup: {lifestyle_mockup}")
    
    all_mockups = generator.create_all_mockup_types(test_design_path, 't-shirt')
    print(f"Created all mockup types: {all_mockups}")
