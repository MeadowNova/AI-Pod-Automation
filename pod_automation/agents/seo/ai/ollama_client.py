"""
Client for interacting with Ollama API.

This module provides a client for interacting with the Ollama API to generate text and embeddings.
"""

import requests
import json
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with Ollama API."""

    def __init__(self, base_url="http://localhost:11434", model="qwen3:8b"):
        """Initialize Ollama client.

        Args:
            base_url (str): Base URL for Ollama API
            model (str): Default model to use
        """
        self.base_url = base_url
        self.model = model
        logger.info(f"Initialized Ollama client with model: {model}")

    def generate(self, prompt, system_prompt=None, temperature=0.7):
        """Generate text using Ollama.

        Args:
            prompt (str): User prompt
            system_prompt (str, optional): System prompt
            temperature (float): Temperature for generation

        Returns:
            str: Generated text
        """
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }

        if system_prompt:
            payload["system"] = system_prompt

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
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

    def embed(self, text):
        """Generate embeddings for text.

        Args:
            text (str): Text to embed

        Returns:
            list: Embedding vector
        """
        url = f"{self.base_url}/api/embeddings"

        payload = {
            "model": self.model,
            "prompt": text
        }

        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            return result.get("embedding", [])
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            return []