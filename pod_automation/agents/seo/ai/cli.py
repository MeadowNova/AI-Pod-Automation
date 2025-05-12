"""
Command-line interface for AI-enhanced SEO optimization.

This module provides a CLI for interacting with the AI-enhanced SEO optimization system.
"""

import os
import sys
import json
import logging
import argparse
from datetime import datetime
import time

from pod_automation.agents.seo.db import seo_db
from pod_automation.agents.seo.ai.ai_seo_optimizer import AISEOOptimizer
from pod_automation.agents.seo.ai.optimization_tracker import OptimizationTracker

logger = logging.getLogger(__name__)

def setup_argparse():
    """Set up argument parser.

    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(description='AI-enhanced SEO optimization CLI')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Optimize listing command
    optimize_parser = subparsers.add_parser('optimize', help='Optimize a listing')
    optimize_parser.add_argument('--id', type=int, help='Etsy listing ID')
    optimize_parser.add_argument('--model', default='qwen3:8b', help='Ollama model to use')
    optimize_parser.add_argument('--explain', action='store_true', help='Explain optimization changes')

    # Optimize batch command
    batch_parser = subparsers.add_parser('batch', help='Optimize a batch of listings')
    batch_parser.add_argument('--status', default='pending', help='Status of listings to optimize')
    batch_parser.add_argument('--limit', type=int, default=10, help='Maximum number of listings to optimize')
    batch_parser.add_argument('--model', default='qwen3:8b', help='Ollama model to use')

    # View optimization command
    view_parser = subparsers.add_parser('view', help='View optimization details')
    view_parser.add_argument('--id', type=int, required=True, help='Etsy listing ID')
    view_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

    # Analyze performance command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze optimization performance')
    analyze_parser.add_argument('--days', type=int, default=30, help='Number of days to analyze')
    analyze_parser.add_argument('--format', choices=['text', 'json'], default='text', help='Output format')

    # Configure command
    config_parser = subparsers.add_parser('config', help='Configure AI settings')
    config_parser.add_argument('--model', help='Set default Ollama model')
    config_parser.add_argument('--list-models', action='store_true', help='List available Ollama models')

    # Export command
    export_parser = subparsers.add_parser('export', help='Export optimization data')
    export_parser.add_argument('--output', required=True, help='Output file path')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Output format')
    export_parser.add_argument('--limit', type=int, default=100, help='Maximum number of listings to export')

    # Import command
    import_parser = subparsers.add_parser('import', help='Import optimization data')
    import_parser.add_argument('--input', required=True, help='Input file path')
    import_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Input format')

    return parser

def optimize_listing(args):
    """Optimize a single listing.

    Args:
        args: Command-line arguments
    """
    if not args.id:
        print("Error: Etsy listing ID is required")
        return

    print(f"Optimizing listing {args.id} with model {args.model}...")

    # Initialize optimizer
    optimizer = AISEOOptimizer(ollama_model=args.model)

    # Get listing data
    listing = seo_db.get_listing(args.id)

    if not listing:
        print(f"Error: Listing {args.id} not found")
        return

    # Optimize listing
    optimized = optimizer.optimize_listing_ai(args.id, listing)

    if not optimized:
        print(f"Error: Failed to optimize listing {args.id}")
        return

    print("\nOptimization complete!")
    print(f"Original title: {listing.get('title_original', '')}")
    print(f"Optimized title: {optimized.get('title_optimized', '')}")
    print(f"Original tags: {', '.join(listing.get('tags_original', []))}")
    print(f"Optimized tags: {', '.join(optimized.get('tags_optimized', []))}")

    # Explain optimization if requested
    if args.explain:
        print("\nOptimization explanation:")
        explanation = optimizer.explain_optimization(listing, optimized)
        print(explanation)

def optimize_batch(args):
    """Optimize a batch of listings.

    Args:
        args: Command-line arguments
    """
    print(f"Optimizing up to {args.limit} listings with status '{args.status}'...")

    # Initialize optimizer
    optimizer = AISEOOptimizer(ollama_model=args.model)

    # Get listings
    listings = seo_db.get_listings(status=args.status, limit=args.limit)

    if not listings:
        print(f"No listings found with status '{args.status}'")
        return

    print(f"Found {len(listings)} listings to optimize")

    # Optimize each listing
    successful = 0
    for i, listing in enumerate(listings, 1):
        etsy_id = listing.get('etsy_listing_id')
        print(f"\n[{i}/{len(listings)}] Optimizing listing {etsy_id}...")

        try:
            optimized = optimizer.optimize_listing_ai(etsy_id, listing)

            if optimized:
                print(f"  ✓ Successfully optimized listing {etsy_id}")
                successful += 1
            else:
                print(f"  ✗ Failed to optimize listing {etsy_id}")
        except Exception as e:
            print(f"  ✗ Error optimizing listing {etsy_id}: {str(e)}")

    print(f"\nBatch optimization complete: {successful}/{len(listings)} listings optimized successfully")

def view_optimization(args):
    """View optimization details.

    Args:
        args: Command-line arguments
    """
    # Get listing
    listing = seo_db.get_listing(args.id)

    if not listing:
        print(f"Error: Listing {args.id} not found")
        return

    # Get optimization history
    history = seo_db.get_optimization_history(listing.get('id'))

    # Initialize tracker
    tracker = OptimizationTracker(seo_db)
    performance = tracker.get_optimization_performance(listing.get('id'))

    if args.format == 'json':
        # Output as JSON
        output = {
            'listing': listing,
            'history': history,
            'performance': performance
        }
        print(json.dumps(output, indent=2))
    else:
        # Output as text
        print(f"Listing: {args.id}")
        print(f"Title (original): {listing.get('title_original', '')}")
        print(f"Title (optimized): {listing.get('title_optimized', '')}")
        print(f"Tags (original): {', '.join(listing.get('tags_original', []))}")
        print(f"Tags (optimized): {', '.join(listing.get('tags_optimized', []))}")
        print(f"Status: {listing.get('status', '')}")
        print(f"Optimization date: {listing.get('optimization_date', '')}")
        print(f"Optimization score: {listing.get('optimization_score', '')}")

        if history:
            print("\nOptimization History:")
            for i, entry in enumerate(history, 1):
                print(f"  {i}. {entry.get('optimization_date', '')} - {entry.get('optimization_type', '')}")
                if 'performance_metrics' in entry and entry['performance_metrics']:
                    metrics = entry['performance_metrics']
                    print(f"     Metrics: {', '.join([f'{k}: {v}' for k, v in metrics.items()])}")

def analyze_performance(args):
    """Analyze optimization performance.

    Args:
        args: Command-line arguments
    """
    print(f"Analyzing optimization performance for the last {args.days} days...")

    # Initialize tracker
    tracker = OptimizationTracker(seo_db)

    # Analyze performance trends
    trends = tracker.analyze_performance_trends(days=args.days)

    if args.format == 'json':
        # Output as JSON
        print(json.dumps(trends, indent=2))
    else:
        # Output as text
        print(f"Status: {trends.get('status', '')}")

        if trends.get('status') == 'success':
            print(f"Total optimizations: {trends.get('total_optimizations', 0)}")
            print(f"Analyzed optimizations: {trends.get('analyzed_optimizations', 0)}")

            if 'average_metrics' in trends:
                print("\nAverage Metrics:")
                for metric, value in trends['average_metrics'].items():
                    print(f"  {metric}: {value}")

            if 'top_performing_listings' in trends:
                print("\nTop Performing Listings:")
                for i, listing in enumerate(trends['top_performing_listings'], 1):
                    print(f"  {i}. Listing {listing.get('etsy_listing_id', '')}")
                    if 'metrics' in listing:
                        metrics = listing['metrics']
                        print(f"     Metrics: {', '.join([f'{k}: {v}' for k, v in metrics.items()])}")
        else:
            print(f"Message: {trends.get('message', '')}")

def configure_ai(args):
    """Configure AI settings.

    Args:
        args: Command-line arguments
    """
    from pod_automation.agents.seo.ai.ollama_client import OllamaClient

    # Initialize Ollama client
    ollama = OllamaClient()

    if args.list_models:
        # List available models
        print("Available Ollama models:")
        models = ollama.get_available_models()

        if models:
            for model in models:
                print(f"  - {model}")
        else:
            print("  No models found or Ollama server not running")

    if args.model:
        # Set default model
        print(f"Setting default Ollama model to {args.model}...")

        # Save to database
        success = seo_db.set_setting(
            'default_ollama_model',
            args.model,
            'Default Ollama model for AI-enhanced SEO optimization'
        )

        if success:
            print(f"Successfully set default model to {args.model}")
        else:
            print(f"Error setting default model")

def export_data(args):
    """Export optimization data.

    Args:
        args: Command-line arguments
    """
    print(f"Exporting optimization data to {args.output}...")

    # Get listings
    listings = seo_db.get_listings(limit=args.limit)

    if not listings:
        print("No listings found")
        return

    print(f"Found {len(listings)} listings to export")

    if args.format == 'json':
        # Export as JSON
        with open(args.output, 'w') as f:
            json.dump(listings, f, indent=2)
    else:
        # Export as CSV
        import csv

        # Determine all possible fields
        fields = set()
        for listing in listings:
            fields.update(listing.keys())

        fields = sorted(list(fields))

        with open(args.output, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()

            for listing in listings:
                # Convert any non-string values to strings
                row = {}
                for field in fields:
                    value = listing.get(field, '')
                    if isinstance(value, (list, dict)):
                        row[field] = json.dumps(value)
                    else:
                        row[field] = value

                writer.writerow(row)

    print(f"Successfully exported {len(listings)} listings to {args.output}")

def import_data(args):
    """Import optimization data.

    Args:
        args: Command-line arguments
    """
    print(f"Importing optimization data from {args.input}...")

    if args.format == 'json':
        # Import from JSON
        with open(args.input, 'r') as f:
            listings = json.load(f)
    else:
        # Import from CSV
        import csv

        listings = []
        with open(args.input, 'r', newline='') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Convert string representations of lists and dicts back to objects
                listing = {}
                for field, value in row.items():
                    if value.startswith('[') or value.startswith('{'):
                        try:
                            listing[field] = json.loads(value)
                        except:
                            listing[field] = value
                    else:
                        listing[field] = value

                listings.append(listing)

    print(f"Found {len(listings)} listings to import")

    # Import each listing
    successful = 0
    for i, listing in enumerate(listings, 1):
        etsy_id = listing.get('etsy_listing_id')
        if not etsy_id:
            print(f"  ✗ Listing {i} has no Etsy listing ID")
            continue

        print(f"  [{i}/{len(listings)}] Importing listing {etsy_id}...")

        try:
            result = seo_db.create_or_update_listing(etsy_id, listing)

            if result:
                print(f"    ✓ Successfully imported listing {etsy_id}")
                successful += 1
            else:
                print(f"    ✗ Failed to import listing {etsy_id}")
        except Exception as e:
            print(f"    ✗ Error importing listing {etsy_id}: {str(e)}")

    print(f"\nImport complete: {successful}/{len(listings)} listings imported successfully")

def main():
    """Main entry point."""
    parser = setup_argparse()
    args = parser.parse_args()

    if args.command == 'optimize':
        optimize_listing(args)
    elif args.command == 'batch':
        optimize_batch(args)
    elif args.command == 'view':
        view_optimization(args)
    elif args.command == 'analyze':
        analyze_performance(args)
    elif args.command == 'config':
        configure_ai(args)
    elif args.command == 'export':
        export_data(args)
    elif args.command == 'import':
        import_data(args)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()