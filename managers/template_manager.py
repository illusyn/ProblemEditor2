"""
Template management for the Simplified Math Editor.

This module provides functionality to handle document templates,
including predefined templates and template insertion.
"""

import tkinter as tk
from pathlib import Path
import os


class TemplateManager:
    """Manages document templates for the Simplified Math Editor"""
    
    def __init__(self, app):
        """
        Initialize the template manager
        
        Args:
            app: Reference to the MathEditor instance
        """
        self.app = app
        
        # Define built-in templates
        self.templates = {
            "basic": self._create_basic_template(),
            "two_equations": self._create_two_equations_template(),
            "image": self._create_image_template()
        }
        
        # Path to templates directory (for custom templates)
        self.templates_dir = self._get_templates_dir()
        
        # Load custom templates
        self.load_custom_templates()
    
    def _get_templates_dir(self):
        """
        Get the templates directory path
        
        Returns:
            Path: Path to templates directory
        """
        # Create templates directory in user's home directory
        templates_dir = Path.home() / ".simplified_math_editor" / "templates"
        templates_dir.mkdir(parents=True, exist_ok=True)
        return templates_dir
    
    def load_custom_templates(self):
        """Load custom templates from the templates directory"""
        if not self.templates_dir.exists():
            return
            
        for file_path in self.templates_dir.glob("*.md"):
            try:
                template_name = file_path.stem
                with open(file_path, "r", encoding="utf-8") as f:
                    template_content = f.read()
                
                # Add to templates dictionary
                self.templates[template_name] = template_content
            except Exception as e:
                print(f"Error loading template '{file_path.name}': {str(e)}")
    
    def save_custom_template(self, name, content):
        """
        Save a custom template
        
        Args:
            name (str): Template name
            content (str): Template content
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Clean the name (remove special characters, spaces, etc.)
            clean_name = "".join(c for c in name if c.isalnum() or c in "._-")
            
            # Save to file
            file_path = self.templates_dir / f"{clean_name}.md"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Add to templates dictionary
            self.templates[clean_name] = content
            
            return True, file_path
        except Exception as e:
            return False, str(e)
    
    def delete_custom_template(self, name):
        """
        Delete a custom template
        
        Args:
            name (str): Template name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if it's a built-in template
            if name in ["basic", "two_equations", "image"]:
                return False, "Cannot delete built-in templates"
            
            # Check if the template exists
            file_path = self.templates_dir / f"{name}.md"
            if not file_path.exists():
                return False, f"Template '{name}' not found"
            
            # Delete the file
            file_path.unlink()
            
            # Remove from templates dictionary
            if name in self.templates:
                del self.templates[name]
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    def insert_template(self, template_name):
        """
        Insert a template into the editor
        
        Args:
            template_name (str): Name of the template to insert
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if the template exists
        if template_name not in self.templates:
            print(f"Template '{template_name}' not found")
            return False
        
        # Get the template content
        template_content = self.templates[template_name]
        
        # Insert into editor
        self.app.editor.set_content(template_content)
        
        # Update preview
        self.app.update_preview()
        
        return True
    
    def get_template_list(self):
        """
        Get a list of available templates
        
        Returns:
            list: List of template names
        """
        return list(self.templates.keys())
    
    def get_template_content(self, template_name):
        """
        Get the content of a template
        
        Args:
            template_name (str): Name of the template
            
        Returns:
            str: Template content or None if not found
        """
        return self.templates.get(template_name)
    
    def show_template_dialog(self):
        """
        Show a dialog to select and insert a template
        
        Returns:
            bool: True if a template was inserted, False otherwise
        """
        # Create a dialog
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Insert Template")
        dialog.geometry("400x300")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Create variables
        template_var = tk.StringVar()
        
        # Create widgets
        frame = tk.Frame(dialog, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Template selection label
        tk.Label(frame, text="Select a template to insert:").pack(anchor=tk.W, pady=5)
        
        # Template listbox
        template_listbox = tk.Listbox(frame, height=10)
        template_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Populate the listbox
        for template_name in self.get_template_list():
            template_listbox.insert(tk.END, template_name)
        
        # Select the first item
        if template_listbox.size() > 0:
            template_listbox.selection_set(0)
        
        # Result variable
        result = {"cancelled": True}
        
        def on_ok():
            # Get the selected template
            selection = template_listbox.curselection()
            if not selection:
                return
            
            template_name = template_listbox.get(selection[0])
            result["cancelled"] = False
            result["template"] = template_name
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = tk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        insert_button = tk.Button(button_frame, text="Insert", command=on_ok)
        insert_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = tk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Double-click to insert
        template_listbox.bind("<Double-Button-1>", lambda e: on_ok())
        
        # Wait for dialog to close
        self.app.root.wait_window(dialog)
        
        if result["cancelled"]:
            return False
        
        # Insert the selected template
        return self.insert_template(result["template"])
    
    def _create_basic_template(self):
        """
        Create a basic problem template
        
        Returns:
            str: Template content
        """
        return """#problem
Solve the following equation:

#eq
2x + 3 = 7

#question
What is the value of x?
"""
    
    def _create_two_equations_template(self):
        """
        Create a two equations problem template
        
        Returns:
            str: Template content
        """
        return """#problem
Solve the system of equations:

#eq
3x + 2y = 12

#eq
x - y = 1

#question
Find the values of x and y.
"""
    
    def _create_image_template(self):
        """
        Create a problem with image template
        
        Returns:
            str: Template content
        """
        return """#problem
Consider the triangle shown in the figure:

[Insert figure reference here]

#question
Calculate the area of the triangle.
"""
    
    def insert_basic_template(self):
        """Insert a basic problem template"""
        return self.insert_template("basic")
    
    def insert_two_equations_template(self):
        """Insert a two equations problem template"""
        return self.insert_template("two_equations")
    
    def insert_image_template(self):
        """Insert a problem with image template"""
        return self.insert_template("image")