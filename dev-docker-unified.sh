#!/bin/bash
# Docker-based unified development script for POD Automation System

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== POD Automation System - Docker Unified Development Environment ===${NC}"
echo "Building development Docker images..."

# Start the development containers
docker-compose -f docker-compose.dev.unified.yml up -d

if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Error starting development environment. See above for details.${NC}"
    exit 1
fi

echo -e "${GREEN}Development environment started successfully!${NC}"
echo -e "Backend API: ${YELLOW}http://localhost:8001${NC}"
echo -e "Frontend: ${YELLOW}http://localhost:5173${NC}"
echo ""
echo "Development Tips:"
echo "- Your local code is mounted into the containers"
echo "- Changes to files will automatically reload the applications"
echo "- View logs with: docker-compose -f docker-compose.dev.unified.yml logs -f"
echo "- Stop the environment with: docker-compose -f docker-compose.dev.unified.yml down"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
