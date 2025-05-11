"""
Batch processor for SEO optimization.

This module provides a batch processor for optimizing multiple listings efficiently.
It uses clustering to group similar listings and processes them in parallel.
"""

import os
import json
import time
import logging
import threading
import concurrent.futures
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
from sklearn.cluster import KMeans

from pod_automation.agents.seo.ai.ollama_client import OllamaClient
from pod_automation.agents.seo.ai.rag_system import RAGSystem

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Batch processor for SEO optimization."""

    def __init__(self, ollama_client, db_client, max_workers=4, cluster_size=5):
        """Initialize batch processor.

        Args:
            ollama_client: Ollama client
            db_client: Database client
            max_workers (int): Maximum number of worker threads
            cluster_size (int): Target size for listing clusters
        """
        self.ollama = ollama_client
        self.db = db_client
        self.max_workers = max_workers
        self.cluster_size = cluster_size
        self.rag = RAGSystem(db_client, ollama_client)

        # Initialize RAG system
        try:
            self.rag.index_keywords()
            logger.info(f"Indexed {len(self.rag.keyword_embeddings)} keywords")
        except Exception as e:
            logger.error(f"Error indexing keywords: {str(e)}")

        logger.info(f"Batch processor initialized with {max_workers} workers")

    def _get_listing_embedding(self, listing):
        """Get embedding for a listing.

        Args:
            listing (dict): Listing data

        Returns:
            list: Embedding vector
        """
        # Create a combined text representation of the listing
        listing_text = f"{listing.get('title_original', '')} {' '.join(listing.get('tags_original', []))}"
        return self.ollama.embed(listing_text)

    def _cluster_listings(self, listings, n_clusters=None):
        """Cluster listings based on embeddings.

        Args:
            listings (list): List of listings
            n_clusters (int, optional): Number of clusters

        Returns:
            dict: Clusters of listings
        """
        if not listings:
            return {}

        # Calculate number of clusters
        if n_clusters is None:
            n_clusters = max(1, len(listings) // self.cluster_size)

        # Get embeddings for all listings
        embeddings = []
        for listing in listings:
            embedding = self._get_listing_embedding(listing)
            if embedding:
                embeddings.append(embedding)
            else:
                # Use a zero vector if embedding fails
                embeddings.append([0.0] * 768)

        # Convert to numpy array
        embeddings_array = np.array(embeddings)

        # Perform clustering
        if len(listings) <= n_clusters:
            # If we have fewer listings than clusters, each listing is its own cluster
            clusters = {i: [listings[i]] for i in range(len(listings))}
        else:
            # Use KMeans clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings_array)

            # Group listings by cluster
            clusters = {}
            for i, label in enumerate(cluster_labels):
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(listings[i])

        return clusters

    def _optimize_listing(self, listing, optimizer):
        """Optimize a single listing.

        Args:
            listing (dict): Listing data
            optimizer: SEO optimizer

        Returns:
            dict: Optimized listing data
        """
        try:
            # Get listing ID
            listing_id = listing.get("id") or listing.get("etsy_listing_id")

            # Check if we have pre-fetched market data
            market_data = listing.pop("_market_data", None)

            # Optimize listing
            if market_data:
                # If we have market data, use it directly to optimize the listing
                # This avoids redundant market data retrieval for each listing in a cluster

                # Extract data
                original_title = listing.get("title_original", "")
                original_tags = listing.get("tags_original", [])
                original_description = listing.get("description_original", "")
                base_keyword = listing.get("base_keyword", "")
                product_type = listing.get("product_type", "")

                # If base_keyword or product_type not available, try to extract from title
                if not base_keyword or not product_type:
                    extracted_data = optimizer.extract_keyword_and_product(original_title)

                    if not base_keyword:
                        base_keyword = extracted_data.get("base_keyword", "")

                    if not product_type:
                        product_type = extracted_data.get("product_type", "")

                # Optimize title
                optimized_title = optimizer.optimize_title_ai(listing, market_data)

                # Optimize tags
                optimized_tags = optimizer.optimize_tags_ai(listing, market_data)

                # Optimize description
                optimized_description = optimizer.optimize_description_ai(listing, market_data)

                # Analyze optimization
                analysis = optimizer.analyze_listing(listing)

                # Prepare optimized listing data
                optimized = {
                    'etsy_listing_id': listing_id,
                    'title_original': original_title,
                    'title_optimized': optimized_title,
                    'tags_original': original_tags,
                    'tags_optimized': optimized_tags,
                    'description_original': original_description,
                    'description_optimized': optimized_description,
                    'base_keyword': base_keyword,
                    'product_type': product_type,
                    'status': 'optimized',
                    'optimization_date': datetime.now().isoformat(),
                    'optimization_score': analysis.get('score', 0),
                    'notes': json.dumps(analysis.get('notes', {}))
                }

                return optimized
            else:
                # Use the standard optimization method
                optimized = optimizer.optimize_listing_ai(listing_id, listing)
                return optimized

        except Exception as e:
            logger.error(f"Error optimizing listing {listing.get('id')}: {str(e)}")
            return None

    def _optimize_cluster(self, cluster, optimizer):
        """Optimize a cluster of listings.

        Args:
            cluster (list): Cluster of listings
            optimizer: SEO optimizer

        Returns:
            list: Optimized listings
        """
        optimized_listings = []

        # Find common elements in the cluster to optimize prompts
        common_keywords = set()
        common_product_types = set()

        # First pass: collect common elements
        for listing in cluster:
            # Extract base keyword and product type
            base_keyword = listing.get("base_keyword", "")
            product_type = listing.get("product_type", "")

            # If not available, try to extract from title
            if not base_keyword or not product_type:
                title = listing.get("title_original", "")
                extracted_data = optimizer.extract_keyword_and_product(title)

                if not base_keyword:
                    base_keyword = extracted_data.get("base_keyword", "")

                if not product_type:
                    product_type = extracted_data.get("product_type", "")

            if base_keyword:
                common_keywords.add(base_keyword)

            if product_type:
                common_product_types.add(product_type)

        # Prepare market data for the entire cluster
        market_data = None
        if common_keywords and common_product_types:
            # Use the most common elements to retrieve market data once for the cluster
            query = f"{next(iter(common_keywords))} {next(iter(common_product_types))}"
            market_data = self.rag.retrieve_market_data(query)
            logger.info(f"Retrieved market data for cluster with query: {query}")

        # Second pass: optimize each listing
        for listing in cluster:
            # If we have market data for the cluster, use it
            if market_data:
                # Add the market data to the listing for optimization
                listing["_market_data"] = market_data

            # Optimize the listing
            optimized = self._optimize_listing(listing, optimizer)
            if optimized:
                optimized_listings.append(optimized)

        return optimized_listings

    def optimize_listings(self, listings, optimizer):
        """Optimize multiple listings in parallel.

        Args:
            listings (list): List of listings to optimize
            optimizer: SEO optimizer

        Returns:
            list: Optimized listings
        """
        if not listings:
            return []

        start_time = time.time()
        logger.info(f"Starting batch optimization of {len(listings)} listings")

        # Cluster listings
        clusters = self._cluster_listings(listings)
        logger.info(f"Clustered listings into {len(clusters)} groups")

        # Process each cluster in parallel
        optimized_listings = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit tasks
            future_to_cluster = {
                executor.submit(self._optimize_cluster, cluster, optimizer): i
                for i, cluster in clusters.items()
            }

            # Process results as they complete
            for future in concurrent.futures.as_completed(future_to_cluster):
                cluster_id = future_to_cluster[future]
                try:
                    cluster_results = future.result()
                    optimized_listings.extend(cluster_results)
                    logger.info(f"Completed cluster {cluster_id} with {len(cluster_results)} listings")
                except Exception as e:
                    logger.error(f"Error processing cluster {cluster_id}: {str(e)}")

        end_time = time.time()
        logger.info(f"Completed batch optimization of {len(optimized_listings)} listings in {end_time - start_time:.2f} seconds")

        return optimized_listings

    def get_cache_stats(self):
        """Get embedding cache statistics.

        Returns:
            dict: Cache statistics
        """
        return self.ollama.get_cache_stats()
