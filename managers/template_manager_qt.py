"""
Template management for the Simplified Math Editor (PyQt5 version).

This module provides functionality to handle document templates,
including predefined templates and template insertion.
"""

from pathlib import Path
import os
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QWidget

class TemplateDialog(QDialog):
    """Dialog for selecting and inserting templates"""
    
    def __init__(self, parent=None, templates=None):
        super().__init__(parent)
        self.templates = templates or []
        self.selected_template = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Insert Template")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout(self)
        
        # Template selection label
        layout.addWidget(QLabel("Select a template to insert:"))
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.addItems(self.templates)
        if self.template_list.count() > 0:
            self.template_list.setCurrentRow(0)
        layout.addWidget(self.template_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        insert_button = QPushButton("Insert")
        cancel_button = QPushButton("Cancel")
        insert_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(insert_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Double-click to insert
        self.template_list.itemDoubleClicked.connect(self.accept)
    
    def get_selected_template(self):
        """Get the selected template name"""
        if self.result() == QDialog.Accepted:
            current_item = self.template_list.currentItem()
            if current_item:
                return current_item.text()
        return None

class TemplateManagerQt:
    """Manages document templates for the Simplified Math Editor (PyQt5 version)"""
    
    def __init__(self, app):
        """
        Initialize the template manager
        
        Args:
            app: Reference to the MainWindow instance
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
            tuple: (success, result)
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
            tuple: (success, error_message)
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
        self.app.editor.set_text(template_content)
        
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
        dialog = TemplateDialog(self.app, self.get_template_list())
        if dialog.exec_() == QDialog.Accepted:
            template_name = dialog.get_selected_template()
            if template_name:
                return self.insert_template(template_name)
        return False
    
    def _create_basic_template(self):
        """Create a basic problem template"""
        return """#problem
Problem statement goes here.

#question
Question text goes here.

#solution
Solution text goes here.
"""
    
    def _create_two_equations_template(self):
        """Create a template with two equations"""
        return """#problem
Problem statement goes here.

#question
Question text goes here.

#solution
First equation:
$$
equation_1
$$

Second equation:
$$
equation_2
$$
"""
    
    def _create_image_template(self):
        """Create a template with an image"""
        return """#problem
Problem statement goes here.

#question
Question text goes here.

#solution
Solution text goes here.

\\begin{figure}[h]
    \\centering
    \\includegraphics[width=0.8\\textwidth]{image.png}
    \\caption{Caption text}
    \\label{fig:label}
\\end{figure}
""" 