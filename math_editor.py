"""
MathEditor component for the Simplified Math Editor.

This module provides the main application class that integrates
all components and handles the user interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from pathlib import Path
import tempfile
import re
import customtkinter as ctk

from editor import Editor
from preview.latex_compiler import LaTeXCompiler
from preview.pdf_viewer import PDFViewer
from converters.image_converter import ImageConverter
from markdown_parser import MarkdownParser
from db_interface import DatabaseInterface
from managers.config_manager import ConfigManager
from managers.file_manager import FileManager
from managers.image_manager import ImageManager
from managers.template_manager import TemplateManager
from core.preview_manager import PreviewManager
from ui.dialogs.preferences_dialog import PreferencesDialog
from ui.menu_manager import MenuManager
from ui.category_panel import CategoryPanel
from db.math_db import MathProblemDB
from ui.sat_type_panel import SatTypePanel
from ui_qt.style_config import (
    DEFAULT_FONT_FAMILY, DEFAULT_BOLD_FONT_FAMILY, DEFAULT_MONO_FONT_FAMILY,
    DEFAULT_FONT_SIZE, DEFAULT_BOLD_FONT_SIZE, DEFAULT_HEADER_FONT_SIZE,
    DEFAULT_ENTRY_FONT_SIZE, DEFAULT_DOMAIN_BTN_FONT_SIZE,
    LEFT_PANEL_BG, MATH_DOMAINS_BG, MATH_DOMAINS_BTN_BG, MATH_DOMAINS_BTN_HOVER,
    MATH_DOMAINS_BTN_TEXT, BUTTON_BG, BUTTON_HOVER, BUTTON_TEXT, HEADER_TEXT
)

print("DEBUG: math_editor.py loaded")

class MathEditor:
    """Main application class for the Simplified Math Editor"""
    
    def __init__(self, root):
        """
        Initialize the application
        
        Args:
            root: The root Tkinter window
        """
        print("DEBUG: MathEditor __init__ called")
        self.root = root
        self.root.title("Simplified Math Editor")
        # Open in full screen mode
        self.root.state('zoomed')  # For Windows; use self.root.attributes('-fullscreen', True) for cross-platform
        # self.root.attributes('-fullscreen', True)  # Uncomment for true cross-platform fullscreen
        self.root.geometry("2200x1200")  # Restore former width and height
                
        # Initialize result set tracking
        self.current_results = []
        self.current_result_index = -1
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # Apply theme from configuration
        theme = self.config_manager.get_value("appearance", "theme", "light")
        ctk.set_appearance_mode(theme)
        ctk.set_default_color_theme("blue")
        
        # Initialize working directory - use exports folder under dev root instead of temp
        dev_root = Path(__file__).parent
        self.working_dir = dev_root / "exports"
        self.working_dir.mkdir(parents=True, exist_ok=True)
        print(f"MathEditor: Working directory set to {self.working_dir}")
        
        # Create images directory
        image_dir = self.working_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the LaTeX compiler
        self.latex_compiler = LaTeXCompiler(working_dir=str(self.working_dir))
        
        # Initialize the image converter with config_manager
        self.image_converter = ImageConverter(
            working_dir=str(self.working_dir / "images"),
            config_manager=self.config_manager
        )
        
        # Create menu manager (this will create all menus)
        self.menu_manager = MenuManager(self, self.root)
        
        # Store reference to menubar for other components to use
        self.menubar = self.menu_manager.get_menubar()
        
        # Initialize the file manager
        self.file_manager = FileManager(self)
        
        # Initialize the database interface (will set up menu later)
        self.db_interface = DatabaseInterface(self)
        
        # Initialize the database connection
        self.db = MathProblemDB()
        
        # Initialize selected categories list
        self.selected_categories = set()
        
        # Initialize the markdown parser with the config manager and config file
        print("MathEditor: Initializing class-based MarkdownParser")
        self.markdown_parser = MarkdownParser()

        print("MathEditor: MarkdownParser initialized.")
        # Load the LaTeX template
        self.template = self.load_template()
        
        # Set up the UI components
        self.create_layout()
        
        # Create editor component and PDF viewer (needed before preview manager)
        self.editor = Editor(self.editor_frame)
        self.editor.pack(fill=tk.BOTH, expand=True)
        self.pdf_viewer = PDFViewer(self.preview_frame)
        
        # Initialize the template manager
        self.template_manager = TemplateManager(self)
        
        # Initialize the image manager
        self.image_manager = ImageManager(self)
        
        # Initialize the preview manager
        self.preview_manager = PreviewManager(self)
        
        # Set up database menu
        self.db_interface.setup_menu()
        
        # Set up preview context menu
        self.preview_context_menu = self.preview_manager.setup_preview_context_menu()
        
        # Apply editor font size from configuration
        font_size = self.config_manager.get_value("editor", "font_size", 12)
        self.editor.font_size = font_size
        self.editor.editor_font = ('Courier', font_size)
        self.editor.editor.configure(font=self.editor.editor_font)
        
        # Update category display
        self.update_category_display()

        # Force window layout and ensure it is visible
        self.root.update_idletasks()
        self.root.deiconify()

        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)

        print("DEBUG: About to create SAT Problem Types label")
        header_font = ctk.CTkFont(family=DEFAULT_FONT_FAMILY, size=DEFAULT_HEADER_FONT_SIZE, weight="bold")
        print("DEBUG: DEFAULT_HEADER_FONT_SIZE =", DEFAULT_HEADER_FONT_SIZE)
        print("DEBUG: header_font actual size =", header_font.cget('size'))
        ctk.CTkLabel(self.left_panel, text="SAT Problem Types", font=header_font, text_color=HEADER_TEXT).pack(anchor="w", padx=10, pady=(15, 2))

    def set_initial_pane_position(self):
        """Set the initial position of the paned window divider"""
        width = self.root.winfo_width()
        if width > 100:  # Only if the window has been realized
            effective_width = width - 580  # Subtracting new category panel width (550) plus some padding
            # Give 40% to editor, 60% to preview
            self.paned_window.sashpos(0, int(effective_width * 0.37))

    def load_template(self):
        """Load the default LaTeX template"""
        # Look for template in resources directory first
        resources_dir = Path(__file__).parent / "resources"
        template_path = resources_dir / "default_template.tex"
        
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()
                # Check if the template has the necessary packages
                if "\\usepackage{graphicx}" not in template:
                    # Add graphicx package if missing using the direct approach
                    template = template.replace("\\begin{document}", 
                        "\\usepackage{graphicx}\n\\graphicspath{{./}{./images/}}\n\n\\begin{document}")
                elif "\\graphicspath" not in template:
                    # Add graphicspath if missing
                    template = template.replace("\\usepackage{graphicx}", 
                        "\\usepackage{graphicx}\n\\graphicspath{{./}{./images/}}")
                    
                return template
        
        # Fallback to a basic template - use raw string directly from test_math_editor.py
        return r"""\documentclass{exam}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{enumitem}
