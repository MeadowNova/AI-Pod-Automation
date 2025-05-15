#!/bin/bash
set -e

# Install missing dependencies
echo "Installing missing dependencies"
pip install pillow numpy pandas matplotlib requests

# Set up Python path
echo "Setting up Python path"
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")

# Create a .pth file to ensure pod_automation is in the Python path
echo "Creating .pth file in $SITE_PACKAGES"
echo "/app" > "$SITE_PACKAGES/pod_automation.pth"
echo "/app/pod_automation" >> "$SITE_PACKAGES/pod_automation.pth"
echo "/pod_automation_api" >> "$SITE_PACKAGES/pod_automation.pth"

# Create symbolic link for pod_automation
echo "Creating symbolic link for pod_automation"
if [ -d "/app/pod_automation" ]; then
  ln -sf /app/pod_automation "$SITE_PACKAGES/pod_automation"
  echo "Created symbolic link from /app/pod_automation to site-packages"
fi

# Try to start the regular application, but fall back to the minimal one if it fails
echo "Starting the application"
if [ "$1" = "uvicorn" ] && [ "$2" = "app.main:app" ]; then
  echo "Attempting to start the regular application"
  uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 || {
    echo "Regular application failed to start, falling back to minimal application"
    exec uvicorn app.main_minimal:app --reload --host 0.0.0.0 --port 8001
  }
else
  # If not starting uvicorn, just run the command as is
  exec "$@"
fi
