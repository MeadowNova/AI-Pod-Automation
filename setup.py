"""
Setup script for POD Automation System.
Handles package installation and configuration.
"""

from setuptools import setup, find_packages

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
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
    ],
    entry_points={
        "console_scripts": [
            "pod-automation=pod_automation.main:main",
        ],
    },
)
