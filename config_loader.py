"""
Configuration loader for the Simplified Math Editor.

This module provides functionality to load and parse JSON configuration files
for the custom markdown system.
"""

import json
import os
from pathlib import Path
import copy
import re

class ConfigLoader:
    """Loads and manages configuration for the custom markdown system"""
    
    def __init__(self, config_file=None):
        """
        Initialize the configuration loader
        
        Args:
            config_file (str, optional): Path to the configuration file.
                If None, a default configuration will be used.
        """
        # System-level defaults (base configuration)
        self.system_config = {
            "variables": {
                "default_format": "\\medskip\\mydefaultsize"
            },
            "commands": {
                "problem": {
                    "description": "Problem section",
                    "parameters": {
                        
                    },
                    "latex_template": "$variables.default_format$\n#CONTENT#"  
                },
                "solution": {
                    "description": "Solution section",
                    "parameters": {},
                    "latex_template": "$variables.default_format$\n\\section*{Solution}"
                },
                "question": {
                    "description": "Question text",
                    "parameters": {},
                    "latex_template": "$variables.default_format$\n#CONTENT#"
                },
                "text": {
                    "description": "Regular text content",
                    "parameters": {},
                    "latex_template": "$variables.default_format$\n#CONTENT#"
                },
                "eq": {
                    "description": "Mathematical equation",
                    "parameters": {
                        "align": {
                            "description": "Text alignment",
                            "type": "string",
                            "default": "left"
                        },
                        "numbering": {
                            "description": "Whether equation is numbered",
                            "type": "boolean",
                            "default": False
                        }
                    },
                    "latex_template": "$variables.default_format$\n$$ #CONTENT# $$"
                },
                "align": {
                    "description": "Aligned equations",
                    "parameters": {},
                    "latex_template": "$variables.default_format$\n\\begin{align*}\n#CONTENT#\n\\end{align*}"
                },
                "config": {
                    "description": "Document-level configuration",
                    "parameters": {},
                    "latex_template": ""  # No output, just updates document configuration
                },
                "bullet": {
                    "description": "Bullet point",
                    "parameters": {},
                    "latex_template": "$variables.default_format$\n\\begin{itemize}\n\\item #CONTENT#\n\\end{itemize}"
                }
            }
        }
        
        # Document-level configuration (from #config blocks)
        self.document_config = {
            "variables": {},
            "commands": {}
        }
        
        # Merged configuration (system + document + runtime)
        self.config = copy.deepcopy(self.system_config)
        
        # Load configuration file if provided (system level)
        if config_file and os.path.exists(config_file):
            self.load_system_config(config_file)
    
    def load_system_config(self, config_file):
        """
        Load system-level configuration from a JSON file
        
        Args:
            config_file (str): Path to the configuration file
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            print(f"ConfigLoader.load_system_config: Loading from {config_file}")
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                
            # Print the loaded config keys
            print(f"ConfigLoader.load_system_config: Loaded config keys: {list(user_config.keys() if user_config else [])}")
            
            # Update system variables if present
            if "variables" in user_config:
                print(f"ConfigLoader.load_system_config: Found variables: {list(user_config['variables'].keys())}")
                self.system_config["variables"].update(user_config["variables"])
            
            # Replace system configuration with the loaded one
            if "commands" in user_config:
                print(f"ConfigLoader.load_system_config: Found commands: {list(user_config['commands'].keys())}")
                self.system_config["commands"].update(user_config["commands"])
                
                # Check for text command specifically
                if "text" in user_config["commands"]:
                    print(f"ConfigLoader.load_system_config: Loaded text command config")
            
            # Re-merge configurations
            self._merge_configurations()
            
            # Check final text command config
            if "text" in self.config["commands"]:
                text_cmd = self.config["commands"]["text"]
                print(f"ConfigLoader.load_system_config: Final text command template: {text_cmd.get('latex_template', 'NONE')}")
                print(f"ConfigLoader.load_system_config: Final text command parameters: {text_cmd.get('parameters', {})}")
            
            return True
            
        except Exception as e:
            print(f"Error loading configuration: {str(e)}")
            return False
    
    def set_document_config(self, doc_config):
        """
        Set document-level configuration
        
        Args:
            doc_config (dict): Document configuration
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if "variables" in doc_config:
                self.document_config["variables"] = doc_config["variables"]
                
            if "commands" in doc_config:
                self.document_config["commands"] = doc_config["commands"]
                
            # Re-merge configurations
            self._merge_configurations()
            
            return True
            
        except Exception as e:
            print(f"Error setting document configuration: {str(e)}")
            return False
    
    def _merge_configurations(self):
        """Merge system and document configurations"""
        # Start with a fresh copy of system config
        self.config = copy.deepcopy(self.system_config)
        
        # Add document-level variables
        if "variables" in self.document_config:
            for var_name, var_value in self.document_config["variables"].items():
                self.config["variables"][var_name] = var_value
        
        # Add document-level commands
        if "commands" in self.document_config:
            for cmd_name, cmd_config in self.document_config["commands"].items():
                if cmd_name in self.config["commands"]:
                    # Merge with existing command
                    self._merge_command_config(self.config["commands"][cmd_name], cmd_config)
                else:
                    # Add new command
                    self.config["commands"][cmd_name] = copy.deepcopy(cmd_config)
        
        # Process variable references in all templates
        self._substitute_variables_in_templates()
    
    def _substitute_variables_in_templates(self):
        """Substitute variable references in LaTeX templates"""
        for cmd_name, cmd_config in self.config["commands"].items():
            if "latex_template" in cmd_config:
                template = cmd_config["latex_template"]
                # Pattern for variable references: $variables.name$
                var_pattern = r'\$variables\.([a-zA-Z0-9_]+)\$'
                
                def replace_var(match):
                    var_name = match.group(1)
                    if var_name in self.config["variables"]:
                        return self.config["variables"][var_name]
                    else:
                        print(f"Warning: Variable '{var_name}' not found in configuration")
                        return match.group(0)  # Keep the original reference
                
                # Replace all variable references
                cmd_config["latex_template"] = re.sub(var_pattern, replace_var, template)
    
    def _merge_command_config(self, base_cmd, new_cmd):
        """
        Merge command configurations
        
        Args:
            base_cmd (dict): Base command configuration
            new_cmd (dict): New command configuration
        """
        # Update description if present
        if "description" in new_cmd:
            base_cmd["description"] = new_cmd["description"]
            
        # Update template if present
        if "latex_template" in new_cmd:
            base_cmd["latex_template"] = new_cmd["latex_template"]
        
        # Merge parameters
        if "parameters" in new_cmd:
            if "parameters" not in base_cmd:
                base_cmd["parameters"] = {}
                
            for param_name, param_config in new_cmd["parameters"].items():
                if param_name in base_cmd["parameters"]:
                    # Update existing parameter
                    base_cmd["parameters"][param_name].update(param_config)
                else:
                    # Add new parameter
                    base_cmd["parameters"][param_name] = copy.deepcopy(param_config)
    
    def register_command(self, command_name, description="", parameters=None, template=""):
        """
        Register a new command at runtime
        
        Args:
            command_name (str): Name of the command
            description (str, optional): Command description
            parameters (dict, optional): Command parameters
            template (str, optional): LaTeX template
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create command configuration
            cmd_config = {
                "description": description,
                "parameters": parameters or {},
                "latex_template": template
            }
            
            # Add to document configuration
            if "commands" not in self.document_config:
                self.document_config["commands"] = {}
                
            self.document_config["commands"][command_name] = cmd_config
            
            # Re-merge configurations
            self._merge_configurations()
            
            return True
            
        except Exception as e:
            print(f"Error registering command: {str(e)}")
            return False
    
    def register_variable(self, var_name, var_value):
        """
        Register a new variable at runtime
        
        Args:
            var_name (str): Variable name
            var_value (str): Variable value
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Ensure variables dict exists
            if "variables" not in self.document_config:
                self.document_config["variables"] = {}
                
            # Add or update the variable
            self.document_config["variables"][var_name] = var_value
            
            # Re-merge configurations
            self._merge_configurations()
            
            return True
            
        except Exception as e:
            print(f"Error registering variable: {str(e)}")
            return False
    
    def register_command_from_definition(self, cmd_def):
        """
        Register a new command from a definition structure
        
        Args:
            cmd_def (dict): Command definition with keys:
                - command: Command name
                - parameters: List of parameter names or parameter configs
                - template: LaTeX template
                - description: Optional command description
                
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if "command" not in cmd_def or "template" not in cmd_def:
                print("Command definition must include 'command' and 'template'")
                return False
                
            command_name = cmd_def["command"]
            template = cmd_def["template"]
            description = cmd_def.get("description", "")
            
            # Parse parameters
            parameters = {}
            param_list = cmd_def.get("parameters", [])
            
            if isinstance(param_list, list):
                # Convert list of parameter names to dictionary
                for param in param_list:
                    if isinstance(param, str):
                        # Simple parameter name
                        parameters[param] = {
                            "description": f"{param} parameter",
                            "type": "string",
                            "default": ""
                        }
                    elif isinstance(param, dict) and "name" in param:
                        # Parameter with configuration
                        param_name = param["name"]
                        parameters[param_name] = {
                            "description": param.get("description", f"{param_name} parameter"),
                            "type": param.get("type", "string"),
                            "default": param.get("default", "")
                        }
            elif isinstance(param_list, dict):
                # Already in dictionary format
                parameters = param_list
            
            # Register the command
            return self.register_command(command_name, description, parameters, template)
            
        except Exception as e:
            print(f"Error registering command from definition: {str(e)}")
            return False
    
    def get_command_config(self, command_name):
        """
        Get configuration for a specific command
        
        Args:
            command_name (str): Name of the command
            
        Returns:
            dict: Command configuration or None if not found
        """
        return self.config["commands"].get(command_name, None)
    
    def get_parameter_config(self, command_name, param_name):
        """
        Get configuration for a specific parameter of a command
        
        Args:
            command_name (str): Name of the command
            param_name (str): Name of the parameter
            
        Returns:
            dict: Parameter configuration or None if not found
        """
        cmd_config = self.get_command_config(command_name)
        if cmd_config and "parameters" in cmd_config:
            return cmd_config["parameters"].get(param_name, None)
        return None
    
    def get_parameter_default(self, command_name, param_name):
        """
        Get default value for a parameter
        
        Args:
            command_name (str): Name of the command
            param_name (str): Name of the parameter
            
        Returns:
            any: Default value or None if not found
        """
        param_config = self.get_parameter_config(command_name, param_name)
        if param_config and "default" in param_config:
            return param_config["default"]
        return None
    
    def get_latex_template(self, command_name):
        """
        Get LaTeX template for a command
        
        Args:
            command_name (str): Name of the command
            
        Returns:
            str: LaTeX template or empty string if not found
        """
        cmd_config = self.get_command_config(command_name)
        if cmd_config and "latex_template" in cmd_config:
            return cmd_config["latex_template"]
        return ""
    
    def get_variable(self, var_name, default=""):
        """
        Get the value of a variable
        
        Args:
            var_name (str): Name of the variable
            default (str, optional): Default value if variable not found
            
        Returns:
            str: Variable value or default if not found
        """
        return self.config["variables"].get(var_name, default)
    
    def get_all_commands(self):
        """
        Get all registered commands
        
        Returns:
            dict: Dictionary of all commands
        """
        return self.config["commands"]
    
    def get_all_variables(self):
        """
        Get all registered variables
        
        Returns:
            dict: Dictionary of all variables
        """
        return self.config["variables"]
    
    def export_config(self, file_path=None):
        """
        Export the current configuration to a JSON file
        
        Args:
            file_path (str, optional): Path to save the configuration file
                If None, returns the configuration as a string
                
        Returns:
            str or bool: JSON string if file_path is None, otherwise True if saved successfully
        """
        try:
            config_json = json.dumps(self.config, indent=2)
            
            if file_path:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(config_json)
                return True
            else:
                return config_json
                
        except Exception as e:
            print(f"Error exporting configuration: {str(e)}")
            return False