#!/bin/bash
# Production deployment script for POD Automation System
# This script builds and deploys the production environment

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== POD Automation System - Production Deployment ===${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}Warning: .env file not found. Make sure your environment variables are configured.${NC}"
    read -p "Continue without .env file? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment aborted."
        exit 1
    fi
fi

echo "Building production Docker image..."

# Build the production Docker image
docker build -t pod-automation-prod .

if [ $? -ne 0 ]; then
    echo -e "${RED}Error building Docker image. See above for details.${NC}"
    exit 1
fi

echo -e "${GREEN}Starting production environment...${NC}"

# Start the production containers
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${RED}Error starting production environment. See above for details.${NC}"
    exit 1
fi

echo -e "${GREEN}Production environment deployed successfully!${NC}"
echo -e "Streamlit dashboard is running at: ${YELLOW}http://localhost:8501${NC}"
echo ""
echo "Production Environment Management:"
echo "- View logs with: docker-compose -f docker-compose.yml -f docker-compose.prod.yml logs -f"
echo "- Check container status: docker-compose -f docker-compose.yml -f docker-compose.prod.yml ps"
echo "- Stop the environment: docker-compose -f docker-compose.yml -f docker-compose.prod.yml down"
echo ""
echo -e "${YELLOW}Important Security Notes:${NC}"
echo "- Make sure your API keys and secrets are properly secured"
echo "- The production environment uses a read-only filesystem with specific writable paths"
echo "- Resource limits are set to prevent container resource exhaustion"
echo ""
echo -e "${GREEN}Deployment complete!${NC}"
