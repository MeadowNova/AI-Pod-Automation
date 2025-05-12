"""
Client for interacting with Ollama API.

This module provides a client for interacting with the Ollama API to generate text and embeddings.
It supports using different models for text generation and embeddings, with caching for embeddings.
"""

import requests
import json
import logging
import time
from typing import List, Dict, Any, Optional

from pod_automation.agents.seo.ai.embedding_cache import embedding_cache

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url="http://localhost:11434",
                 generation_model="mistral:latest",
                 embedding_model="nomic-embed-text:latest"):
        """Initialize Ollama client with separate models for generation and embeddings.

        Args:
            base_url (str): Base URL for Ollama API
            generation_model (str): Model to use for text generation
            embedding_model (str): Model to use for embeddings
        """
        self.base_url = base_url
        self.generation_model = generation_model
        self.embedding_model = embedding_model

        # For backward compatibility
        self.model = generation_model

        logger.info(f"Initialized Ollama client with generation model: {generation_model}, embedding model: {embedding_model}")

        # Check if models are available
        self._ensure_models_available()

    def _ensure_models_available(self):
        """Check if the specified models are available and pull them if not."""
        available_models = self.get_available_models()

        # Check generation model
        if self.generation_model not in available_models:
            logger.warning(f"Generation model {self.generation_model} not found in available models")
            if ":" in self.generation_model:  # If it's a specific version
                base_model = self.generation_model.split(":")[0]
                if any(model.startswith(f"{base_model}:") for model in available_models):
                    # Use an available version of the model
                    for model in available_models:
                        if model.startswith(f"{base_model}:"):
                            self.generation_model = model
                            logger.info(f"Using available version of generation model: {model}")
                            break

        # Check embedding model
        if self.embedding_model not in available_models:
            logger.warning(f"Embedding model {self.embedding_model} not found in available models")
            # Try to find an alternative embedding model
            embedding_alternatives = ["nomic-embed-text:latest", "nomic-embed-text", "all-minilm:l6-v2", "e5-small-v2"]
            for alt_model in embedding_alternatives:
                if alt_model in available_models:
                    self.embedding_model = alt_model
                    logger.info(f"Using alternative embedding model: {alt_model}")
                    break

    def generate(self, prompt, system_prompt=None, temperature=0.7):
        """Generate text using Ollama with the generation model.

        Args:
            prompt (str): User prompt
            system_prompt (str, optional): System prompt
            temperature (float): Temperature for generation

        Returns:
            str: Generated text
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.generation_model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            start_time = time.time()
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            end_time = time.time()
            logger.debug(f"Text generation took {end_time - start_time:.2f} seconds")
            return result.get("response", "")
        except Exception as e:
            logger.error(f"Error generating text with Ollama: {str(e)}")
            return ""

    def get_available_models(self):
        """Get list of available models.

        Returns:
            list: List of model names
        """
        url = f"{self.base_url}/api/tags"

        try:
            response = requests.get(url)
            response.raise_for_status()
            result = response.json()
            return [model["name"] for model in result.get("models", [])]
        except Exception as e:
            logger.error(f"Error getting available models: {str(e)}")
            return []

    def embed(self, text, use_cache=True):
        """Generate embeddings for text using the embedding model.

        Args:
            text (str): Text to embed
            use_cache (bool): Whether to use the embedding cache

        Returns:
            list: Embedding vector
        """
        # Check cache first if enabled
        if use_cache:
            cached_embedding = embedding_cache.get(text, self.embedding_model)
            if cached_embedding is not None:
                logger.debug(f"Using cached embedding for text: {text[:30]}...")
                return cached_embedding

        url = f"{self.base_url}/api/embeddings"

        payload = {
            "model": self.embedding_model,
            "prompt": text
        }

        try:
            start_time = time.time()
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            embedding = result.get("embedding", [])
            end_time = time.time()

            generation_time = end_time - start_time
            logger.debug(f"Embedding generation took {generation_time:.2f} seconds")

            # Store in cache if enabled
            if use_cache and embedding:
                embedding_cache.put(text, self.embedding_model, embedding)

            return embedding
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return []

    def get_cache_stats(self):
        """Get embedding cache statistics.

        Returns:
            dict: Cache statistics
        """
        return embedding_cache.get_stats()