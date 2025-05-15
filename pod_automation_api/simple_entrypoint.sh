#!/bin/bash
set -e

# Install missing dependencies
echo "Installing missing dependencies"
pip install pillow

# Install other potential dependencies that might be needed
echo "Installing other potential dependencies"
pip install numpy pandas matplotlib requests

echo "Running direct fix for pod_automation imports"
python /pod_automation_api/direct_fix.py || true

# Run the command passed to the script even if the fix script fails
echo "Starting the application"
exec "$@"
