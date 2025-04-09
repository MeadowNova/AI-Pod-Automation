"""
Configuration module for POD Automation System.
Handles loading and saving configuration values.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Config:
    """Configuration manager for POD Automation System."""
    
    def __init__(self, config_file=None):
        """Initialize configuration manager.
        
        Args:
            config_file (str, optional): Path to configuration file
        """
        if config_file is None:
            # Use default config file in user's home directory
            self.config_file = os.path.join(str(Path.home()), '.pod_automation_config.json')
        else:
            self.config_file = config_file
        
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from file."""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                logger.debug(f"Loaded configuration from {self.config_file}")
            else:
                logger.debug(f"Configuration file {self.config_file} not found. Using default configuration.")
                self.config = {}
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            self.config = {}
    
    def save_config(self):
        """Save configuration to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(self.config_file)), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.debug(f"Saved configuration to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
            return False
    
    def get(self, key, default=None):
        """Get configuration value.
        
        Args:
            key (str): Configuration key (dot notation supported)
            default: Default value if key not found
            
        Returns:
            Configuration value or default if not found
        """
        # Handle dot notation (e.g., "api.printify.api_key")
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key, value):
        """Set configuration value.
        
        Args:
            key (str): Configuration key (dot notation supported)
            value: Configuration value
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Handle dot notation (e.g., "api.printify.api_key")
        keys = key.split('.')
        config = self.config
        
        # Navigate to the correct nested dictionary
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            elif not isinstance(config[k], dict):
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        return True
    
    def delete(self, key):
        """Delete configuration value.
        
        Args:
            key (str): Configuration key (dot notation supported)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Handle dot notation (e.g., "api.printify.api_key")
        keys = key.split('.')
        config = self.config
        
        # Navigate to the correct nested dictionary
        for k in keys[:-1]:
            if k not in config or not isinstance(config[k], dict):
                return False
            config = config[k]
        
        # Delete the value
        if keys[-1] in config:
            del config[keys[-1]]
            return True
        
        return False

# Singleton instance
_config_instance = None

def get_config(config_file=None):
    """Get configuration manager instance.
    
    Args:
        config_file (str, optional): Path to configuration file
        
    Returns:
        Config: Configuration manager instance
    """
    global _config_instance
    
    if _config_instance is None:
        _config_instance = Config(config_file)
    
    return _config_instance
