"""
Menu manager for the Simplified Math Editor.

This module provides functionality to create and manage application menus.
"""

import tkinter as tk
from tkinter import messagebox


class MenuManager:
    """Manages the application menus for the Simplified Math Editor"""
    
    def __init__(self, app, root):
        """
        Initialize the menu manager
        
        Args:
            app: Reference to the MathEditor instance
            root: Root Tkinter window
        """
        self.app = app
        self.root = root
        self.menubar = tk.Menu(self.root)
        
        # Create all menus
        self.create_file_menu()
        self.create_edit_menu()
        self.create_insert_menu()
        self.create_view_menu()
        self.create_template_menu()
        self.create_image_menu()
        self.create_help_menu()
        
        # Apply the menubar to the root window
        self.root.config(menu=self.menubar)
    
    def create_file_menu(self):
        """Create the File menu"""
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.app.new_file)
        file_menu.add_command(label="Open...", command=self.app.open_file)
        file_menu.add_command(label="Save", command=self.app.save_file)
        file_menu.add_command(label="Save As...", command=self.app.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export to PDF...", command=self.app.export_to_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Preferences...", command=self.app.show_preferences)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="File", menu=file_menu)
    
    def create_edit_menu(self):
        """Create the Edit menu"""
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=lambda: self.app.editor.cut_text())
        edit_menu.add_command(label="Copy", command=lambda: self.app.editor.copy_text())
        edit_menu.add_command(label="Paste", command=lambda: self.app.editor.paste_text())
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
    
    def create_insert_menu(self):
        """Create the Insert menu"""
        insert_menu = tk.Menu(self.menubar, tearoff=0)
        insert_menu.add_command(label="Paste MathML as LaTeX", command=lambda: self.app.editor.paste_mathml())
        insert_menu.add_command(label="Paste LaTeX as Equation", command=lambda: self.app.editor.paste_latex())
        insert_menu.add_command(label="Paste Image as Figure", command=self.app.paste_image)
        insert_menu.add_command(label="Insert Image from File...", command=self.app.insert_image_from_file)
        insert_menu.add_separator()
        
        # Add markdown commands
        insert_menu.add_command(label="Problem Section", command=lambda: self.app.editor.insert_problem_section())
        insert_menu.add_command(label="Solution Section", command=lambda: self.app.editor.insert_solution_section())
        insert_menu.add_command(label="Question", command=lambda: self.app.editor.insert_question())
        insert_menu.add_command(label="Equation", command=lambda: self.app.editor.insert_equation())
        insert_menu.add_command(label="Aligned Equations", command=lambda: self.app.editor.insert_aligned_equations())
        insert_menu.add_command(label="Bullet Point", command=lambda: self.app.editor.insert_bullet_point())
        
        self.menubar.add_cascade(label="Insert", menu=insert_menu)
    
    def create_view_menu(self):
        """Create the View menu"""
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_command(label="Increase Font Size", command=lambda: self.app.editor.increase_font_size())
        view_menu.add_command(label="Decrease Font Size", command=lambda: self.app.editor.decrease_font_size())
        view_menu.add_separator()
        view_menu.add_command(label="Update Preview", command=self.app.update_preview)
        self.menubar.add_cascade(label="View", menu=view_menu)
    
    def create_template_menu(self):
        """Create the Templates menu"""
        template_menu = tk.Menu(self.menubar, tearoff=0)
        template_menu.add_command(label="Basic Problem", command=self.app.insert_basic_template)
        template_menu.add_command(label="Two Equations Problem", command=self.app.insert_two_equations_template)
        template_menu.add_command(label="Problem with Image", command=self.app.insert_image_template)
        self.menubar.add_cascade(label="Templates", menu=template_menu)
    
    def create_image_menu(self):
        """Create the Image menu"""
        image_menu = tk.Menu(self.menubar, tearoff=0)
        image_menu.add_command(label="Adjust Image Size...", command=self.app.adjust_image_size)
        self.menubar.add_cascade(label="Image", menu=image_menu)
    
    def create_help_menu(self):
        """Create the Help menu"""
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="Markdown Syntax", command=self.app.show_markdown_help)
        self.menubar.add_cascade(label="Help", menu=help_menu)

    def get_menubar(self):
        """Get the menubar object for external integration"""
        return self.menubar
    
    def add_database_menu(self, database_menu):
        """Add the database menu to the menubar"""
        self.menubar.add_cascade(label="Database", menu=database_menu)
    
    def update_menus(self):
        """Update menu states based on application state"""
        # This method can be expanded to update menu item states
        # (enabled/disabled) based on the application state
        pass