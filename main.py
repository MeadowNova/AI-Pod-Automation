#!/usr/bin/env python3
"""
Main entry point for POD Automation System.
This is a simple wrapper that calls the main function from the pod_automation package.
"""

import sys
from pod_automation.pod_automation_system import main

if __name__ == "__main__":
    sys.exit(main())
