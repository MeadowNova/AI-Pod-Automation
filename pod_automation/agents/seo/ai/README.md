# AI-Enhanced SEO Optimization

This module provides AI-enhanced SEO optimization for Etsy listings using Ollama and Supabase.

## Overview

The AI-enhanced SEO optimization system extends the base SEO optimizer with AI capabilities, using:

1. **Ollama** for local LLM processing
2. **Supabase** for data storage and retrieval
3. **RAG (Retrieval-Augmented Generation)** for market data analysis

## Components

The system consists of the following components:

1. **Ollama Client** (`ollama_client.py`): Handles interactions with Ollama API
2. **RAG System** (`rag_system.py`): Implements RAG functionality for market data
3. **AI SEO Optimizer** (`ai_seo_optimizer.py`): Extends the base SEO optimizer with AI capabilities
4. **Optimization Tracker** (`optimization_tracker.py`): Tracks and analyzes optimization performance
5. **CLI Interface** (`cli.py`): Provides a command-line interface for the system

## Requirements

- Ollama running locally (default: http://localhost:11434)
- Supabase project with the following tables:
  - `seo_listings`
  - `seo_keywords`
  - `seo_settings`
  - `seo_optimization_history`

## Usage

### Command-Line Interface

The system provides a command-line interface for easy interaction:

```bash
# Optimize a single listing
python -m pod_automation.agents.seo.ai.cli optimize --id 123456789

# Optimize a batch of listings
python -m pod_automation.agents.seo.ai.cli batch --status pending --limit 10

# View optimization details
python -m pod_automation.agents.seo.ai.cli view --id 123456789

# Analyze optimization performance
python -m pod_automation.agents.seo.ai.cli analyze --days 30

# Configure AI settings
python -m pod_automation.agents.seo.ai.cli config --model llama3

# Export optimization data
python -m pod_automation.agents.seo.ai.cli export --output data.json

# Import optimization data
python -m pod_automation.agents.seo.ai.cli import --input data.json
```

### Programmatic Usage

You can also use the system programmatically:

```python
from pod_automation.agents.seo.db import seo_db
from pod_automation.agents.seo.ai.ai_seo_optimizer import AISEOOptimizer
from pod_automation.agents.seo.ai.optimization_tracker import OptimizationTracker

# Initialize optimizer
optimizer = AISEOOptimizer(ollama_model="llama3")

# Optimize a listing
optimized = optimizer.optimize_listing_ai(etsy_listing_id=123456789)

# Track performance
tracker = OptimizationTracker(seo_db)
performance = tracker.get_optimization_performance(listing_id=1)

# Analyze performance trends
trends = tracker.analyze_performance_trends(days=30)
```

## How It Works

1. **Data Retrieval**: The system retrieves listing data from Supabase
2. **Market Analysis**: The RAG system analyzes market data to identify relevant keywords and trends
3. **AI Optimization**: The AI SEO optimizer uses Ollama to generate optimized titles, tags, and descriptions
4. **Performance Tracking**: The optimization tracker records and analyzes optimization performance

## Customization

You can customize the system by:

1. **Changing the Ollama model**: Use a different model for optimization
2. **Adjusting the RAG system**: Modify the retrieval and formatting logic
3. **Extending the optimizer**: Add new optimization methods
4. **Enhancing the tracker**: Add new performance metrics and analysis methods