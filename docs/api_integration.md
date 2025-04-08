# POD Automation System - API Integration Documentation

## Overview

This document provides detailed information about the API integrations implemented for the POD Automation System. The system integrates with Printify and Etsy APIs to automate the creation, publishing, and management of print-on-demand products.

## Table of Contents

1. [Configuration](#configuration)
2. [Printify API Integration](#printify-api-integration)
3. [Etsy API Integration](#etsy-api-integration)
4. [Performance Optimization](#performance-optimization)
5. [Usage Examples](#usage-examples)
6. [Troubleshooting](#troubleshooting)

## Configuration

The system uses a centralized configuration system to manage API keys and other settings. Configuration values are stored securely and can be accessed through the `get_config()` function.

### Setting Up API Keys

Before using the API integrations, you need to set up your API keys:

1. **Printify API Key**: Obtain from your Printify account dashboard
2. **Printify Shop ID**: Found in your Printify shop settings
3. **Etsy API Key**: Obtain from the Etsy Developer Portal
4. **Etsy API Secret**: Obtain from the Etsy Developer Portal

You can set these values using the command-line interface:

```bash
python -m pod_automation.main --setup --printify-key YOUR_PRINTIFY_KEY --printify-shop YOUR_PRINTIFY_SHOP_ID --etsy-key YOUR_ETSY_KEY --etsy-secret YOUR_ETSY_SECRET
```

Or you can run the setup wizard:

```bash
python -m pod_automation.main --setup
```

## Printify API Integration

The Printify API integration allows you to:

- Access the Printify catalog
- Create and manage products
- Publish products to your shop
- Upload images for products
- Manage orders

### Print Providers

The system is configured to work with the following print providers:

- **Monster Digital**: For T-Shirts and Sweatshirts
- **Sensaria**: For Posters
- **MWW**: For pillow cases

### Key Features

- **Authentication**: Secure API key-based authentication
- **Rate Limiting**: Respects Printify's rate limits (600 requests per minute)
- **Error Handling**: Comprehensive error handling with retries
- **Caching**: Caches responses to reduce API calls

### Example Usage

```python
from pod_automation.api import PrintifyAPI

# Initialize API client
printify = PrintifyAPI(api_key="your_api_key", shop_id="your_shop_id")

# Get shop information
shop_info = printify.get_shop()
print(f"Shop: {shop_info.get('title')}")

# Get catalog
catalog = printify.get_catalog(limit=10)
for blueprint in catalog.get('data', []):
    print(f"Blueprint: {blueprint.get('title')}")
```

## Etsy API Integration

The Etsy API integration allows you to:

- Authenticate with OAuth 2.0
- Create and manage listings
- Upload images for listings
- Manage inventory and variations
- Access shop statistics

### Key Features

- **OAuth 2.0 Authentication**: Secure token-based authentication
- **Token Refresh**: Automatic refresh of expired tokens
- **Rate Limiting**: Respects Etsy's rate limits
- **Error Handling**: Comprehensive error handling with retries
- **Caching**: Caches responses to reduce API calls

### Example Usage

```python
from pod_automation.api import EtsyAPI

# Initialize API client
etsy = EtsyAPI(
    api_key="your_api_key",
    api_secret="your_api_secret",
    shop_id="your_shop_id"
)

# Start OAuth flow if needed
if not etsy.access_token:
    etsy.start_oauth_flow()

# Get shop information
shop_info = etsy.get_shop()
print(f"Shop: {shop_info.get('shop_name')}")

# Get listings
listings = etsy.get_listings(limit=10)
for listing in listings.get('results', []):
    print(f"Listing: {listing.get('title')}")
```

## Performance Optimization

The API integrations include several performance optimizations:

### Caching

API responses are cached to reduce the number of API calls:

```python
from pod_automation.utils import cache_api_response

@cache_api_response(ttl=3600)  # Cache for 1 hour
def get_data():
    # Make API call
    return data
```

### Rate Limiting

API calls are rate-limited to prevent hitting API rate limits:

```python
from pod_automation.utils import rate_limit

@rate_limit(calls_per_minute=60)
def make_api_call():
    # Make API call
    return response
```

### Retries

API calls are automatically retried on failure:

```python
from pod_automation.utils import retry_on_failure

@retry_on_failure(max_retries=3, backoff_factor=2)
def make_api_call():
    # Make API call that might fail
    return response
```

### Batch Processing

Large operations are processed in batches:

```python
from pod_automation.utils import batch_process

@batch_process(batch_size=10, delay_between_batches=1)
def process_items(items):
    # Process items in batches
    return results
```

### Optimizing API Clients

You can apply all optimizations to an API client:

```python
from pod_automation.utils import optimize_api_client
from pod_automation.api import PrintifyAPI

printify = PrintifyAPI(api_key="your_api_key", shop_id="your_shop_id")
optimized_printify = optimize_api_client(
    printify,
    cache_ttl=3600,
    rate_limit_calls=60,
    max_retries=3
)
```

## Usage Examples

### Creating a Product on Printify and Publishing to Etsy

```python
from pod_automation.api import PrintifyAPI, EtsyAPI
from pod_automation.utils import optimize_api_client
import base64

# Initialize API clients
printify = optimize_api_client(PrintifyAPI(api_key="your_printify_key", shop_id="your_printify_shop_id"))
etsy = optimize_api_client(EtsyAPI(api_key="your_etsy_key", api_secret="your_etsy_secret", shop_id="your_etsy_shop_id"))

# Ensure Etsy authentication
if not etsy.access_token:
    etsy.start_oauth_flow()

# 1. Upload image to Printify
with open("design.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode("utf-8")

image_response = printify.upload_image({
    "file_name": "design.png",
    "contents": image_data
})

# 2. Create product on Printify
product_data = {
    "title": "Cat T-Shirt",
    "description": "Adorable cat t-shirt for cat lovers",
    "blueprint_id": "5d39b76eb2e9a90016473cd1",  # T-shirt blueprint ID
    "print_provider_id": 29,  # Monster Digital
    "variants": [
        {
            "id": 12345,
            "price": 2499,  # $24.99
            "is_enabled": True
        }
    ],
    "print_areas": [
        {
            "variant_ids": [12345],
            "placeholders": [
                {
                    "position": "front",
                    "images": [
                        {
                            "id": image_response["id"],
                            "x": 0.5,
                            "y": 0.5,
                            "scale": 1,
                            "angle": 0
                        }
                    ]
                }
            ]
        }
    ]
}

product = printify.create_product(product_data)

# 3. Publish product to Printify shop
printify.publish_product(product["id"])

# 4. Create listing on Etsy
listing_data = {
    "quantity": 999,
    "title": "Cat T-Shirt - Perfect Gift for Cat Lovers",
    "description": "Adorable cat t-shirt for cat lovers. Made with high-quality materials.",
    "price": {
        "amount": 2999,  # $29.99
        "currency_code": "USD"
    },
    "who_made": "i_did",
    "when_made": "made_to_order",
    "taxonomy_id": 1234,  # Clothing category
    "type": "physical",
    "shipping_profile_id": 5678,
    "tags": ["cat", "t-shirt", "pet", "animal", "gift", "cat lover"],
    "materials": ["cotton", "polyester"],
    "shop_section_id": 9012,
    "is_customizable": False,
    "is_digital": False,
    "processing_min": 1,
    "processing_max": 3,
    "production_partner_ids": []
}

etsy_listing = etsy.create_draft_listing(listing_data)

# 5. Upload image to Etsy listing
with open("design.png", "rb") as f:
    etsy_image_data = base64.b64encode(f.read()).decode("utf-8")

etsy.upload_listing_image(
    etsy_listing["listing_id"],
    {
        "image": etsy_image_data,
        "file_name": "design.png"
    }
)

print(f"Product created on Printify: {product['id']}")
print(f"Listing created on Etsy: {etsy_listing['listing_id']}")
```

## Troubleshooting

### Common Issues

#### Authentication Errors

- **Printify**: Ensure your API key is correct and has the necessary permissions
- **Etsy**: If OAuth flow fails, try running it again or check your API key and secret

#### Rate Limiting

If you encounter rate limiting errors:

1. Reduce the frequency of API calls
2. Use the optimization utilities to handle rate limiting automatically
3. Implement exponential backoff for retries

#### API Changes

If you encounter unexpected errors:

1. Check the official API documentation for changes
2. Update the API client implementation if necessary
3. Report issues to the development team

### Logging

The system uses Python's logging module to log API calls and errors. You can configure the logging level:

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

For more detailed logging, set the level to `logging.DEBUG`.

### Validation

You can validate your API connections using the validation tool:

```bash
python -m pod_automation.main --validate
```

This will test the connections to both Printify and Etsy APIs and report any issues.
