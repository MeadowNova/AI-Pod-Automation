#!/bin/bash
set -e

echo "Checking pod_automation directory structure"
python /pod_automation_api/check_pod_automation_dir.py

echo "Creating and installing pod_automation package"
python /pod_automation_api/create_package.py

echo "Installing pod_automation module (fallback method)"
python /pod_automation_api/install_pod_automation.py

echo "Setting up Python paths"
python /pod_automation_api/fix_imports.py

# Create a .pth file to ensure pod_automation is in the Python path
SITE_PACKAGES=$(python -c "import site; print(site.getsitepackages()[0])")
echo "Creating .pth file in $SITE_PACKAGES"
echo "/pod_automation" > "$SITE_PACKAGES/pod_automation.pth"
echo "/app" >> "$SITE_PACKAGES/pod_automation.pth"
echo "/pod_automation_api" >> "$SITE_PACKAGES/pod_automation.pth"

# Create symbolic links as a last resort
echo "Creating symbolic links for pod_automation"
if [ -d "/app/pod_automation" ]; then
  ln -sf /app/pod_automation /usr/local/lib/python3.12/site-packages/pod_automation
  echo "Created symbolic link from /app/pod_automation to site-packages"
elif [ -d "/pod_automation" ]; then
  ln -sf /pod_automation /usr/local/lib/python3.12/site-packages/pod_automation
  echo "Created symbolic link from /pod_automation to site-packages"
fi

# Verify imports
echo "Verifying imports"
python -c "import pod_automation; print(f'pod_automation imported from {pod_automation.__file__}')"

# Run the command passed to the script
exec "$@"