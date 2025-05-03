"""
Setup script for POD Automation System.
Handles package installation and configuration.
"""

from setuptools import setup, find_packages
import os

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]

# Read long description from README.md if it exists
long_description = ""
if os.path.exists("README.md"):
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()

setup(
    name="pod-automation",
    version="0.1.0",
    author="POD Automation Team",
    author_email="info@podautomation.com",
    description="Automation system for print-on-demand product creation and management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pod-automation",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pod-automation=pod_automation.main:main",
        ],
    },
)
