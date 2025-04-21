#!/bin/bash

# Installation script for POD Automation System
# This script installs all required dependencies and sets up the system

echo "=== POD Automation System Installation ==="
echo "This script will install all required dependencies and set up the system."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Detected Python version: $python_version"

# Check if Python version is at least 3.8
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -lt 3 ] || ([ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]); then
    echo "Error: Python 3.8 or higher is required."
    echo "Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "Python version check passed."
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install required packages
echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Install the package in development mode
echo "Installing POD Automation System..."
pip install -e .

# Create data directories
echo "Creating data directories..."
mkdir -p data/designs
mkdir -p data/mockups
mkdir -p data/trends
mkdir -p data/seo
mkdir -p data/published
mkdir -p data/debug
mkdir -p data/optimization

# Set up configuration
echo "Setting up configuration..."
python -c "from pod_automation.config import Config; Config().create_default_config()"

echo ""
echo "Installation complete!"
echo ""
echo "To start using the POD Automation System:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Set up your API keys: pod-automation --setup"
echo "3. Launch the dashboard: pod-automation --dashboard"
echo ""
echo "For more information, see the documentation in the docs directory."
echo "=== Thank you for installing POD Automation System! ==="
