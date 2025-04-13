#!/bin/bash
# Script to test the healthcheck endpoint of the POD Automation System

# Default port
PORT=${1:-8501}

echo "Testing healthcheck endpoint on port $PORT..."

# Try to connect to the healthcheck endpoint
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/healthz)

# Check the response
if [ "$response" == "200" ]; then
    echo "✅ Healthcheck passed! The service is running correctly."
    
    # Get the actual response content
    content=$(curl -s http://localhost:$PORT/healthz)
    echo "Response: $content"
    
    exit 0
else
    echo "❌ Healthcheck failed! Response code: $response"
    echo "The service may not be running or the healthcheck endpoint is not accessible."
    echo "Make sure the container is running with: docker-compose ps"
    echo "Check logs with: docker-compose logs pod-automation"
    
    exit 1
fi
