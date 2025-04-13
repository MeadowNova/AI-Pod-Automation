#!/bin/bash
# Development script for POD Automation System
# This script builds and runs the development environment

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== POD Automation System - Development Environment ===${NC}"
echo "Building development Docker image..."

# Build the development Docker image
docker build -t pod-automation-dev -f Dockerfile.dev .

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Error building Docker image. See above for details.${NC}"
    exit 1
fi

echo -e "${GREEN}Starting development environment...${NC}"

# Start the development container
docker-compose -f docker-compose.dev.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Error starting development environment. See above for details.${NC}"
    exit 1
fi

echo -e "${GREEN}Development environment started successfully!${NC}"
echo -e "Streamlit dashboard is running at: ${YELLOW}http://localhost:8501${NC}"
echo ""
echo "Development Tips:"
echo "- Your local code is mounted into the container"
echo "- Changes to Python files will automatically reload the application"
echo "- View logs with: docker-compose -f docker-compose.dev.yml logs -f"
echo "- Stop the environment with: docker-compose -f docker-compose.dev.yml down"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
