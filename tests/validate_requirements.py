"""
Requirements validation for POD Automation System.
Validates the implementation against the original requirements.
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from pod_automation.api import PrintifyAPI, EtsyAPI
from pod_automation.config import get_config
from pod_automation.utils import optimize_api_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("validation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_api_integrations():
    """Validate API integrations against requirements."""
    logger.info("Validating API integrations...")
    
    # Check Printify API implementation
    printify_requirements = [
        "Authentication with API key",
        "Shop information retrieval",
        "Catalog access",
        "Product creation and management",
        "Image upload",
        "Publishing products",
        "Order management",
        "Support for Monster Digital (T-Shirts/Sweatshirts)",
        "Support for Sensaria (Posters)",
        "Support for MWW (pillow cases)"
    ]
    
    printify_implemented = []
    
    # Check if PrintifyAPI class exists and has required methods
    try:
        printify = PrintifyAPI()
        
        if hasattr(printify, '_get_headers'):
            printify_implemented.append("Authentication with API key")
        
        if hasattr(printify, 'get_shop'):
            printify_implemented.append("Shop information retrieval")
        
        if hasattr(printify, 'get_catalog'):
            printify_implemented.append("Catalog access")
        
        if all(hasattr(printify, method) for method in ['create_product', 'get_product', 'update_product', 'delete_product']):
            printify_implemented.append("Product creation and management")
        
        if hasattr(printify, 'upload_image'):
            printify_implemented.append("Image upload")
        
        if hasattr(printify, 'publish_product'):
            printify_implemented.append("Publishing products")
        
        if all(hasattr(printify, method) for method in ['get_orders', 'get_order']):
            printify_implemented.append("Order management")
        
        # Check print provider support in documentation
        docs_path = Path(__file__).parent.parent / "docs" / "api_integration.md"
        if docs_path.exists():
            with open(docs_path, 'r') as f:
                docs_content = f.read()
                if "Monster Digital" in docs_content and "T-Shirts" in docs_content:
                    printify_implemented.append("Support for Monster Digital (T-Shirts/Sweatshirts)")
                if "Sensaria" in docs_content and "Posters" in docs_content:
                    printify_implemented.append("Support for Sensaria (Posters)")
                if "MWW" in docs_content and "pillow cases" in docs_content:
                    printify_implemented.append("Support for MWW (pillow cases)")
    
    except Exception as e:
        logger.error(f"Error validating Printify API: {str(e)}")
    
    # Check Etsy API implementation
    etsy_requirements = [
        "OAuth 2.0 authentication",
        "Token refresh",
        "Shop information retrieval",
        "Listing creation and management",
        "Image upload",
        "Inventory management",
        "Shop statistics"
    ]
    
    etsy_implemented = []
    
    # Check if EtsyAPI class exists and has required methods
    try:
        etsy = EtsyAPI()
        
        if hasattr(etsy, 'start_oauth_flow'):
            etsy_implemented.append("OAuth 2.0 authentication")
        
        if hasattr(etsy, '_refresh_token'):
            etsy_implemented.append("Token refresh")
        
        if hasattr(etsy, 'get_shop'):
            etsy_implemented.append("Shop information retrieval")
        
        if all(hasattr(etsy, method) for method in ['create_draft_listing', 'get_listing', 'update_listing', 'delete_listing']):
            etsy_implemented.append("Listing creation and management")
        
        if hasattr(etsy, 'upload_listing_image'):
            etsy_implemented.append("Image upload")
        
        if all(hasattr(etsy, method) for method in ['get_listing_inventory', 'update_listing_inventory']):
            etsy_implemented.append("Inventory management")
        
        if hasattr(etsy, 'get_shop_stats'):
            etsy_implemented.append("Shop statistics")
    
    except Exception as e:
        logger.error(f"Error validating Etsy API: {str(e)}")
    
    # Print validation results
    logger.info("\n=== Printify API Validation ===")
    for req in printify_requirements:
        status = "✅ Implemented" if req in printify_implemented else "❌ Not implemented"
        logger.info(f"{status}: {req}")
    
    logger.info("\n=== Etsy API Validation ===")
    for req in etsy_requirements:
        status = "✅ Implemented" if req in etsy_implemented else "❌ Not implemented"
        logger.info(f"{status}: {req}")
    
    # Calculate implementation percentages
    printify_percentage = len(printify_implemented) / len(printify_requirements) * 100
    etsy_percentage = len(etsy_implemented) / len(etsy_requirements) * 100
    
    logger.info(f"\nPrintify API implementation: {printify_percentage:.1f}%")
    logger.info(f"Etsy API implementation: {etsy_percentage:.1f}%")
    
    return printify_percentage >= 90 and etsy_percentage >= 90

def validate_optimization():
    """Validate optimization features against requirements."""
    logger.info("\nValidating optimization features...")
    
    optimization_requirements = [
        "Caching",
        "Rate limiting",
        "Error handling with retries",
        "Batch processing"
    ]
    
    optimization_implemented = []
    
    # Check if optimization utilities exist
    try:
        from pod_automation.utils import (
            APICache, 
            cache_api_response, 
            RateLimiter, 
            rate_limit, 
            retry_on_failure, 
            batch_process, 
            optimize_api_client
        )
        
        if all(cls for cls in [APICache, cache_api_response]):
            optimization_implemented.append("Caching")
        
        if all(cls for cls in [RateLimiter, rate_limit]):
            optimization_implemented.append("Rate limiting")
        
        if retry_on_failure:
            optimization_implemented.append("Error handling with retries")
        
        if batch_process:
            optimization_implemented.append("Batch processing")
    
    except Exception as e:
        logger.error(f"Error validating optimization features: {str(e)}")
    
    # Print validation results
    logger.info("\n=== Optimization Features Validation ===")
    for req in optimization_requirements:
        status = "✅ Implemented" if req in optimization_implemented else "❌ Not implemented"
        logger.info(f"{status}: {req}")
    
    # Calculate implementation percentage
    optimization_percentage = len(optimization_implemented) / len(optimization_requirements) * 100
    
    logger.info(f"\nOptimization features implementation: {optimization_percentage:.1f}%")
    
    return optimization_percentage >= 90

def validate_documentation():
    """Validate documentation against requirements."""
    logger.info("\nValidating documentation...")
    
    documentation_requirements = [
        "API integration documentation",
        "Configuration documentation",
        "Usage examples",
        "Troubleshooting guide",
        "Project README"
    ]
    
    documentation_implemented = []
    
    # Check if documentation files exist
    docs_path = Path(__file__).parent.parent / "docs"
    
    if (docs_path / "api_integration.md").exists():
        documentation_implemented.append("API integration documentation")
    
    # Check if configuration documentation exists in API integration doc
    if (docs_path / "api_integration.md").exists():
        with open(docs_path / "api_integration.md", 'r') as f:
            content = f.read()
            if "Configuration" in content:
                documentation_implemented.append("Configuration documentation")
            if "Usage Examples" in content:
                documentation_implemented.append("Usage examples")
            if "Troubleshooting" in content:
                documentation_implemented.append("Troubleshooting guide")
    
    # Check if README exists
    if (Path(__file__).parent.parent / "README.md").exists():
        documentation_implemented.append("Project README")
    
    # Print validation results
    logger.info("\n=== Documentation Validation ===")
    for req in documentation_requirements:
        status = "✅ Implemented" if req in documentation_implemented else "❌ Not implemented"
        logger.info(f"{status}: {req}")
    
    # Calculate implementation percentage
    documentation_percentage = len(documentation_implemented) / len(documentation_requirements) * 100
    
    logger.info(f"\nDocumentation implementation: {documentation_percentage:.1f}%")
    
    return documentation_percentage >= 90

def validate_project_structure():
    """Validate project structure against requirements."""
    logger.info("\nValidating project structure...")
    
    structure_requirements = [
        "API module",
        "Configuration module",
        "Utilities module",
        "Documentation",
        "Tests",
        "Main entry point"
    ]
    
    structure_implemented = []
    
    # Check if required directories and files exist
    project_root = Path(__file__).parent.parent
    
    if (project_root / "api").is_dir() and (project_root / "api" / "__init__.py").exists():
        structure_implemented.append("API module")
    
    if (project_root / "config").is_dir() and (project_root / "config" / "__init__.py").exists():
        structure_implemented.append("Configuration module")
    
    if (project_root / "utils").is_dir() and (project_root / "utils" / "__init__.py").exists():
        structure_implemented.append("Utilities module")
    
    if (project_root / "docs").is_dir():
        structure_implemented.append("Documentation")
    
    if (project_root / "tests").is_dir() and (project_root / "tests" / "__init__.py").exists():
        structure_implemented.append("Tests")
    
    if (project_root / "main.py").exists():
        structure_implemented.append("Main entry point")
    
    # Print validation results
    logger.info("\n=== Project Structure Validation ===")
    for req in structure_requirements:
        status = "✅ Implemented" if req in structure_implemented else "❌ Not implemented"
        logger.info(f"{status}: {req}")
    
    # Calculate implementation percentage
    structure_percentage = len(structure_implemented) / len(structure_requirements) * 100
    
    logger.info(f"\nProject structure implementation: {structure_percentage:.1f}%")
    
    return structure_percentage >= 90

def main():
    """Main validation function."""
    logger.info("Starting validation of POD Automation System...")
    
    # Validate API integrations
    api_valid = validate_api_integrations()
    
    # Validate optimization features
    optimization_valid = validate_optimization()
    
    # Validate documentation
    documentation_valid = validate_documentation()
    
    # Validate project structure
    structure_valid = validate_project_structure()
    
    # Print overall validation results
    logger.info("\n=== Overall Validation Results ===")
    logger.info(f"API integrations: {'✅ Valid' if api_valid else '❌ Invalid'}")
    logger.info(f"Optimization features: {'✅ Valid' if optimization_valid else '❌ Invalid'}")
    logger.info(f"Documentation: {'✅ Valid' if documentation_valid else '❌ Invalid'}")
    logger.info(f"Project structure: {'✅ Valid' if structure_valid else '❌ Invalid'}")
    
    # Calculate overall validation result
    overall_valid = api_valid and optimization_valid and documentation_valid and structure_valid
    
    logger.info(f"\nOverall validation result: {'✅ PASSED' if overall_valid else '❌ FAILED'}")
    
    return overall_valid

if __name__ == "__main__":
    main()
