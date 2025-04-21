"""
Publishing Agent for POD Automation System.
Automates the publishing process to Printify and Etsy using the API integrations.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from pathlib import Path
import random
import base64

# Set up logging
from pod_automation.config.logging_config import setup_logging
setup_logging()
logger = logging.getLogger(__name__)

# Import API clients
from pod_automation.api.printify_api import PrintifyAPI
from pod_automation.api.etsy_api import EtsyAPI
from pod_automation.utils.api_optimization import optimize_api_client

class PublishingAgent:
    """Agent for automating the publishing process to Printify and Etsy."""
    
    def __init__(self, config=None):
        """Initialize publishing agent.
        
        Args:
            config (dict, optional): Configuration dictionary
        """
        self.config = config or {}
        
        # Set up directories
        self.designs_dir = self.config.get('designs_dir', 'data/designs')
        self.mockups_dir = self.config.get('mockups_dir', 'data/mockups')
        self.output_dir = self.config.get('output_dir', 'data/published')
        
        os.makedirs(self.designs_dir, exist_ok=True)
        os.makedirs(self.mockups_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize API clients
        printify_api_key = self.config.get('printify_api_key') or os.environ.get('PRINTIFY_API_KEY')
        printify_shop_id = self.config.get('printify_shop_id') or os.environ.get('PRINTIFY_SHOP_ID')
        
        etsy_api_key = self.config.get('etsy_api_key') or os.environ.get('ETSY_API_KEY')
        etsy_api_secret = self.config.get('etsy_api_secret') or os.environ.get('ETSY_API_SECRET')
        etsy_shop_id = self.config.get('etsy_shop_id') or os.environ.get('ETSY_SHOP_ID')
        
        # Initialize Printify API client
        self.printify = None
        if printify_api_key and printify_shop_id:
            self.printify = optimize_api_client(
                PrintifyAPI(api_key=printify_api_key, shop_id=printify_shop_id)
            )
        else:
            logger.warning("Printify API key or shop ID not set. Printify publishing will be unavailable.")
        
        # Initialize Etsy API client
        self.etsy = None
        if etsy_api_key and etsy_api_secret:
            self.etsy = optimize_api_client(
                EtsyAPI(api_key=etsy_api_key, api_secret=etsy_api_secret, shop_id=etsy_shop_id)
            )
        else:
            logger.warning("Etsy API key or secret not set. Etsy publishing will be unavailable.")
        
        # Set up print provider mappings
        self.print_provider_mappings = {
            't-shirt': {
                'provider': 'monster_digital',
                'provider_id': 29,  # Monster Digital ID in Printify
                'blueprint_id': '5d39b76eb2e9a90016473cd1',  # T-shirt blueprint ID
                'variants': self._get_tshirt_variants()
            },
            'sweatshirt': {
                'provider': 'monster_digital',
                'provider_id': 29,  # Monster Digital ID in Printify
                'blueprint_id': '5d39b773b2e9a90016473cd3',  # Sweatshirt blueprint ID
                'variants': self._get_sweatshirt_variants()
            },
            'poster': {
                'provider': 'sensaria',
                'provider_id': 16,  # Sensaria ID in Printify
                'blueprint_id': '5d39b80cb2e9a90016473ce0',  # Poster blueprint ID
                'variants': self._get_poster_variants()
            },
            'pillow_case': {
                'provider': 'mww',
                'provider_id': 1,  # MWW ID in Printify
                'blueprint_id': '5d39b7f7b2e9a90016473cde',  # Pillow case blueprint ID
                'variants': self._get_pillow_variants()
            }
        }
    
    def _get_tshirt_variants(self):
        """Get T-shirt variants.
        
        Returns:
            list: List of variant dictionaries
        """
        # In a real implementation, these would be fetched from Printify API
        # For this demonstration, we'll use placeholder data
        return [
            {'id': 38377, 'title': 'White / S', 'price': 1999},
            {'id': 38378, 'title': 'White / M', 'price': 1999},
            {'id': 38379, 'title': 'White / L', 'price': 1999},
            {'id': 38380, 'title': 'White / XL', 'price': 1999},
            {'id': 38381, 'title': 'White / 2XL', 'price': 2199},
            {'id': 38382, 'title': 'Black / S', 'price': 1999},
            {'id': 38383, 'title': 'Black / M', 'price': 1999},
            {'id': 38384, 'title': 'Black / L', 'price': 1999},
            {'id': 38385, 'title': 'Black / XL', 'price': 1999},
            {'id': 38386, 'title': 'Black / 2XL', 'price': 2199}
        ]
    
    def _get_sweatshirt_variants(self):
        """Get sweatshirt variants.
        
        Returns:
            list: List of variant dictionaries
        """
        # In a real implementation, these would be fetched from Printify API
        # For this demonstration, we'll use placeholder data
        return [
            {'id': 38387, 'title': 'Gray / S', 'price': 2999},
            {'id': 38388, 'title': 'Gray / M', 'price': 2999},
            {'id': 38389, 'title': 'Gray / L', 'price': 2999},
            {'id': 38390, 'title': 'Gray / XL', 'price': 2999},
            {'id': 38391, 'title': 'Gray / 2XL', 'price': 3199},
            {'id': 38392, 'title': 'Black / S', 'price': 2999},
            {'id': 38393, 'title': 'Black / M', 'price': 2999},
            {'id': 38394, 'title': 'Black / L', 'price': 2999},
            {'id': 38395, 'title': 'Black / XL', 'price': 2999},
            {'id': 38396, 'title': 'Black / 2XL', 'price': 3199}
        ]
    
    def _get_poster_variants(self):
        """Get poster variants.
        
        Returns:
            list: List of variant dictionaries
        """
        # In a real implementation, these would be fetched from Printify API
        # For this demonstration, we'll use placeholder data
        return [
            {'id': 38397, 'title': '12×16 in', 'price': 1499},
            {'id': 38398, 'title': '16×20 in', 'price': 1999},
            {'id': 38399, 'title': '18×24 in', 'price': 2499},
            {'id': 38400, 'title': '24×36 in', 'price': 2999}
        ]
    
    def _get_pillow_variants(self):
        """Get pillow case variants.
        
        Returns:
            list: List of variant dictionaries
        """
        # In a real implementation, these would be fetched from Printify API
        # For this demonstration, we'll use placeholder data
        return [
            {'id': 38401, 'title': '14×14 in', 'price': 1999},
            {'id': 38402, 'title': '16×16 in', 'price': 2199},
            {'id': 38403, 'title': '18×18 in', 'price': 2399},
            {'id': 38404, 'title': '20×20 in', 'price': 2599}
        ]
    
    def upload_design_to_printify(self, design_path):
        """Upload a design to Printify.
        
        Args:
            design_path (str): Path to design image
            
        Returns:
            dict: Printify image data or None if upload failed
        """
        if not self.printify:
            logger.error("Printify API client not initialized")
            return None
        
        logger.info(f"Uploading design to Printify: {design_path}")
        
        try:
            # Read image file
            with open(design_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Upload image to Printify
            response = self.printify.upload_image({
                'file_name': os.path.basename(design_path),
                'contents': image_data
            })
            
            if 'id' in response:
                logger.info(f"Design uploaded successfully to Printify. Image ID: {response['id']}")
                return response
            else:
                logger.error(f"Failed to upload design to Printify: {response}")
                return None
        
        except Exception as e:
            logger.error(f"Error uploading design to Printify: {str(e)}")
            return None
    
    def create_printify_product(self, title, description, design_path, product_type, tags=None, publish=False):
        """Create a product on Printify.
        
        Args:
            title (str): Product title
            description (str): Product description
            design_path (str): Path to design image
            product_type (str): Type of product (t-shirt, sweatshirt, poster, pillow_case)
            tags (list, optional): List of tags
            publish (bool, optional): Whether to publish the product
            
        Returns:
            dict: Printify product data or None if creation failed
        """
        if not self.printify:
            logger.error("Printify API client not initialized")
            return None
        
        if product_type not in self.print_provider_mappings:
            logger.error(f"Unsupported product type: {product_type}")
            return None
        
        logger.info(f"Creating {product_type} product on Printify: {title}")
        
        try:
            # Upload design to Printify
            image_data = self.upload_design_to_printify(design_path)
            if not image_data:
                return None
            
            # Get product mapping
            product_mapping = self.print_provider_mappings[product_type]
            
            # Prepare variants
            variants = []
            for variant in product_mapping['variants']:
                variants.append({
                    'id': variant['id'],
                    'price': variant['price'],
                    'is_enabled': True
                })
            
            # Prepare print areas
            print_areas = [{
                'variant_ids': [v['id'] for v in product_mapping['variants']],
                'placeholders': [{
                    'position': 'front',
                    'images': [{
                        'id': image_data['id'],
                        'x': 0.5,
                        'y': 0.5,
                        'scale': 1,
                        'angle': 0
                    }]
                }]
            }]
            
            # Create product
            product_data = {
                'title': title,
                'description': description,
                'blueprint_id': product_mapping['blueprint_id'],
                'print_provider_id': product_mapping['provider_id'],
                'variants': variants,
                'print_areas': print_areas
            }
            
            if tags:
                product_data['tags'] = tags
            
            # Create product on Printify
            product = self.printify.create_product(product_data)
            
            if 'id' in product:
                logger.info(f"Product created successfully on Printify. Product ID: {product['id']}")
                
                # Publish product if requested
                if publish:
                    publish_result = self.printify.publish_product(product['id'])
                    if publish_result.get('status') == 'success':
                        logger.info(f"Product published successfully on Printify. Product ID: {product['id']}")
                    else:
                        logger.error(f"Failed to publish product on Printify: {publish_result}")
                
                return product
            else:
                logger.error(f"Failed to create product on Printify: {product}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating product on Printify: {str(e)}")
            return None
    
    def upload_image_to_etsy(self, listing_id, image_path):
        """Upload an image to an Etsy listing.
        
        Args:
            listing_id (int): Etsy listing ID
            image_path (str): Path to image
            
        Returns:
            dict: Etsy image data or None if upload failed
        """
        if not self.etsy:
            logger.error("Etsy API client not initialized")
            return None
        
        logger.info(f"Uploading image to Etsy listing {listing_id}: {image_path}")
        
        try:
            # Read image file
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Upload image to Etsy
            response = self.etsy.upload_listing_image(
                listing_id,
                {
                    'image': image_data,
                    'file_name': os.path.basename(image_path)
                }
            )
            
            if 'listing_image_id' in response:
                logger.info(f"Image uploaded successfully to Etsy. Image ID: {response['listing_image_id']}")
                return response
            else:
                logger.error(f"Failed to upload image to Etsy: {response}")
                return None
        
        except Exception as e:
            logger.error(f"Error uploading image to Etsy: {str(e)}")
            return None
    
    def create_etsy_listing(self, title, description, price, design_path, mockup_paths, tags=None, is_draft=True):
        """Create a listing on Etsy.
        
        Args:
            title (str): Listing title
            description (str): Listing description
            price (float): Listing price
            design_path (str): Path to design image
            mockup_paths (list): List of paths to mockup images
            tags (list, optional): List of tags
            is_draft (bool, optional): Whether to create as draft
            
        Returns:
            dict: Etsy listing data or None if creation failed
        """
        if not self.etsy:
            logger.error("Etsy API client not initialized")
            return None
        
        logger.info(f"Creating listing on Etsy: {title}")
        
        try:
            # Ensure Etsy authentication
            if not self.etsy.access_token:
                logger.info("Starting Etsy OAuth flow")
                self.etsy.start_oauth_flow()
            
            # Prepare listing data
            listing_data = {
                'quantity': 999,
                'title': title,
                'description': description,
                'price': {
                    'amount': int(price * 100),  # Convert to cents
                    'currency_code': 'USD'
                },
                'who_made': 'i_did',
                'when_made': 'made_to_order',
                'taxonomy_id': 1234,  # Clothing category
                'type': 'physical',
                'shipping_profile_id': 5678,  # This would be fetched from Etsy in a real implementation
                'materials': ['cotton', 'polyester'],
                'shop_section_id': 9012,  # This would be fetched from Etsy in a real implementation
                'is_customizable': False,
                'is_digital': False,
                'processing_min': 1,
                'processing_max': 3,
                'production_partner_ids': []
            }
            
            if tags:
                listing_data['tags'] = tags
            
            # Create listing on Etsy
            if is_draft:
                listing = self.etsy.create_draft_listing(listing_data)
            else:
                listing = self.etsy.create_listing(listing_data)
            
            if 'listing_id' in listing:
                logger.info(f"Listing created successfully on Etsy. Listing ID: {listing['listing_id']}")
                
                # Upload images
                all_images = [design_path] + mockup_paths
                for image_path in all_images:
                    image_result = self.upload_image_to_etsy(listing['listing_id'], image_path)
                    if not image_result:
                        logger.warning(f"Failed to upload image to Etsy: {image_path}")
                
                return listing
            else:
                logger.error(f"Failed to create listing on Etsy: {listing}")
                return None
        
        except Exception as e:
            logger.error(f"Error creating listing on Etsy: {str(e)}")
            return None
    
    def publish_design(self, design_path, title, description, product_types=None, tags=None, mockup_paths=None):
        """Publish a design to Printify and Etsy.
        
        Args:
            design_path (str): Path to design image
            title (str): Product/listing title
            description (str): Product/listing description
            product_types (list, optional): List of product types
            tags (list, optional): List of tags
            mockup_paths (list, optional): List of paths to mockup images
            
        Returns:
            dict: Publishing results
        """
        logger.info(f"Publishing design: {design_path}")
        
        # Use default product types if none specified
        if product_types is None:
            product_types = ['t-shirt', 'poster', 'pillow_case']
        
        # Use default tags if none specified
        if tags is None:
            tags = ['cat', 'cat lover', 'cat design', 'cute cat', 'cat gift']
        
        # Initialize results
        results = {
            'design': design_path,
            'title': title,
            'description': description,
            'printify_products': [],
            'etsy_listings': []
        }
        
        # Publish to Printify
        if self.printify:
            for product_type in product_types:
                product = self.create_printify_product(
                    title=f"{title} - {product_type.replace('_', ' ').title()}",
                    description=description,
                    design_path=design_path,
                    product_type=product_type,
                    tags=tags,
                    publish=True
                )
                
                if product:
                    results['printify_products'].append({
                        'product_id': product['id'],
                        'product_type': product_type,
                        'title': product['title']
                    })
        
        # Publish to Etsy
        if self.etsy:
            # Use mockups if provided, otherwise use design
            images_to_upload = [design_path]
            if mockup_paths:
                images_to_upload.extend(mockup_paths)
            
            # Create Etsy listing
            listing = self.create_etsy_listing(
                title=title,
                description=description,
                price=29.99,  # Default price
                design_path=design_path,
                mockup_paths=mockup_paths or [],
                tags=tags,
                is_draft=True
            )
            
            if listing:
                results['etsy_listings'].append({
                    'listing_id': listing['listing_id'],
                    'title': listing['title']
                })
        
        # Save results
        timestamp = int(time.time())
        design_name = os.path.basename(design_path).split('.')[0]
        results_path = os.path.join(self.output_dir, f"published_{design_name}_{timestamp}.json")
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Publishing results saved to: {results_path}")
        
        return results
    
    def publish_collection(self, collection_name, designs_data):
        """Publish a collection of designs.
        
        Args:
            collection_name (str): Name of the collection
            designs_data (list): List of design data dictionaries
            
        Returns:
            dict: Collection publishing results
        """
        logger.info(f"Publishing collection: {collection_name}")
        
        # Initialize results
        results = {
            'collection_name': collection_name,
            'timestamp': int(time.time()),
            'designs': []
        }
        
        # Publish each design
        for design_data in designs_data:
            design_result = self.publish_design(
                design_path=design_data['design_path'],
                title=design_data['title'],
                description=design_data['description'],
                product_types=design_data.get('product_types'),
                tags=design_data.get('tags'),
                mockup_paths=design_data.get('mockup_paths')
            )
            
            results['designs'].append(design_result)
        
        # Save collection results
        timestamp = int(time.time())
        results_path = os.path.join(self.output_dir, f"collection_{collection_name}_{timestamp}.json")
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Collection publishing results saved to: {results_path}")
        
        return results
    
    def validate_api_connections(self):
        """Validate API connections to Printify and Etsy.
        
        Returns:
            dict: Validation results
        """
        logger.info("Validating API connections")
        
        results = {
            'printify': {
                'connected': False,
                'shop_info': None,
                'error': None
            },
            'etsy': {
                'connected': False,
                'shop_info': None,
                'error': None
            }
        }
        
        # Validate Printify connection
        if self.printify:
            try:
                shop_info = self.printify.get_shop()
                if 'id' in shop_info:
                    results['printify']['connected'] = True
                    results['printify']['shop_info'] = {
                        'id': shop_info['id'],
                        'title': shop_info.get('title', 'Unknown')
                    }
                else:
                    results['printify']['error'] = "Failed to get shop information"
            except Exception as e:
                results['printify']['error'] = str(e)
        else:
            results['printify']['error'] = "Printify API client not initialized"
        
        # Validate Etsy connection
        if self.etsy:
            try:
                # Ensure Etsy authentication
                if not self.etsy.access_token:
                    logger.info("Starting Etsy OAuth flow")
                    self.etsy.start_oauth_flow()
                
                shop_info = self.etsy.get_shop()
                if 'shop_id' in shop_info:
                    results['etsy']['connected'] = True
                    results['etsy']['shop_info'] = {
                        'shop_id': shop_info['shop_id'],
                        'shop_name': shop_info.get('shop_name', 'Unknown')
                    }
                else:
                    results['etsy']['error'] = "Failed to get shop information"
            except Exception as e:
                results['etsy']['error'] = str(e)
        else:
            results['etsy']['error'] = "Etsy API client not initialized"
        
        logger.info(f"API validation results: Printify: {results['printify']['connected']}, Etsy: {results['etsy']['connected']}")
        
        return results

def main():
    """Main function to test publishing agent."""
    logger.info("Testing Publishing Agent")
    
    # Check if API keys are set
    printify_api_key = os.environ.get('PRINTIFY_API_KEY')
    printify_shop_id = os.environ.get('PRINTIFY_SHOP_ID')
    etsy_api_key = os.environ.get('ETSY_API_KEY')
    etsy_api_secret = os.environ.get('ETSY_API_SECRET')
    
    if not printify_api_key or not printify_shop_id:
        logger.warning("Printify API key or shop ID not set. Printify publishing will be unavailable.")
    
    if not etsy_api_key or not etsy_api_secret:
        logger.warning("Etsy API key or secret not set. Etsy publishing will be unavailable.")
    
    # Create publishing agent
    agent = PublishingAgent()
    
    # Validate API connections
    validation_results = agent.validate_api_connections()
    
    if validation_results['printify']['connected'] or validation_results['etsy']['connected']:
        logger.info("API validation successful")
    else:
        logger.error("API validation failed")

if __name__ == "__main__":
    main()
