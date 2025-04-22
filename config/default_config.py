"""
Default configuration for POD Automation System.
"""

# Default configuration values
DEFAULT_CONFIG = {
    "api": {
        "printify": {
            "api_key": "",
            "shop_id": "",
            "base_url": "https://api.printify.com/v1"
        },
        "etsy": {
            "api_key": "",
            "api_secret": "",
            "shop_id": "",
            "access_token": "",
            "refresh_token": "",
            "token_expiry": 0,
            "base_url": "https://api.etsy.com/v3"
        },
        "pinterest": {
            "api_key": "",
            "access_token": "",
            "base_url": "https://api.pinterest.com/v5"
        }
    },
    "design": {
        "output_dir": "./designs",
        "mockup_dir": "./mockups",
        "template_dir": "./templates",
        "max_designs_per_run": 10
    },
    "stable_diffusion": {
        "api_key": "",
        "model": "stable-diffusion-xl-1024-v1-0",
        "steps": 30,
        "width": 1024,
        "height": 1024
    },
    "system": {
        "log_level": "INFO",
        "cache_dir": "./cache",
        "temp_dir": "./temp",
        "max_retries": 3,
        "timeout": 30
    }
}
