# Ollama Connection Setup

This document explains how the POD AI Automation system connects to Ollama for AI-powered SEO optimization.

## Overview

The SEO optimization module uses Ollama to run AI models for text generation and embeddings. Specifically, it uses:

- `mistral:latest` for text generation (optimizing titles, descriptions, etc.)
- `nomic-embed-text:latest` for embeddings (used in the RAG system)

## Connection Configuration

The connection to Ollama is configured in the `OllamaClient` class located at:
```
/pod_automation/agents/seo/ai/ollama_client.py
```

### Docker Environment Connection

When running in a Docker container, the Ollama client needs to connect to the Ollama service running on the host machine. This is achieved by using the special DNS name `host.docker.internal`, which Docker provides to allow containers to access services running on the host.

The connection URL is hardcoded in the `OllamaClient` class:
```python
self.base_url = "http://host.docker.internal:11434"  # Force correct URL for Docker environment
```

This ensures that regardless of what URL is passed to the constructor, the client will always use the correct URL to connect to Ollama.

## Troubleshooting

If you encounter issues with the Ollama connection, check the following:

1. **Ensure Ollama is running on the host machine:**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   ```

2. **Verify the models are available:**
   ```bash
   # List available models
   ollama list
   ```

3. **Pull the required models if they're not available:**
   ```bash
   # Pull the required models
   ollama pull mistral:latest
   ollama pull nomic-embed-text:latest
   ```

4. **Check container connectivity:**
   ```bash
   # From inside the API container
   docker exec -it pod-api-dev curl http://host.docker.internal:11434/api/tags
   ```

5. **Run the diagnostic script:**
   ```bash
   # From inside the API container
   docker exec -it pod-api-dev python /app/pod_automation_api/scripts/test_ollama_connection.py
   ```

## Testing SEO Optimization

To test if the SEO optimization is working correctly, run the test script:
```bash
docker exec -it pod-api-dev python /app/pod_automation_api/scripts/test_seo_optimization.py
```

This script tests both single listing optimization and batch optimization to ensure the SEO module is working correctly.

## Environment Variables

The following environment variables are defined in the Docker Compose file but are not actually used since the URL is hardcoded in the `OllamaClient` class:
```yaml
- AI_MODEL_HOST=http://host.docker.internal:11434  # Point to the Ollama service on the host
- AI_MODEL_NAME=mistral:latest  # Specify the preferred model
```

These are kept for reference and potential future use if the hardcoded URL is removed.

## Future Improvements

Potential improvements to the Ollama connection setup:

1. **Make the URL configurable:** Instead of hardcoding the URL, make it configurable through environment variables with the hardcoded URL as a fallback.

2. **Add retry logic:** Implement retry logic with exponential backoff to handle temporary connection issues.

3. **Add connection pooling:** Implement connection pooling to improve performance when making multiple requests to Ollama.

4. **Add health checks:** Implement health checks to verify that Ollama is running and the required models are available before starting the API server.

5. **Add a dedicated Ollama container:** Add a dedicated Ollama container to the Docker Compose file to ensure Ollama is always available when the API server is running.
