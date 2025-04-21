"""
Configuration manager for the Simplified Math Editor.

This module provides functionality to load, save, and manage
application-level configuration settings.
"""

import json
import os
from pathlib import Path
import tempfile

class ConfigManager:
    """Manages application configuration settings"""
    
    def __init__(self, config_file=None):
        """
        Initialize the configuration manager
        
        Args:
            config_file (str, optional): Path to the configuration file.
                If None, a default location will be used.
        """
        # Default configuration file path
        if config_file is None:
            config_dir = Path.home() / ".simplified_math_editor"
            config_dir.mkdir(exist_ok=True)
            config_file = config_dir / "config.json"
        
        self.config_file = Path(config_file)
        
   
        # In the default_config dictionary:
        self.default_config = {
            "image": {
                "default_max_height": 800,
                "caption_behavior": "none",
                "indent_points": 48  # Add this new option for figure indentation
            },
            "editor": {
                "font_size": 12
            },
            "preview": {
                "font_size": 16,
                "font_family": "Carlito"
            }
        }
        
        # Current configuration
        self.config = self.default_config.copy()
        
        # Load configuration from file if it exists
        self.load_config()
    
    def load_config(self):
        """
        Load configuration from file
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                
                # Merge with default configuration to ensure all keys are present
                self._merge_config(self.config, loaded_config)
                return True
            
            return False
            
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return False
    
    def save_config(self):
        """
        Save configuration to file
        
        Returns:
            bool: True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            self.config_file.parent.mkdir(exist_ok=True)
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
            
            return True
            
        except Exception as e:
            print(f"Error saving configuration: {str(e)}")
            return False
    
    def _merge_config(self, base, overlay):
        """
        Merge overlay configuration into base configuration
        
        Args:
            base (dict): Base configuration
            overlay (dict): Configuration to merge into base
        """
        for key, value in overlay.items():
            if isinstance(value, dict) and key in base and isinstance(base[key], dict):
                # Recursively merge subdictionaries
                self._merge_config(base[key], value)
            else:
                # Set or overwrite value
                base[key] = value
    
    def get_value(self, section, key, default=None):
        """
        Get a configuration value
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            default (any, optional): Default value if not found
            
        Returns:
            any: Configuration value or default
        """
        try:
            return self.config[section][key]
        except (KeyError, TypeError):
            return default
    
    def set_value(self, section, key, value):
        """
        Set a configuration value
        
        Args:
            section (str): Configuration section
            key (str): Configuration key
            value (any): Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section][key] = value
            return True
            
        except Exception:
            return False
    
    def update_config(self, new_config):
        """
        Update the entire configuration
        
        Args:
            new_config (dict): New configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self._merge_config(self.config, new_config)
            return self.save_config()
            
        except Exception as e:
            print(f"Error updating configuration: {str(e)}")
            return False
    
    def reset_to_defaults(self):
        """
        Reset configuration to defaults
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.config = self.default_config.copy()
            return self.save_config()
            
        except Exception as e:
            print(f"Error resetting configuration: {str(e)}")
            return False