\usepackage{graphicx}
\graphicspath{{./}{./images/}} 
\setlength{\parindent}{0pt}

\begin{document}

#CONTENT#

\end{document}
"""

    def create_layout(self):
        """Create the main application layout"""
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top toolbar
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Add toolbar buttons
        self.latex_button = ttk.Button(
            self.toolbar,
            text="Paste LaTeX",
            command=lambda: self.editor.paste_latex()
        )
        self.latex_button.pack(side=tk.LEFT, padx=5)
        
        self.image_button = ttk.Button(
            self.toolbar,
            text="Paste Image",
            command=self.paste_image
        )
        self.image_button.pack(side=tk.LEFT, padx=5)
        
        self.file_image_button = ttk.Button(
            self.toolbar,
            text="Insert Image",
            command=self.insert_image_from_file
        )
        self.file_image_button.pack(side=tk.LEFT, padx=5)
        
        # Add markdown-specific buttons
        self.problem_button = ttk.Button(
            self.toolbar,
            text="Problem",
            command=lambda: self.editor.insert_problem_section()
        )
        self.problem_button.pack(side=tk.LEFT, padx=5)
        
        self.solution_button = ttk.Button(
            self.toolbar,
            text="Solution",
            command=lambda: self.editor.insert_solution_section()
        )
        self.solution_button.pack(side=tk.LEFT, padx=5)
        
        self.question_button = ttk.Button(
            self.toolbar,
            text="Question",
            command=lambda: self.editor.insert_question()
        )
        self.question_button.pack(side=tk.LEFT, padx=5)
        
        self.equation_button = ttk.Button(
            self.toolbar,
            text="Equation",
            command=lambda: self.editor.insert_equation()
        )
        self.equation_button.pack(side=tk.LEFT, padx=5)
        
        self.preview_button = ttk.Button(
            self.toolbar,
            text="Update Preview",
            command=self.update_preview
        )
        self.preview_button.pack(side=tk.LEFT, padx=5)
        
        # Add font size buttons to toolbar
        self.font_increase_button = ttk.Button(
            self.toolbar,
            text="A+",
            width=3,
            command=lambda: self.editor.increase_font_size()
        )
        self.font_increase_button.pack(side=tk.LEFT, padx=5)
        
        self.font_decrease_button = ttk.Button(
            self.toolbar,
            text="A-",
            width=3,
            command=lambda: self.editor.decrease_font_size()
        )
        self.font_decrease_button.pack(side=tk.LEFT, padx=5)
        
        # Create a frame for the main content and category panel
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left side panel containing categories, notes, and answer
        self.left_panel = ctk.CTkFrame(self.content_frame, fg_color=LEFT_PANEL_BG, corner_radius=8, width=800)
        self.left_panel.pack_propagate(False)
        self.left_panel.pack(side="left", fill="y", padx=20, pady=20)

        # Larger fonts
        bold_font = ctk.CTkFont(family=DEFAULT_BOLD_FONT_FAMILY, size=DEFAULT_BOLD_FONT_SIZE, weight="bold")
        header_font = ctk.CTkFont(family=DEFAULT_FONT_FAMILY, size=DEFAULT_HEADER_FONT_SIZE, weight="bold")
        entry_font = ctk.CTkFont(family=DEFAULT_FONT_FAMILY, size=DEFAULT_ENTRY_FONT_SIZE)

        print("DEBUG: DEFAULT_HEADER_FONT_SIZE =", DEFAULT_HEADER_FONT_SIZE)
        print("DEBUG: header_font actual size =", header_font.cget('size'))
        ctk.CTkLabel(self.left_panel, text="SAT Problem Types", font=header_font, text_color=HEADER_TEXT).pack(anchor="w", padx=10, pady=(15, 2))
        sat_types_row = ctk.CTkFrame(self.left_panel, fg_color=LEFT_PANEL_BG)
        sat_types_row.pack(anchor="w", padx=10, pady=(0, 10))
        self.sat_type_vars = {}
        for label in ["Efficiency", "Math Concept", "SAT Problem"]:
            var = ctk.StringVar()
            cb = ctk.CTkCheckBox(
                sat_types_row,
                text=label,
                font=bold_font,
                fg_color=BUTTON_BG,
                border_color=BUTTON_HOVER,
                text_color=HEADER_TEXT,
                variable=var,
                onvalue="1",
                offvalue="0"
            )
            cb.pack(side="left", padx=16)
            self.sat_type_vars[label] = var

        # Math Domains (Categories) Section
        ctk.CTkLabel(self.left_panel, text="Math Domains", font=header_font, text_color=HEADER_TEXT).pack(anchor="w", padx=10, pady=(10, 2))
        domains_frame = ctk.CTkFrame(self.left_panel, fg_color=MATH_DOMAINS_BG, corner_radius=8, width=700, height=600)
        domains_frame.pack(padx=10, pady=(0, 10))
        domains_frame.pack_propagate(False)
        self.category_panel = CategoryPanelCTk(domains_frame, on_category_click=self.on_category_click)
        self.category_panel.pack(fill="x", padx=10, pady=10)

        # Notes Section (moved below Math Domains)
        ctk.CTkLabel(self.left_panel, text="Notes", font=header_font, text_color=HEADER_TEXT).pack(anchor="w", padx=10, pady=(10, 2))
        self.notes_text = ctk.CTkTextbox(self.left_panel, width=660, height=140, font=(DEFAULT_FONT_FAMILY, DEFAULT_FONT_SIZE))
        self.notes_text.pack(padx=10, pady=(0, 10), fill="x")
        
        # Create paned window for editor and preview
        self.paned_window = ttk.PanedWindow(self.content_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Editor frame
        self.editor_frame = ttk.Frame(self.paned_window, height=400)  # Less height for editor
        self.editor_frame.pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(self.editor_frame, weight=1)
        
        # Preview frame
        self.preview_frame = ttk.Frame(self.paned_window)
        self.preview_frame.pack(fill=tk.BOTH, expand=True)
        self.paned_window.add(self.preview_frame, weight=2)  # Give preview more weight
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.root, 
            textvariable=self.status_var, 
            relief=tk.SUNKEN, 
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Set initial paned window position (after a delay)
        self.root.after(100, self.set_initial_pane_position)
    
    def update_category_display(self):
        """Update the category panel display"""
        success, categories = self.db.get_categories()
        if success:
            category_names = [cat["name"] for cat in categories]
            self.category_panel.update_display(category_names)
            # Ensure panel's selected categories match editor's
            for cat in category_names:
                self.category_panel.highlight_category(cat, cat in self.selected_categories)
    
    def on_category_click(self, category):
        """
        Handle category button click
        
        Args:
            category: Name of the clicked category
        """
        # Toggle the clicked category in our set
        if category in self.selected_categories:
            self.selected_categories.remove(category)
        else:
            self.selected_categories.add(category)
        
        # Update status bar with selected categories
        if self.selected_categories:
            self.status_var.set(f"Selected categories: {', '.join(sorted(self.selected_categories))}")
        else:
            self.status_var.set("No categories selected")
        
        # Don't auto-load problems on category click - let user explicitly query when ready
        # This prevents unwanted loading after reset or during new problem creation
    
    def load_problem_content(self, problem):
        """
        Load problem content into the editor
        
        Args:
            problem: Problem dictionary containing content and metadata
        """
        # Store the problem ID
        self.current_problem_id = problem.get('problem_id')
        # Set the Problem ID field
        if hasattr(self, 'problem_id_entry'):
            self.problem_id_entry.delete(0, tk.END)
            if self.current_problem_id is not None:
                self.problem_id_entry.insert(0, str(self.current_problem_id))
        # Set the content
        self.editor.set_text(problem.get('content', ''))
        # Set answer and notes
        self.answer_text.delete(0, tk.END)
        self.answer_text.insert(0, problem.get('answer', ''))
        self.notes_text.delete("1.0", tk.END)
        self.notes_text.insert("1.0", problem.get('notes', ''))
        # Clear and set categories
        self.selected_categories.clear()
        if 'categories' in problem and problem['categories']:
            self.selected_categories = {cat['name'] for cat in problem['categories']}
        # Update category panel to reflect the loaded problem's categories
        if hasattr(self, 'category_panel'):
            for cat, btn in self.category_panel.buttons.items():
                if cat in self.selected_categories:
                    self.category_panel.highlight_category(cat, True)
                    self.category_panel.selected_categories.add(cat)
                else:
                    self.category_panel.highlight_category(cat, False)
                    if cat in self.category_panel.selected_categories:
                        self.category_panel.selected_categories.remove(cat)
        # Set SAT types for this problem
        if hasattr(self, 'sat_type_panel'):
            sat_types = []
            if 'problem_id' in problem and problem['problem_id'] is not None:
                success, types = self.db.get_sat_types_for_problem(problem['problem_id'])
                if success:
                    sat_types = [t['name'] for t in types]
            self.sat_type_panel.set_selected_types(sat_types)
        # Update preview
        self.update_preview()
    
    # File operation methods - delegated to FileManager
    def new_file(self):
        """Create a new file - delegate to FileManager"""
        return self.file_manager.new_file()
    
    def open_file(self):
        """Open a file - delegate to FileManager"""
        return self.file_manager.open_file()
    
    def save_file(self):
        # Save the current file - delegate to FileManager
        result = self.file_manager.save_file()
        # Save SAT types for this problem
        if hasattr(self, 'sat_type_panel') and self.current_problem_id is not None:
            # Remove all current associations
            success, types = self.db.get_sat_types_for_problem(self.current_problem_id)
            if success:
                for t in types:
                    self.db.remove_problem_from_sat_type(self.current_problem_id, t['type_id'])
            # Add selected types
            for t in self.sat_type_panel.get_selected_types():
                self.db.add_problem_to_sat_type(self.current_problem_id, t)
        return result
    
    def save_as(self):
        """Save the file with a new name - delegate to FileManager"""
        return self.file_manager.save_as()
    
    def export_to_pdf(self):
        """Export the current document to PDF - delegate to FileManager"""
        return self.file_manager.export_to_pdf()
    
    def check_save_changes(self):
        """Check if there are unsaved changes - delegate to FileManager"""
        return self.file_manager.check_save_changes()
    
    # Preview methods - delegated to PreviewManager
    def update_preview(self):
        """Update the preview - delegate to PreviewManager"""
        return self.preview_manager.update_preview()
    
    def extract_images_for_compilation(self):
        """Extract images for compilation - delegate to PreviewManager"""
        return self.preview_manager.extract_images_for_compilation()
    
    def show_preview_context_menu(self, event):
        """Show preview context menu - delegate to PreviewManager"""
        return self.preview_manager.show_preview_context_menu(event)
    
    # Image management methods - delegated to ImageManager
    def get_clipboard_image(self):
        """Get clipboard image - delegate to ImageManager"""
        return self.image_manager.get_clipboard_image()
    
    def paste_image(self):
        """Paste image from clipboard - delegate to ImageManager"""
        return self.image_manager.paste_image()
    
    def insert_image_from_file(self):
        """Insert image from file - delegate to ImageManager"""
        return self.image_manager.insert_image_from_file()
    
    def get_image_details(self, image_info):
        """Get image details - delegate to ImageManager"""
        return self.image_manager.get_image_details(image_info)
    
    def adjust_image_size(self):
        """Adjust image size - delegate to ImageManager"""
        return self.image_manager.adjust_image_size()
    
    # Template methods - delegated to TemplateManager
    def insert_basic_template(self):
        """Insert basic template - delegate to TemplateManager"""
        return self.template_manager.insert_basic_template()
    
    def insert_two_equations_template(self):
        """Insert two equations template - delegate to TemplateManager"""
        return self.template_manager.insert_two_equations_template()
    
    def insert_image_template(self):
        """Insert image template - delegate to TemplateManager"""
        return self.template_manager.insert_image_template()
    
    def show_preferences(self):
        """Show the preferences dialog"""
        # Create preferences dialog
        PreferencesDialog(
            self.root,
            config=self.config_manager.config,
            on_save=self.apply_preferences
        )

    def apply_preferences(self, new_config):
        """
        Apply new preferences from the preferences dialog
        
        Args:
            new_config (dict): Updated configuration
        """
        # Update configuration
        self.config_manager.update_config(new_config)
        
        # Apply font size to editor
        font_size = self.config_manager.get_value("editor", "font_size", 12)
        self.editor.font_size = font_size
        self.editor.editor_font = ('Courier', font_size)
        self.editor.editor.configure(font=self.editor.editor_font)
        
        # Update tag configurations for styled text
        self.editor.editor.tag_configure("command", font=(self.editor.editor_font[0], font_size, "bold"))
        self.editor.editor.tag_configure("section", font=(self.editor.editor_font[0], font_size, "bold"))
        
        # Reapply syntax highlighting to update styled text
        self.editor.highlight_syntax()
        
        # If preview font settings were changed, refresh the preview
        if "preview" in new_config and ("font_size" in new_config["preview"] or "font_family" in new_config["preview"]):
            # Update preview with new font settings
            self.update_preview()
        
        # Update status
        self.status_var.set("Preferences updated")
    
    def show_markdown_help(self):
        """Show help for markdown syntax"""
        help_text = """
