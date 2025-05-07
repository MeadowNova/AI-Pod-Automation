"""
Retrieval-Augmented Generation system for SEO data.

This module provides a RAG system for retrieving and formatting relevant SEO data.
Supports GPU acceleration for vector similarity calculations.
"""

import numpy as np
import torch
from typing import List, Dict, Any, Optional
import logging

from pod_automation.utils.gpu_utils import get_device, to_tensor, batch_process, clear_gpu_memory

logger = logging.getLogger(__name__)

class RAGSystem:
    """Retrieval-Augmented Generation system for SEO data."""

    def __init__(self, db_client, ollama_client, device=None):
        """Initialize RAG system.

        Args:
            db_client: Database client
            ollama_client: Ollama client
            device: PyTorch device to use (None for auto-detection)
        """
        self.db = db_client
        self.ollama = ollama_client
        self.device = get_device() if device is None else device
        self.keyword_embeddings = {}
        self.listing_embeddings = {}
        logger.info(f"Initialized RAG system using device: {self.device}")

    def index_keywords(self):
        """Index keywords from database."""
        logger.info("Indexing keywords")
        keywords = self.db.get_keywords(limit=1000)

        for keyword_data in keywords:
            keyword = keyword_data["keyword"]
            embedding = self.ollama.embed(keyword)
            self.keyword_embeddings[keyword] = {
                "embedding": embedding,
                "data": keyword_data
            }

        logger.info(f"Indexed {len(self.keyword_embeddings)} keywords")

    def index_listings(self, limit=100):
        """Index listings from database.

        Args:
            limit (int): Maximum number of listings to index
        """
        logger.info("Indexing listings")
        listings = self.db.get_listings(limit=limit)

        for listing in listings:
            listing_id = listing["id"]
            # Create a combined text representation of the listing
            listing_text = f"{listing.get('title_original', '')} {listing.get('title_optimized', '')} {' '.join(listing.get('tags_original', []))}"
            embedding = self.ollama.embed(listing_text)
            self.listing_embeddings[listing_id] = {
                "embedding": embedding,
                "data": listing
            }

        logger.info(f"Indexed {len(self.listing_embeddings)} listings")

    def _cosine_similarity(self, vec1, vec2):
        """Calculate cosine similarity between two vectors using GPU if available."""
        if vec1 is None or vec2 is None or len(vec1) == 0 or len(vec2) == 0:
            return 0

        # Convert to PyTorch tensors and move to device
        vec1_tensor = to_tensor(vec1, self.device)
        vec2_tensor = to_tensor(vec2, self.device)

        # Normalize vectors
        vec1_norm = torch.nn.functional.normalize(vec1_tensor.unsqueeze(0), p=2, dim=1)
        vec2_norm = torch.nn.functional.normalize(vec2_tensor.unsqueeze(0), p=2, dim=1)

        # Calculate cosine similarity
        similarity = torch.mm(vec1_norm, vec2_norm.transpose(0, 1)).item()

        return similarity

    def _batch_cosine_similarity(self, query_embedding, embeddings_list, batch_size=1000):
        """Calculate cosine similarity for multiple embeddings in batches.

        Args:
            query_embedding: Query embedding vector
            embeddings_list: List of embedding vectors to compare against
            batch_size: Size of each batch (larger for GPU, smaller for CPU)
        """
        # Adjust batch size based on device
        if self.device.type == 'cuda':
            # Use larger batches for GPU
            batch_size = min(5000, len(embeddings_list)) if batch_size < 1000 else batch_size
        else:
            # Use smaller batches for CPU
            batch_size = min(100, len(embeddings_list))
        if query_embedding is None or embeddings_list is None or len(embeddings_list) == 0:
            return []

        # Convert query to tensor
        query_tensor = to_tensor(query_embedding, self.device)
        query_tensor = torch.nn.functional.normalize(query_tensor.unsqueeze(0), p=2, dim=1)

        similarities = []

        # Process in batches
        for i in range(0, len(embeddings_list), batch_size):
            batch = embeddings_list[i:i+batch_size]

            # Convert batch to tensors - more efficient approach for GPU
            if self.device.type == 'cuda':
                # For GPU: Convert all at once for better parallelism
                valid_batch = [emb for emb in batch if emb]
                if not valid_batch:
                    continue

                # Convert to 2D tensor directly
                batch_matrix = torch.tensor(valid_batch, device=self.device)
                # Normalize all at once
                batch_matrix = torch.nn.functional.normalize(batch_matrix, p=2, dim=1)
            else:
                # For CPU: Original approach
                batch_tensors = [to_tensor(emb, self.device) for emb in batch if emb]
                if not batch_tensors:
                    continue

                batch_matrix = torch.stack([torch.nn.functional.normalize(t.unsqueeze(0), p=2, dim=1) for t in batch_tensors]).squeeze(1)

            # Calculate similarities for the batch
            batch_similarities = torch.mm(query_tensor, batch_matrix.transpose(0, 1)).squeeze(0)

            # Move results back to CPU and convert to list
            similarities.extend(batch_similarities.cpu().tolist())

        return similarities

    def retrieve_relevant_keywords(self, query, top_k=10):
        """Retrieve relevant keywords for a query using GPU acceleration.

        Args:
            query (str): Query text
            top_k (int): Number of results to return

        Returns:
            list: List of relevant keywords with data
        """
        query_embedding = self.ollama.embed(query)

        if not self.keyword_embeddings:
            return []

        # Extract all embeddings
        keywords = list(self.keyword_embeddings.keys())
        embeddings = [self.keyword_embeddings[k]["embedding"] for k in keywords]

        # Calculate similarities in batches
        similarities = self._batch_cosine_similarity(query_embedding, embeddings)

        # Create result list with similarities
        results = []
        for i, (keyword, similarity) in enumerate(zip(keywords, similarities)):
            if i < len(similarities):  # Safety check
                results.append({
                    "keyword": keyword,
                    "similarity": similarity,
                    "data": self.keyword_embeddings[keyword]["data"]
                })

        # Sort by similarity (descending)
        results.sort(key=lambda x: x["similarity"], reverse=True)

        # Clear GPU memory after processing
        clear_gpu_memory()

        # Return top_k results
        return results[:top_k]

    def retrieve_similar_listings(self, query, top_k=5):
        """Retrieve similar listings for a query using GPU acceleration.

        Args:
            query (str): Query text
            top_k (int): Number of results to return

        Returns:
            list: List of similar listings with data
        """
        query_embedding = self.ollama.embed(query)

        if not self.listing_embeddings:
            return []

        # Extract all embeddings
        listing_ids = list(self.listing_embeddings.keys())
        embeddings = [self.listing_embeddings[lid]["embedding"] for lid in listing_ids]

        # Calculate similarities in batches
        similarities = self._batch_cosine_similarity(query_embedding, embeddings)

        # Create result list with similarities
        results = []
        for i, (listing_id, similarity) in enumerate(zip(listing_ids, similarities)):
            if i < len(similarities):  # Safety check
                results.append({
                    "listing_id": listing_id,
                    "similarity": similarity,
                    "data": self.listing_embeddings[listing_id]["data"]
                })

        # Sort by similarity (descending)
        results.sort(key=lambda x: x["similarity"], reverse=True)

        # Clear GPU memory after processing
        clear_gpu_memory()

        # Return top_k results
        return results[:top_k]

    def retrieve_market_data(self, query, keyword_count=10, listing_count=5):
        """Retrieve market data for a query.

        Args:
            query (str): Query text
            keyword_count (int): Number of keywords to retrieve
            listing_count (int): Number of listings to retrieve

        Returns:
            dict: Market data
        """
        keywords = self.retrieve_relevant_keywords(query, keyword_count)
        listings = self.retrieve_similar_listings(query, listing_count)

        return {
            "keywords": keywords,
            "listings": listings
        }

    def format_context(self, keywords, listings):
        """Format retrieved data as context for LLM.

        Args:
            keywords (list): List of relevant keywords
            listings (list): List of similar listings

        Returns:
            str: Formatted context
        """
        context = "## Market Research Data\n\n"

        # Add keyword information
        context += "### Relevant Keywords\n"
        for i, kw in enumerate(keywords, 1):
            keyword_data = kw["data"]
            context += f"{i}. '{kw['keyword']}'\n"
            context += f"   - Search Volume: {keyword_data.get('search_volume', 'N/A')}\n"
            context += f"   - Competition: {keyword_data.get('competition', 'N/A')}/10\n"
            if "category" in keyword_data:
                context += f"   - Category: {keyword_data['category']}\n"

        # Add listing information
        context += "\n### Similar Successful Listings\n"
        for i, listing in enumerate(listings, 1):
            listing_data = listing["data"]
            context += f"{i}. '{listing_data.get('title_original', 'Untitled')}'\n"
            context += f"   - Tags: {', '.join(listing_data.get('tags_original', []))}\n"
            if listing_data.get('optimization_score'):
                context += f"   - Optimization Score: {listing_data['optimization_score']}\n"

        return context