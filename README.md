# POD Automation System - README

## Overview

The POD Automation System is a comprehensive solution for automating print-on-demand (POD) product creation, publishing, SEO optimization, and promotion. The system integrates with Printify and Etsy to streamline the entire POD workflow.

## Features

- **API Integrations**: Secure and optimized connections to Printify and Etsy APIs
- **Print Provider Support**: Configured for Monster Digital (T-Shirts/Sweatshirts), Sensaria (Posters), and MWW (pillow cases)
- **Performance Optimization**: Caching, rate limiting, retries, and batch processing
- **Comprehensive Documentation**: Detailed guides for setup and usage

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Printify account with API key
- Etsy account with API key and secret

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pod-automation.git
cd pod-automation
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up API keys:
```bash
python -m pod_automation.main --setup
```

### Validating API Connections

To ensure your API connections are working correctly:

```bash
python -m pod_automation.main --validate
```

## Documentation

Detailed documentation is available in the `docs` directory:

- [API Integration Guide](docs/api_integration.md): Comprehensive guide to the Printify and Etsy API integrations
- [Usage Examples](docs/examples.md): Examples of common workflows

## Project Structure

```
pod_automation/
├── api/                  # API integration modules
│   ├── __init__.py
│   ├── printify_api.py   # Printify API client
│   └── etsy_api.py       # Etsy API client
├── config/               # Configuration management
│   ├── __init__.py
│   └── config.py         # Configuration utilities
├── utils/                # Utility functions
│   ├── __init__.py
│   └── api_optimization.py  # API optimization utilities
├── tests/                # Test modules
│   ├── __init__.py
│   └── test_api_integration.py  # API integration tests
├── docs/                 # Documentation
│   └── api_integration.md  # API integration documentation
└── main.py               # Main entry point
```

## Usage

### Basic Usage

```python
from pod_automation.api import PrintifyAPI, EtsyAPI
from pod_automation.utils import optimize_api_client

# Initialize API clients
printify = optimize_api_client(PrintifyAPI())
etsy = optimize_api_client(EtsyAPI())

# Use the API clients to automate your POD workflow
shop_info = printify.get_shop()
print(f"Connected to Printify shop: {shop_info.get('title')}")
```

### Command-line Interface

```bash
# Set up API connections
python -m pod_automation.main --setup

# Validate API connections
python -m pod_automation.main --validate
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
