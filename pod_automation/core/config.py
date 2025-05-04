"""
Configuration management for POD Automation System.
Handles loading, saving, and accessing configuration values.
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Union

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for POD Automation System."""

    def __init__(self, config_path: Optional[str] = None, config_file: Optional[str] = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to configuration file (optional)
            config_file: Alternative name for config_path (for backward compatibility)
        """
        # Handle config_file parameter for backward compatibility
        if config_file and not config_path:
            config_path = config_file

        if config_path:
            self.config_path = config_path
            self.config_dir = os.path.dirname(self.config_path)
            # Create config directory if it doesn't exist and if we're using a directory
            if self.config_dir:
                os.makedirs(self.config_dir, exist_ok=True)
        else:
            # Default config path
            config_dir = os.path.join(os.path.expanduser("~"), ".pod_automation")
            os.makedirs(config_dir, exist_ok=True)
            self.config_path = os.path.join(config_dir, "config.json")
            self.config_dir = config_dir

        self.config: Dict[str, Any] = {}

        # Load configuration
        self.load_config()

    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file.

        Returns:
            Dict containing configuration values
        """
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    self.config = json.load(f)
                logger.info(f"Loaded configuration from {self.config_path}")
            else:
                logger.info(f"Configuration file {self.config_path} not found, using defaults")
                self.config = {}
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.config = {}

        return self.config

    def save_config(self) -> bool:
        """Save configuration to file.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            logger.info(f"Saved configuration to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.

        Args:
            key: Configuration key (dot notation supported)
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        # Handle dot notation (e.g., "api.printify.api_key")
        if "." in key:
            parts = key.split(".")
            current = self.config

            for part in parts[:-1]:
                if part not in current or not isinstance(current[part], dict):
                    return default
                current = current[part]

            return current.get(parts[-1], default)

        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """Set configuration value.

        Args:
            key: Configuration key (dot notation supported)
            value: Configuration value
        """
        # Handle dot notation (e.g., "api.printify.api_key")
        if "." in key:
            parts = key.split(".")
            current = self.config

            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    current[part] = {}

                current = current[part]

            current[parts[-1]] = value
        else:
            self.config[key] = value

    def create_default_config(self) -> None:
        """Create default configuration file."""
        # Create basic config structure
        default_config = {
            'api': {
                'printify': '',
                'etsy': '',
                'openrouter': '',
                'pinterest': ''
            },
            'data_dir': os.path.join(os.path.expanduser('~'), '.pod_automation', 'data')
        }

        # Update config with defaults
        self.config.update(default_config)

        # Save config
        self.save_config()

# Global configuration instance
_config_instance = None

def get_config(config_path: Optional[str] = None) -> Config:
    """Get global configuration instance.

    Args:
        config_path: Path to configuration file (optional)

    Returns:
        Config instance
    """
    global _config_instance

    if _config_instance is None or config_path is not None:
        _config_instance = Config(config_path)

    return _config_instance
