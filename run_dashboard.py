#!/usr/bin/env python3
"""
Run the POD Automation System dashboard.
"""

import os
import sys
import subprocess

def main():
    """Run the dashboard."""
    try:
        # Check if Streamlit is installed
        try:
            import streamlit
            print("Streamlit is installed.")
        except ImportError:
            print("Streamlit is not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "streamlit"])
            print("Streamlit installed successfully.")
        
        # Run the dashboard
        print("Starting dashboard...")
        subprocess.check_call([
            "streamlit", "run", 
            os.path.join("pod_automation", "ui", "dashboard.py"),
            "--server.port=8501",
            "--server.address=0.0.0.0"
        ])
    except Exception as e:
        print(f"Error running dashboard: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()