"""
Script to create a proper Python package for pod_automation.
This script will create a setup.py file and install the package in development mode.
"""

import os
import sys
import subprocess
import tempfile

# Find the pod_automation directory
locations_to_check = [
    "/pod_automation",
    "/app/pod_automation",
    os.path.join(os.getcwd(), "pod_automation"),
    os.path.join(os.path.dirname(os.getcwd()), "pod_automation")
]

# Find the pod_automation directory
pod_automation_path = None
for location in locations_to_check:
    print(f"Checking location: {location}")
    if os.path.exists(location) and os.path.isdir(location):
        print(f"Found pod_automation directory at: {location}")
        pod_automation_path = location
        break

# If not found in the standard locations, search the entire filesystem
if pod_automation_path is None:
    print("pod_automation directory not found in standard locations, searching the filesystem...")
    for root, dirs, files in os.walk('/app', topdown=True, followlinks=False):
        if 'pod_automation' in dirs:
            potential_path = os.path.join(root, 'pod_automation')
            if os.path.isdir(potential_path) and os.path.exists(os.path.join(potential_path, "__init__.py")):
                print(f"Found pod_automation directory at: {potential_path}")
                pod_automation_path = potential_path
                break

if pod_automation_path is None:
    print("ERROR: Could not find pod_automation directory")
    sys.exit(1)

# Create a temporary setup.py file
with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
    setup_py_path = f.name
    f.write("""
from setuptools import setup, find_packages

setup(
    name="pod_automation",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
)
""")

# Copy the setup.py file to the parent directory of pod_automation
parent_dir = os.path.dirname(pod_automation_path)
setup_py_dest = os.path.join(parent_dir, "setup.py")
try:
    with open(setup_py_path, 'r') as src, open(setup_py_dest, 'w') as dest:
        dest.write(src.read())
    print(f"Created setup.py at {setup_py_dest}")
except Exception as e:
    print(f"ERROR: Failed to copy setup.py to {parent_dir}: {e}")
    sys.exit(1)

# Install the package in development mode
try:
    print(f"Installing pod_automation package in development mode from {parent_dir}")
    subprocess.run([sys.executable, "-m", "pip", "install", "-e", parent_dir], check=True)
    print("Successfully installed pod_automation package")
except subprocess.CalledProcessError as e:
    print(f"ERROR: Failed to install pod_automation package: {e}")
    sys.exit(1)

# Verify the installation
try:
    # Clear any previous import attempts
    if 'pod_automation' in sys.modules:
        print("Removing pod_automation from sys.modules")
        del sys.modules['pod_automation']
    
    # Try importing pod_automation
    import pod_automation
    print(f"Successfully imported pod_automation from {pod_automation.__file__}")
    print(f"pod_automation version: {pod_automation.__version__}")
except ImportError as e:
    print(f"ERROR: Failed to import pod_automation: {e}")
    sys.exit(1)

print("Package creation and installation completed successfully")
