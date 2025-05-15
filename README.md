# POD Automation System

A comprehensive solution for automating print-on-demand (POD) product creation, publishing, SEO optimization, and promotion. The system integrates with Printify and Etsy to streamline the entire POD workflow.

## Features

- **Trend Forecasting**: Analyze trending keywords and designs
- **Design Generation**: Generate designs using Stable Diffusion
- **Mockup Creation**: Create product mockups for various POD products
- **SEO Optimization**: Optimize listings for better visibility
- **Publishing**: Publish products to Printify and Etsy
- **Dashboard**: Interactive dashboard for managing the entire workflow
- **API Integrations**: Secure and optimized connections to Printify and Etsy APIs
- **Print Provider Support**: Configured for Monster Digital (T-Shirts/Sweatshirts), Sensaria (Posters), and MWW (pillow cases)
- **Performance Optimization**: Caching, rate limiting, retries, and batch processing

## Getting Started

### Prerequisites

- Python 3.8 or higher (for local development)
- Docker and Docker Compose (for containerized development)
- Printify account with API key
- Etsy account with API key and secret

### Installation

#### Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pod-automation.git
cd pod-automation
```

2. Install the package in development mode:
```bash
pip install -e .
```

3. Set up API keys:
```bash
python -m pod_automation --setup
```

#### Development Environment

#### Unified Development Environment

For a streamlined development experience that runs all components concurrently with hot reloading:

1. Local development (requires Node.js, Python, and their dependencies):
```bash
./dev-unified.sh
```

2. Docker-based development (requires only Docker and Docker Compose):
```bash
./dev-docker-unified.sh
```

Both options will start:
- Backend API at http://localhost:8001
- Frontend at http://localhost:5173

All components feature hot reloading, so changes to your code will be reflected immediately.

#### Docker Production Deployment

For deploying to production with Docker:

1. Configure your production environment variables (API keys, etc.)

2. Deploy using the production configuration:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

3. The production setup includes:
   - Resource limits (CPU and memory)
   - Improved logging configuration
   - Read-only filesystem with specific writable paths
   - Enhanced security settings

4. Monitor the application:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f
```

5. Stop the production environment:
```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml down
```

### Validating API Connections

To ensure your API connections are working correctly:

```bash
python -m pod_automation --validate
```

## Documentation

Detailed documentation is available in the `docs` directory:

- [API Integration Guide](docs/api_integration.md): Comprehensive guide to the Printify and Etsy API integrations
- [Usage Examples](docs/examples.md): Examples of common workflows

## Project Structure

```
pod_automation/
├── __init__.py           # Package initialization
├── main.py               # Main entry point
├── core/                 # Core functionality
│   ├── __init__.py
│   ├── system.py         # Main system class
│   └── config.py         # Configuration management
├── agents/               # Agent components
│   ├── __init__.py
│   ├── trend_forecaster.py
│   ├── prompt_optimizer.py
│   ├── design_generation.py
│   ├── stable_diffusion.py
│   ├── mockup_generator.py
│   ├── publishing_agent.py
│   ├── seo_optimizer.py
│   └── autogen/          # Autogen agents subpackage
│       ├── __init__.py
│       ├── file_tools.py
│       ├── planner_agent.py
│       └── main.py
├── api/                  # API integrations
│   ├── __init__.py
│   ├── printify_api.py   # Printify API client
│   ├── etsy_api.py       # Etsy API client
│   └── pinterest_api.py  # Pinterest API client
├── utils/                # Utility functions
│   ├── __init__.py
│   ├── api_optimization.py  # API optimization utilities
│   └── logging_config.py # Logging configuration
├── dashboard/            # Dashboard functionality
│   ├── __init__.py
│   └── dashboard.py      # Streamlit dashboard
├── data/                 # Data directory
│   ├── designs/          # Design files
│   ├── mockups/          # Mockup files
│   ├── trends/           # Trend data
│   ├── seo/              # SEO data
│   └── published/        # Published product data
└── tests/                # Tests
    ├── __init__.py
    ├── test_api_integration.py
    ├── test_components.py
    └── test_system.py
```

## Usage

### Basic Usage

```python
from pod_automation import PODAutomationSystem

# Initialize the system
system = PODAutomationSystem()

# Run the full pipeline
results = system.run_full_pipeline(
    keyword="cat lover",
    product_types=["t-shirt", "poster"],
    publish=False
)

# Print results
print(f"Designs Generated: {len(results['designs'])}")
total_mockups = sum(len(mockups) for mockups in results['mockups'].values())
print(f"Mockups Created: {total_mockups}")
```

### API Usage

```python
from pod_automation.api import PrintifyAPI, EtsyAPI
from pod_automation.utils import optimize_api_client

# Initialize API clients
printify = optimize_api_client(PrintifyAPI(api_key="your_printify_api_key"))
etsy = optimize_api_client(EtsyAPI(api_key="your_etsy_api_key", api_secret="your_etsy_api_secret"))

# Use the API clients to automate your POD workflow
shop_info = printify.get_shop()
print(f"Connected to Printify shop: {shop_info.get('title')}")
```

### Command-line Interface

```bash
# Set up API connections
python -m pod_automation --setup

# Validate API connections
python -m pod_automation --validate

# Run the full pipeline
python -m pod_automation --run --keyword "cat lover" --products "t-shirt,poster"

# Run the interactive dashboard
python -m pod_automation --dashboard


```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
