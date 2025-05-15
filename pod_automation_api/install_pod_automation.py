"""
Script to install the pod_automation module in the site-packages directory.
This script will copy the entire pod_automation directory to the site-packages directory.
"""

import os
import sys
import site
import shutil
import importlib

# Get the site-packages directory
site_packages = site.getsitepackages()[0]
print(f"Site packages directory: {site_packages}")

# Possible locations of the pod_automation directory
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

# Destination path in site-packages
pod_automation_site_path = os.path.join(site_packages, "pod_automation")

# Remove existing directory or symlink if it exists
if os.path.exists(pod_automation_site_path):
    print(f"Removing existing pod_automation in site-packages: {pod_automation_site_path}")
    if os.path.islink(pod_automation_site_path):
        os.unlink(pod_automation_site_path)
    else:
        shutil.rmtree(pod_automation_site_path)

# Copy the pod_automation directory to site-packages
print(f"Copying pod_automation from {pod_automation_path} to {pod_automation_site_path}")
try:
    shutil.copytree(pod_automation_path, pod_automation_site_path)
    print(f"Successfully copied pod_automation to site-packages")
except Exception as e:
    print(f"ERROR: Failed to copy pod_automation to site-packages: {e}")
    
    # Try creating a symbolic link instead
    try:
        print(f"Attempting to create symbolic link instead")
        os.symlink(pod_automation_path, pod_automation_site_path)
        print(f"Successfully created symbolic link")
    except Exception as e:
        print(f"ERROR: Failed to create symbolic link: {e}")
        
        # Try adding to Python path directly
        print(f"Adding pod_automation directory to Python path directly")
        if pod_automation_path not in sys.path:
            sys.path.insert(0, pod_automation_path)
            print(f"Added {pod_automation_path} to sys.path")

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
    
    # Try importing from the parent directory
    parent_dir = os.path.dirname(pod_automation_path)
    if parent_dir not in sys.path:
        print(f"Adding parent directory {parent_dir} to sys.path")
        sys.path.insert(0, parent_dir)
    
    try:
        # Clear any previous import attempts
        if 'pod_automation' in sys.modules:
            del sys.modules['pod_automation']
        
        import pod_automation
        print(f"Successfully imported pod_automation after adding parent directory to sys.path")
    except ImportError as e:
        print(f"ERROR: Still failed to import pod_automation: {e}")

print("Installation completed")
