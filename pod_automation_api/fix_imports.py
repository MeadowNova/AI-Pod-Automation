"""
Script to fix imports by creating symbolic links.
Enhanced with additional debugging information.
"""

import os
import site
import sys
import shutil

# Get the site-packages directory
site_packages = site.getsitepackages()[0]
print(f"Site packages directory: {site_packages}")

# Create a symbolic link for pod_automation
pod_automation_path = "/app/pod_automation"
pod_automation_link = os.path.join(site_packages, "pod_automation")

# Check if source directory exists
if os.path.exists(pod_automation_path):
    print(f"Source directory exists: {pod_automation_path}")
    print(f"Source directory contents: {os.listdir(pod_automation_path)}")
else:
    print(f"ERROR: Source directory does not exist: {pod_automation_path}")
    # Try to find pod_automation directory
    print("Searching for pod_automation directory...")
    for root, dirs, files in os.walk('/app', topdown=True, followlinks=False):
        if 'pod_automation' in dirs:
            found_path = os.path.join(root, 'pod_automation')
            print(f"Found potential pod_automation directory at: {found_path}")
            if os.path.isdir(found_path):
                print(f"This is a valid directory with contents: {os.listdir(found_path)}")
                pod_automation_path = found_path
                break

# Check permissions on site-packages directory
try:
    test_file = os.path.join(site_packages, 'test_write_permission.txt')
    with open(test_file, 'w') as f:
        f.write('test')
    os.remove(test_file)
    print(f"Have write permission to site-packages directory: {site_packages}")
except Exception as e:
    print(f"ERROR: Do not have write permission to site-packages directory: {e}")

print(f"Creating symbolic link from {pod_automation_path} to {pod_automation_link}")

# Remove existing link or directory if it exists
if os.path.exists(pod_automation_link):
    print(f"Target already exists: {pod_automation_link}")
    if os.path.islink(pod_automation_link):
        print(f"Target is a symbolic link pointing to: {os.readlink(pod_automation_link)}")
        try:
            os.unlink(pod_automation_link)
            print(f"Removed existing symbolic link: {pod_automation_link}")
        except Exception as e:
            print(f"ERROR: Failed to remove existing symbolic link: {e}")
    else:
        print(f"Target is a directory, attempting to remove it")
        try:
            shutil.rmtree(pod_automation_link)
            print(f"Removed existing directory: {pod_automation_link}")
        except Exception as e:
            print(f"ERROR: Failed to remove existing directory: {e}")

# Create the symbolic link
try:
    os.symlink(pod_automation_path, pod_automation_link)
    print(f"Symbolic link created: {os.path.exists(pod_automation_link)}")
    if os.path.islink(pod_automation_link):
        print(f"Symbolic link points to: {os.readlink(pod_automation_link)}")
except Exception as e:
    print(f"ERROR: Failed to create symbolic link: {e}")
    # If symlink creation fails, try copying the directory instead
    try:
        print(f"Attempting to copy directory instead of creating symlink")
        shutil.copytree(pod_automation_path, pod_automation_link)
        print(f"Directory copied successfully")
    except Exception as e:
        print(f"ERROR: Failed to copy directory: {e}")

# Add pod_automation directory to Python path directly
if pod_automation_path not in sys.path:
    print(f"Adding {pod_automation_path} to sys.path")
    sys.path.insert(0, pod_automation_path)
    print(f"Updated sys.path: {sys.path}")

# Verify the import works
try:
    import pod_automation
    print(f"Successfully imported pod_automation from {pod_automation.__file__}")
except ImportError as e:
    print(f"Failed to import pod_automation: {e}")

    # Try to import using absolute path
    parent_dir = os.path.dirname(pod_automation_path)
    if parent_dir not in sys.path:
        print(f"Adding parent directory {parent_dir} to sys.path")
        sys.path.insert(0, parent_dir)

    try:
        import pod_automation
        print(f"Successfully imported pod_automation after adding parent directory to sys.path")
    except ImportError as e:
        print(f"Still failed to import pod_automation: {e}")

# Check if app module is importable
try:
    import app
    print(f"Successfully imported app module from {app.__file__}")
except ImportError as e:
    print(f"Failed to import app module: {e}")

    # Try to find app directory
    app_path = "/pod_automation_api/app"
    if os.path.exists(app_path):
        print(f"App directory exists at {app_path}")
        if app_path not in sys.path:
            print(f"Adding {app_path} to sys.path")
            sys.path.insert(0, app_path)
            try:
                import app
                print(f"Successfully imported app module after adding to sys.path")
            except ImportError as e:
                print(f"Still failed to import app module: {e}")
    else:
        print(f"App directory not found at {app_path}")
        # Try to find app directory
        for root, dirs, files in os.walk('/app', topdown=True, followlinks=False):
            if 'app' in dirs:
                found_path = os.path.join(root, 'app')
                print(f"Found potential app directory at: {found_path}")
                if os.path.isdir(found_path):
                    print(f"This is a valid directory with contents: {os.listdir(found_path)}")
                    if found_path not in sys.path:
                        print(f"Adding {found_path} to sys.path")
                        sys.path.insert(0, found_path)
                        try:
                            import app
                            print(f"Successfully imported app module after adding to sys.path")
                            break
                        except ImportError as e:
                            print(f"Still failed to import app module: {e}")

print("Import fix script completed")