# Custom Markdown Syntax

## Basic Structure
#problem     - Problem section
#solution    - Solution section
#question    - Question text

## Equation Environments
#eq          - Start an equation, put the equation on the next line
#align       - Start an aligned equations environment

## Lists
#bullet      - Create a bullet point item

## Example:
#problem
Solve the equation:

#eq
2x + 3 = 7

#question
What is x?

#solution
We solve step by step:

#eq
2x = 4

#eq
x = 2
"""
        # Create help window
        help_window = tk.Toplevel(self.root)
        help_window.title("Markdown Syntax Help")
        help_window.geometry("600x500")
        
        # Create text widget
        from tkinter import scrolledtext
        text = scrolledtext.ScrolledText(help_window, wrap=tk.WORD, font=('Courier', 12))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Insert help text
        text.insert(tk.END, help_text)
        text.config(state=tk.DISABLED)  # Make read-only
        
        # Close button
        close_button = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_button.pack(pady=10)

    def load_problem_by_id(self):
        """Load a problem using its ID"""
        try:
            problem_id = int(self.problem_id_entry.get())
            success, problem = self.db.get_problem(problem_id)
            
            if not success:
                messagebox.showerror("Error", f"Failed to load problem: {problem}")
                return
            
            # Load the problem content
            self.load_problem_content(problem)
            self.status_var.set(f"Loaded problem #{problem_id}")
            
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid problem ID")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def query_by_categories(self):
        """Query problems based on selected categories"""
        if not self.selected_categories:
            messagebox.showwarning("Warning", "No categories selected")
            return
            
        print(f"Querying with categories: {self.selected_categories}")
        success, problems = self.db.get_problems_list(
            category_id=None,  # We'll filter by category names
            search_term=None
        )
        
        if not success:
            messagebox.showerror("Error", f"Failed to query problems: {problems}")
            return
            
        print(f"Got {len(problems)} problems from database")
        
        # Filter problems that have ALL selected categories
        self.current_results = []
        for problem in problems:
            print(f"\nChecking problem {problem.get('problem_id')}:")
            if "categories" in problem:
                problem_categories = set(cat["name"] for cat in problem["categories"])
                print(f"  Problem categories: {problem_categories}")
                print(f"  Selected categories: {self.selected_categories}")
                print(f"  Selected categories is subset? {self.selected_categories.issubset(problem_categories)}")
                print(f"  Problem categories is subset? {problem_categories.issubset(self.selected_categories)}")
                if self.selected_categories.issubset(problem_categories):
                    print(f"  -> Adding problem {problem.get('problem_id')} to results")
                    self.current_results.append(problem)
                else:
                    print(f"  -> Not adding problem {problem.get('problem_id')} (categories don't match)")
            else:
                print(f"  -> Problem {problem.get('problem_id')} has no categories")
        
        print(f"\nFound {len(self.current_results)} matching problems")
        
        if not self.current_results:
            messagebox.showinfo("No Results", "No problems found with all selected categories")
            return
            
        # Sort by last modified date, most recent first
        self.current_results.sort(key=lambda p: p["last_modified"], reverse=True)
        
        # Reset index and load first result
        self.current_result_index = 0
        self.load_problem_content(self.current_results[0])
        first_problem_id = self.current_results[0].get('problem_id', '?')
        self.status_var.set(f"Showing result 1 of {len(self.current_results)} (Problem ID: {first_problem_id})")
    
    def next_match(self):
        """Load the next matching problem from the current result set"""
        if not self.current_results:
            messagebox.showinfo("No Results", "No active query results")
            return
            
        # Move to next result, wrapping around to start if at end
        self.current_result_index = (self.current_result_index + 1) % len(self.current_results)
        problem = self.current_results[self.current_result_index]
        
        # Load the problem
        self.load_problem_content(problem)
        problem_id = problem.get('problem_id', '?')
        self.status_var.set(
            f"Showing result {self.current_result_index + 1} of {len(self.current_results)} (Problem ID: {problem_id})"
        )
    
    def previous_match(self):
        """Load the previous matching problem from the current result set"""
        if not self.current_results:
            messagebox.showinfo("No Results", "No active query results")
            return
        # Move to previous result, wrapping around to end if at start
        self.current_result_index = (self.current_result_index - 1) % len(self.current_results)
        problem = self.current_results[self.current_result_index]
        self.load_problem_content(problem)
        problem_id = problem.get('problem_id', '?')
        self.status_var.set(
            f"Showing result {self.current_result_index + 1} of {len(self.current_results)} (Problem ID: {problem_id})"
        )
    
    def reset_form(self):
        """Reset all form fields"""
        # Clear editor content
        self.editor.set_text("")
        
        # Clear answer and notes
        self.answer_text.delete(0, tk.END)
        self.notes_text.delete("1.0", tk.END)
        
        # Clear problem ID
        self.problem_id_entry.delete(0, tk.END)
        
        # Clear selected categories and reset category panel
        self.selected_categories.clear()
        self.category_panel.selected_categories.clear()
        # Reset visual state of all category buttons
        for cat, btn in self.category_panel.buttons.items():
            self.category_panel.highlight_category(cat, False)
        
        # Clear current problem ID and results
        self.current_problem_id = None
        self.current_results = []
        self.current_result_index = -1
        
        # Update status
        self.status_var.set("Form reset")
    
    def delete_problem(self):
        """Delete the current problem from the database"""
        if not hasattr(self, 'current_problem_id') or self.current_problem_id is None:
            messagebox.showwarning("Warning", "No problem is currently loaded")
            return
            
        if not messagebox.askyesno("Confirm Delete", 
            f"Are you sure you want to delete problem #{self.current_problem_id}?\nThis action cannot be undone."):
            return
            
        success, message = self.db.delete_problem(self.current_problem_id)
        if success:
            self.status_var.set(f"Deleted problem #{self.current_problem_id}")
            self.reset_form()
        else:
            messagebox.showerror("Error", f"Failed to delete problem: {message}")

    def query_by_text(self):
        """Query problems by text in the problem content"""
        search_text = self.search_text_entry.get().strip()
        if not search_text:
            messagebox.showwarning("Warning", "Please enter text to search for.")
            return

        # Get all problems
        success, problems = self.db.get_problems_list()
        if not success:
            messagebox.showerror("Error", f"Failed to query problems: {problems}")
            return

        # Filter by text (case-insensitive)
        matches = [
            p for p in problems
            if search_text.lower() in p.get('content', '').lower()
        ]

        if not matches:
            messagebox.showinfo("No Results", f"No problems found containing '{search_text}'.")
            return

        self.current_results = matches
        self.current_result_index = 0
        self.load_problem_content(self.current_results[0])
        self.status_var.set(
            f"Showing result 1 of {len(self.current_results)} (Problem ID: {self.current_results[0].get('problem_id', '?')})"
        )

    def save_problem_and_types(self):
        """
        Save the current problem's content, answer, notes, and SAT types to the database.
        """
        if not hasattr(self, 'current_problem_id') or self.current_problem_id is None:
            messagebox.showwarning("Warning", "No problem is currently loaded")
            return
        # Gather updated fields
        content = self.editor.get_text()
        answer = self.answer_text.get()
        notes = self.notes_text.get("1.0", tk.END).strip()
        # Update the problem in the database
        success, msg = self.db.update_problem(
            self.current_problem_id,
            content=content,
            answer=answer,
            notes=notes
        )
        if not success:
            messagebox.showerror("Error", f"Failed to save problem: {msg}")
            return
        # Update SAT types
        if hasattr(self, 'sat_type_panel'):
            # Remove all current associations
            success, types = self.db.get_sat_types_for_problem(self.current_problem_id)
            if success:
                for t in types:
                    self.db.remove_problem_from_sat_type(self.current_problem_id, t['type_id'])
            # Add selected types
            for t in self.sat_type_panel.get_selected_types():
                self.db.add_problem_to_sat_type(self.current_problem_id, t)
        self.status_var.set("Problem and SAT types saved.")


class CategoryPanelCTk(ctk.CTkFrame):
    def __init__(self, parent, categories=None, on_category_click=None):
        super().__init__(parent, fg_color=MATH_DOMAINS_BG)
        self.categories = categories or []
        self.on_category_click = on_category_click
        self.buttons = {}
        self.selected_categories = set()
        self.build_panel()

    def build_panel(self):
        # Remove old buttons
        for btn in self.buttons.values():
            btn.destroy()
        self.buttons.clear()
        # Display as a grid, 2 columns
        for idx, cat in enumerate(self.categories):
            btn = ctk.CTkButton(
                self,
                text=cat,
                font=(DEFAULT_BOLD_FONT_FAMILY, DEFAULT_DOMAIN_BTN_FONT_SIZE, "bold"),
                fg_color=MATH_DOMAINS_BTN_BG,
                hover_color=MATH_DOMAINS_BTN_HOVER,
                text_color=MATH_DOMAINS_BTN_TEXT,
                corner_radius=8,
                width=220,
                height=40,
                command=lambda c=cat: self.toggle_category(c)
            )
            btn.grid(row=idx//2, column=idx%2, padx=8, pady=4, sticky="ew")
            self.buttons[cat] = btn

    def update_display(self, categories):
        self.categories = categories
        self.build_panel()

    def toggle_category(self, cat):
        if cat in self.selected_categories:
            self.selected_categories.remove(cat)
            self.buttons[cat].configure(fg_color=MATH_DOMAINS_BTN_BG)
        else:
            self.selected_categories.add(cat)
            self.buttons[cat].configure(fg_color=MATH_DOMAINS_BTN_HOVER)
        if self.on_category_click:
            self.on_category_click(cat)

    def highlight_category(self, cat, selected):
        if cat in self.buttons:
            self.buttons[cat].configure(fg_color=MATH_DOMAINS_BTN_HOVER if selected else MATH_DOMAINS_BTN_BG)
            if selected:
                self.selected_categories.add(cat)
            else:
                self.selected_categories.discard(cat)
