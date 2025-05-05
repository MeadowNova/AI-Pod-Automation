"""
Test script to verify Ollama is properly configured and working.

This script performs basic tests to ensure Ollama is running and can generate responses.
"""

import sys
import requests
import json
import time

def check_ollama_server():
    """Check if Ollama server is running."""
    print("Checking if Ollama server is running...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            print("✅ Ollama server is running")
            return True
        else:
            print(f"❌ Ollama server returned status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Ollama server is not running or not accessible at http://localhost:11434")
        return False
    except Exception as e:
        print(f"❌ Error connecting to Ollama server: {str(e)}")
        return False

def list_available_models():
    """List available models in Ollama."""
    print("\nListing available models...")
    
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            
            if models:
                print(f"Found {len(models)} models:")
                for model in models:
                    print(f"  - {model['name']} (Size: {model.get('size', 'N/A')})")
                return models
            else:
                print("No models found. You may need to pull a model using 'ollama pull <model>'")
                return []
        else:
            print(f"Failed to list models: {response.status_code}")
            return []
    except Exception as e:
        print(f"Error listing models: {str(e)}")
        return []

def test_generation(model_name="llama3"):
    """Test text generation with a specific model."""
    print(f"\nTesting text generation with model '{model_name}'...")
    
    try:
        # Prepare request
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": model_name,
            "prompt": "What are the best practices for Etsy SEO?",
            "stream": False
        }
        
        # Send request
        start_time = time.time()
        response = requests.post(url, json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get("response", "")
            
            print(f"✅ Successfully generated text in {end_time - start_time:.2f} seconds")
            print(f"First 150 characters of response:")
            print("-" * 50)
            print(generated_text[:150] + "..." if len(generated_text) > 150 else generated_text)
            print("-" * 50)
            return True
        else:
            print(f"❌ Failed to generate text: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error generating text: {str(e)}")
        return False

def test_embedding(model_name="llama3"):
    """Test embedding generation with a specific model."""
    print(f"\nTesting embedding generation with model '{model_name}'...")
    
    try:
        # Prepare request
        url = "http://localhost:11434/api/embeddings"
        payload = {
            "model": model_name,
            "prompt": "cat lover t-shirt"
        }
        
        # Send request
        start_time = time.time()
        response = requests.post(url, json=payload)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            embedding = result.get("embedding", [])
            
            print(f"✅ Successfully generated embedding in {end_time - start_time:.2f} seconds")
            print(f"Embedding dimension: {len(embedding)}")
            print(f"First 5 values: {embedding[:5]}")
            return True
        else:
            print(f"❌ Failed to generate embedding: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error generating embedding: {str(e)}")
        return False

def main():
    """Main entry point."""
    print("=" * 50)
    print("OLLAMA CONFIGURATION TEST")
    print("=" * 50)
    
    # Check if Ollama server is running
    server_running = check_ollama_server()
    
    if not server_running:
        print("\n❌ Ollama server is not running. Please start it with 'ollama serve'")
        sys.exit(1)
    
    # List available models
    models = list_available_models()
    
    if not models:
        print("\n❌ No models available. Please pull a model with 'ollama pull llama3'")
        sys.exit(1)
    
    # Select model to test
    default_model = "llama3"
    available_model_names = [model["name"] for model in models]
    
    if default_model in available_model_names:
        test_model = default_model
    else:
        test_model = available_model_names[0]
    
    print(f"\nUsing model '{test_model}' for tests")
    
    # Test text generation
    generation_success = test_generation(test_model)
    
    # Test embedding generation
    embedding_success = test_embedding(test_model)
    
    # Print summary
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    print(f"Ollama Server: {'✅ Running' if server_running else '❌ Not running'}")
    print(f"Available Models: {'✅ ' + str(len(models)) + ' models found' if models else '❌ No models found'}")
    print(f"Text Generation: {'✅ Working' if generation_success else '❌ Failed'}")
    print(f"Embedding Generation: {'✅ Working' if embedding_success else '❌ Failed'}")
    
    if server_running and models and generation_success and embedding_success:
        print("\n✅ All tests passed! Ollama is properly configured and working.")
    else:
        print("\n❌ Some tests failed. Please check the issues above.")

if __name__ == "__main__":
    main()