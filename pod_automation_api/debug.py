"""
Debug script to test the application startup.
"""

import os
import sys
import importlib

# Print Python path
print("Python path:", sys.path)
print("Current directory:", os.getcwd())

# Try to import the pod_automation module
try:
    import pod_automation
    print("Successfully imported pod_automation")
    print("pod_automation path:", pod_automation.__file__)
except ImportError as e:
    print(f"Failed to import pod_automation: {e}")

# Try to import the app
try:
    from app.main import app
    print("Successfully imported app")
except ImportError as e:
    print(f"Failed to import app: {e}")
    
    # Try to import individual modules to pinpoint the issue
    try:
        import app
        print("Successfully imported app package")
        
        # List all modules in app
        print("app modules:", dir(app))
        
        try:
            import app.main
            print("Successfully imported app.main")
        except ImportError as e:
            print(f"Failed to import app.main: {e}")
    except ImportError as e:
        print(f"Failed to import app package: {e}")

# Try to start the server
try:
    import uvicorn
    print("Starting uvicorn server...")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, log_level="debug")
except Exception as e:
    print(f"Failed to start uvicorn server: {e}")