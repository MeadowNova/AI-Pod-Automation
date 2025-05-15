#!/bin/bash
# Unified development script for POD Automation System
# Runs both frontend and backend concurrently with hot reloading

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== POD Automation System - Unified Development Environment ===${NC}"

# Check if concurrently is installed
if ! command -v concurrently &> /dev/null; then
    echo -e "${YELLOW}concurrently not found. Installing...${NC}"
    npm install -g concurrently
fi

echo -e "${GREEN}Starting development environment...${NC}"
echo -e "${YELLOW}Backend API:${NC} http://localhost:8001"
echo -e "${YELLOW}Frontend:${NC} http://localhost:5173"

# Run backend API and frontend concurrently
concurrently \
    --names "API,FRONTEND" \
    --prefix-colors "blue,green" \
    "cd pod_automation_api && uvicorn app.main:app --reload --host 127.0.0.1 --port 8001" \
    "cd pod_automation_frontend && npm run dev"
