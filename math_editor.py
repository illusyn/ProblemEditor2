"""
MathEditor component for the Simplified Math Editor.

This module provides the main application class that integrates
all components and handles the user interface.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
from pathlib import Path
import tempfile
import base64
import io
import shutil
import re

from editor import EditorComponent
from preview.latex_compiler import LaTeXCompiler
from preview.pdf_viewer import PDFViewer
from converters.image_converter import ImageConverter
from PIL import Image, ImageTk
from markdown_parser import MarkdownParser  # Import for markdown parsing
from db_interface import DatabaseInterface

class MathEditor:
    """Main application class for the Simplified Math Editor"""
    
    def __init__(self, root):
        """
        Initialize the application
        
        Args:
            root: The root Tkinter window
        """
        self.root = root
        self.root.title("Simplified Math Editor")
        self.root.geometry("1200x800")
                
        # Initialize working directory
        self.working_dir = Path(tempfile.gettempdir()) / "simplified_math_editor"
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        # Create images directory
        image_dir = self.working_dir / "images"
        image_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the LaTeX compiler
        self.latex_compiler = LaTeXCompiler(working_dir=str(self.working_dir))
        
        # Initialize the image converter
        self.image_converter = ImageConverter(working_dir=str(self.working_dir / "images"))
        
        # Initialize the database interface (will set up menu later)
        self.db_interface = DatabaseInterface(self)
        
        # Initialize the markdown parser
        self.markdown_parser = MarkdownParser()
        
        # Load the LaTeX template
        self.template = self.load_template()
        
        # Set up the UI components
        self.create_menu()
        self.create_layout()
        
        # Set up database menu
        self.db_interface.setup_menu()
        
        # Initialize current file path
        self.current_file = None
        
        # Set up preview context menu
        self.setup_preview_context_menu()
    
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
        return r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\graphicspath{{./}{./images/}}

\begin{document}

#CONTENT#

\end{document}
"""
    
    def create_menu(self):
        """Create the application menu"""
        self.menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_as)
        file_menu.add_separator()
        file_menu.add_command(label="Export to PDF...", command=self.export_to_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.destroy)
        self.menubar.add_cascade(label="File", menu=file_menu)
        
        # Edit menu
        edit_menu = tk.Menu(self.menubar, tearoff=0)
        edit_menu.add_command(label="Cut", command=lambda: self.editor.cut_text())
        edit_menu.add_command(label="Copy", command=lambda: self.editor.copy_text())
        edit_menu.add_command(label="Paste", command=lambda: self.editor.paste_text())
        self.menubar.add_cascade(label="Edit", menu=edit_menu)
        
        # Insert menu
        insert_menu = tk.Menu(self.menubar, tearoff=0)
        insert_menu.add_command(label="Paste MathML as LaTeX", command=lambda: self.editor.paste_mathml())
        insert_menu.add_command(label="Paste LaTeX as Equation", command=lambda: self.editor.paste_latex())
        insert_menu.add_command(label="Paste Image as Figure", command=self.paste_image)
        insert_menu.add_command(label="Insert Image from File...", command=self.insert_image_from_file)
        insert_menu.add_separator()
        
        # Add markdown commands
        insert_menu.add_command(label="Problem Section", command=lambda: self.editor.insert_problem_section())
        insert_menu.add_command(label="Solution Section", command=lambda: self.editor.insert_solution_section())
        insert_menu.add_command(label="Question", command=lambda: self.editor.insert_question())
        insert_menu.add_command(label="Equation", command=lambda: self.editor.insert_equation())
        insert_menu.add_command(label="Aligned Equations", command=lambda: self.editor.insert_aligned_equations())
        insert_menu.add_command(label="Bullet Point", command=lambda: self.editor.insert_bullet_point())
        
        self.menubar.add_cascade(label="Insert", menu=insert_menu)
        
        # View menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_command(label="Increase Font Size", command=lambda: self.editor.increase_font_size())
        view_menu.add_command(label="Decrease Font Size", command=lambda: self.editor.decrease_font_size())
        view_menu.add_separator()
        view_menu.add_command(label="Update Preview", command=self.update_preview)
        self.menubar.add_cascade(label="View", menu=view_menu)
        
        # Template menu
        template_menu = tk.Menu(self.menubar, tearoff=0)
        template_menu.add_command(label="Basic Problem", command=self.insert_basic_template)
        template_menu.add_command(label="Two Equations Problem", command=self.insert_two_equations_template)
        template_menu.add_command(label="Problem with Image", command=self.insert_image_template)
        self.menubar.add_cascade(label="Templates", menu=template_menu)
        
        # Image menu
        image_menu = tk.Menu(self.menubar, tearoff=0)
        image_menu.add_command(label="Adjust Image Size...", command=self.adjust_image_size)
        self.menubar.add_cascade(label="Image", menu=image_menu)
        
        # Help menu
        help_menu = tk.Menu(self.menubar, tearoff=0)
        help_menu.add_command(label="Markdown Syntax", command=self.show_markdown_help)
        self.menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=self.menubar)
    
    def create_layout(self):
        """Create the main application layout"""
        # Create main frame
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top toolbar
        self.toolbar = ttk.Frame(self.main_frame)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Add toolbar buttons
        self.math_button = ttk.Button(
            self.toolbar, 
            text="Paste MathML",
            command=lambda: self.editor.paste_mathml()
        )
        self.math_button.pack(side=tk.LEFT, padx=5)
        
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
        
        # Create paned window for editor and preview
        self.paned_window = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.paned_window.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Editor frame
        self.editor_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.editor_frame, weight=1)
        
        # Preview frame
        self.preview_frame = ttk.Frame(self.paned_window)
        self.paned_window.add(self.preview_frame, weight=1)
        
        # Create editor component
        self.editor = EditorComponent(self.editor_frame)
        
        # Create PDF viewer component
        self.pdf_viewer = PDFViewer(self.preview_frame)
        
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
    
    def setup_preview_context_menu(self):
        """Set up context menu for the preview panel"""
        self.preview_context_menu = tk.Menu(self.root, tearoff=0)
        self.preview_context_menu.add_command(label="Adjust Image Size", command=self.adjust_image_size)
        
        # Bind right-click to show context menu to multiple components in the preview
        # This ensures we catch the right-click regardless of where it happens in the preview
        self.pdf_viewer.frame.bind("<Button-3>", self.show_preview_context_menu)
        self.pdf_viewer.canvas.bind("<Button-3>", self.show_preview_context_menu)
        self.pdf_viewer.pdf_frame.bind("<Button-3>", self.show_preview_context_menu)
        
        # Bind to canvas_frame too as it contains the scrollable view
        self.pdf_viewer.canvas_frame.bind("<Button-3>", self.show_preview_context_menu)
        
        # Also bind to any existing children
        for child in self.pdf_viewer.pdf_frame.winfo_children():
            child.bind("<Button-3>", self.show_preview_context_menu)
    
    def show_preview_context_menu(self, event):
        """Show the context menu at the current mouse position"""
        try:
            self.preview_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.preview_context_menu.grab_release()
    
    def set_initial_pane_position(self):
        """Set the initial position of the paned window divider"""
        width = self.root.winfo_width()
        if width > 100:  # Only if the window has been realized
            self.paned_window.sashpos(0, width // 2)
    
    def new_file(self):
        """Create a new file"""
        if self.check_save_changes():
            self.editor.set_content("")
            self.current_file = None
            self.root.title("Simplified Math Editor - Untitled")
            self.status_var.set("New file created")
    
    def open_file(self):
        """Open a file"""
        if self.check_save_changes():
            filepath = filedialog.askopenfilename(
                filetypes=[("Text files", "*.txt"), ("TeX files", "*.tex"), ("Markdown files", "*.md"), ("All files", "*.*")]
            )
            if filepath:
                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        content = file.read()
                        self.editor.set_content(content)
                        self.current_file = filepath
                        self.root.title(f"Simplified Math Editor - {os.path.basename(filepath)}")
                        self.status_var.set(f"Opened {filepath}")
                        
                        # Update preview
                        self.update_preview()
                except Exception as e:
                    messagebox.showerror("Error", f"Could not open file: {str(e)}")
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            return self._save_to_file(self.current_file)
        else:
            return self.save_as()
    
    def save_as(self):
        """Save the file with a new name"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("TeX files", "*.tex"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filepath:
            return self._save_to_file(filepath)
        return False
    
    def _save_to_file(self, filepath):
        """Save content to the specified file"""
        try:
            content = self.editor.get_content()
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
            self.current_file = filepath
            self.root.title(f"Simplified Math Editor - {os.path.basename(filepath)}")
            self.status_var.set(f"Saved to {filepath}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save file: {str(e)}")
            return False
    
    def extract_images_for_compilation(self):
        """
        Extract images from the database for LaTeX compilation
        
        Returns:
            bool: Success or failure
        """
        try:
            # Extract image filenames from the LaTeX content
            content = self.editor.get_content()
            # Modified pattern to be more robust in catching image filenames
            image_pattern = r'\\includegraphics(?:\[.*?\])?\{([^{}]+)\}'
            image_filenames = re.findall(image_pattern, content)
            
            if not image_filenames:
                # No images to extract
                return True
                
            # Debugging information
            print(f"Found {len(image_filenames)} images in LaTeX content: {image_filenames}")
            
            # Create images subdirectory in compilation directory if it doesn't exist
            dest_dir = self.working_dir
            images_dir = dest_dir / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Extract and save each image
            for image_name in image_filenames:
                print(f"Extracting image: {image_name}")
                # Remove any extra whitespace or newlines
                image_name = image_name.strip()
                
                # Get the image from the database
                success, img = self.image_converter.image_db.get_image(image_name)
                
                if not success:
                    # Try with common image extensions if the name doesn't have one
                    if '.' not in image_name:
                        extensions = ['.png', '.jpg', '.jpeg', '.gif']
                        for ext in extensions:
                            success, img = self.image_converter.image_db.get_image(image_name + ext)
                            if success:
                                image_name = image_name + ext
                                break
                
                if not success:
                    self.status_var.set(f"Error retrieving image from database: {image_name}")
                    print(f"Failed to retrieve image from database: {img}")
                    return False
                
                # Save to both main directory and images subdirectory for LaTeX compatibility
                try:
                    # Save to main directory
                    main_path = dest_dir / image_name
                    # Get format from file extension or use PNG as default
                    format_ext = os.path.splitext(image_name)[1][1:].upper() or 'PNG'
                    img.save(str(main_path), format=format_ext)
                    print(f"Saved image to: {main_path}")
                    
                    # Save to images subdirectory
                    subdir_path = images_dir / image_name
                    img.save(str(subdir_path), format=format_ext)
                    print(f"Saved image to: {subdir_path}")
                except Exception as e:
                    self.status_var.set(f"Error saving image: {str(e)}")
                    print(f"Failed to save image: {str(e)}")
                    return False
            
            return True
        except Exception as e:
            self.status_var.set(f"Error extracting images: {str(e)}")
            print(f"Error extracting images for compilation: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def update_preview(self):
        """Generate and display a preview of the current content"""
        try:
            # Update status
            self.status_var.set("Processing markdown...")
            self.root.update_idletasks()  # Force UI update
            
            # Get the editor content
            content = self.editor.get_content()
            
            # Parse the markdown to LaTeX
            latex_document = self.markdown_parser.parse(content)
            
            # DEBUG: Check if graphicx package is in the template
            if "\\usepackage{graphicx}" not in latex_document:
                print("WARNING: graphicx package missing from template!")
                # Add it immediately before \begin{document}
                latex_document = latex_document.replace("\\begin{document}", 
                    "\\usepackage{graphicx}\n\\graphicspath{{./}{./images/}}\n\n\\begin{document}")
                print("Added graphicx package to template")
            
            # Update status
            self.status_var.set("Preparing images for LaTeX compilation...")
            self.root.update_idletasks()  # Force UI update
            
            # Extract images from the database for compilation
            if not self.extract_images_for_compilation():
                self.status_var.set("Failed to extract images from database")
                messagebox.showerror("Image Error", "Failed to extract one or more images from the database for LaTeX compilation.")
                return
            
            # Write debug LaTeX file
            debug_file = self.working_dir / "debug_latex.tex"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(latex_document)
            print(f"Debug LaTeX document written to: {debug_file}")
            
            # Update status for compilation
            self.status_var.set("Compiling LaTeX document...")
            self.root.update_idletasks()  # Force UI update
            
            # Compile the LaTeX document
            success, result = self.latex_compiler.compile_latex(latex_document)
            
            if success:
                # Display the PDF
                if self.pdf_viewer.display_pdf(result):
                    self.status_var.set("Preview updated successfully")
                    
                    # Rebind the right-click event to any new elements in the preview
                    for child in self.pdf_viewer.pdf_frame.winfo_children():
                        child.bind("<Button-3>", self.show_preview_context_menu)
                else:
                    self.status_var.set("Error displaying PDF")
            else:
                # Show compilation error
                self.status_var.set("LaTeX compilation failed")
                messagebox.showerror("Compilation Error", result)
        
        except Exception as e:
            self.status_var.set("Preview error")
            messagebox.showerror("Preview Error", str(e))
    
    def export_to_pdf(self):
        """Export the current document to PDF"""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if not filepath:
            return
        
        try:
            # Get the editor content
            content = self.editor.get_content()
            
            # Parse the markdown to LaTeX
            latex_document = self.markdown_parser.parse(content)
            
            # Ensure graphicx package is included
            if "\\usepackage{graphicx}" not in latex_document:
                # Add it immediately before \begin{document}
                latex_document = latex_document.replace("\\begin{document}", 
                    "\\usepackage{graphicx}\n\\graphicspath{{./}{./images/}}\n\n\\begin{document}")
            
            # Update status
            self.status_var.set("Extracting images for LaTeX compilation...")
            self.root.update_idletasks()  # Force UI update
            
            # Extract images from the database for compilation
            if not self.extract_images_for_compilation():
                self.status_var.set("Failed to extract images from database")
                messagebox.showerror("Image Error", "Failed to extract one or more images from the database for PDF export.")
                return
            
            # Update status for compilation
            self.status_var.set("Compiling LaTeX for PDF export...")
            self.root.update_idletasks()  # Force UI update
            
            # Compile the LaTeX document
            success, result = self.latex_compiler.compile_latex(latex_document, "export")
            
            if success:
                # Copy the PDF to the target location
                import shutil
                shutil.copy2(result, filepath)
                self.status_var.set(f"Exported to {filepath}")
                
                # Ask if the user wants to open the PDF
                if messagebox.askyesno("Export Complete", "PDF exported successfully. Open the PDF?"):
                    self.open_file_with_default_app(filepath)
            else:
                # Show compilation error
                self.status_var.set("PDF export failed")
                messagebox.showerror("Export Error", result)
        
        except Exception as e:
            self.status_var.set("Export error")
            messagebox.showerror("Export Error", str(e))
    
    def get_clipboard_image(self):
        """Get image from clipboard"""
        try:
            # Use PIL's ImageGrab for clipboard access
            from PIL import ImageGrab
            
            # Try to grab the image from clipboard
            image = ImageGrab.grabclipboard()
            
            # Check what we got back
            if isinstance(image, Image.Image):
                # We got an image directly
                return image
            elif isinstance(image, list) and len(image) > 0:
                # We got a list of file paths
                if os.path.isfile(image[0]):
                    return Image.open(image[0])
            
            # If we get here, no valid image was found
            return None
            
        except ImportError:
            messagebox.showinfo("Missing Dependency", 
                               "PIL ImageGrab module is required for clipboard images.\n"
                               "On Linux, you may need additional packages.")
            return None
        except Exception as e:
            print(f"Clipboard error: {str(e)}")
            return None
    
    def paste_image(self):
        """Paste image from clipboard as LaTeX figure"""
        try:
            # Try to get image from clipboard
            clipboard_image = self.get_clipboard_image()
            
            if not clipboard_image:
                messagebox.showinfo("No Image", 
                                   "No image found in clipboard.\n\n"
                                   "Note: The application can only access images that are\n"
                                   "copied as images, not as files or other formats.")
                return
            
            # Process the image (store in database)
            success, result = self.image_converter.process_image(clipboard_image)
            
            if not success:
                messagebox.showerror("Image Processing Error", result)
                return
            
            # Create a dialog to get caption and width
            image_info = self.get_image_details(result)
            if not image_info:
                return  # User cancelled
            
            # Check if document is empty or lacks structure
            content = self.editor.get_content().strip()
            needs_structure = not content or not any(tag in content for tag in ["#problem", "#question", "#solution"])
            
            # If document needs structure, add a minimal structure before the figure
            if needs_structure:
                # Add a problem section before the image
                self.editor.editor.insert(tk.INSERT, "#problem\n\n")
            
            # Create LaTeX figure code
            latex_figure = self.image_converter.create_latex_figure(
                image_path=image_info["filename"],  # Use just the filename
                caption=image_info["caption"],
                label=image_info["label"],
                width=image_info["width"]
            )
            
            # Insert at cursor position
            self.editor.editor.insert(tk.INSERT, latex_figure)
            
            # Immediately extract image and update preview
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("Image Error", str(e))
    
    def get_image_details(self, image_info):
        """Show dialog to get image details"""
        # Create a dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Image Details")
        dialog.geometry("400x500")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create variables
        caption_var = tk.StringVar(value="Figure caption")
        label_var = tk.StringVar(value=f"fig:{Path(image_info['filename']).stem}")
        width_var = tk.DoubleVar(value=0.8)
        
        # Create widgets
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Caption
        ttk.Label(frame, text="Caption:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        caption_entry = ttk.Entry(frame, textvariable=caption_var, width=40)
        caption_entry.grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Label
        ttk.Label(frame, text="Label:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        label_entry = ttk.Entry(frame, textvariable=label_var, width=40)
        label_entry.grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Width
        ttk.Label(frame, text="Width (0.1-1.0):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        width_scale = ttk.Scale(frame, from_=0.1, to=1.0, variable=width_var, orient=tk.HORIZONTAL)
        width_scale.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        width_label = ttk.Label(frame, textvariable=width_var)
        width_label.grid(row=2, column=2, padx=5, pady=5)
        
        # Preview
        ttk.Label(frame, text="Preview:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Get the image from database for preview
        success, image = self.image_converter.image_db.get_image(image_info["filename"])
        if success:
            # Resize image for preview
            max_size = (350, 300)
            image.thumbnail(max_size)
            photo = ImageTk.PhotoImage(image)
            
            # Store reference to prevent garbage collection
            dialog.photo = photo
            
            # Display image
            image_label = ttk.Label(frame, image=photo)
            image_label.grid(row=4, column=0, columnspan=3, padx=5, pady=5)
        
        # Result
        result = {"cancelled": True}
        
        def on_ok():
            result["cancelled"] = False
            result["caption"] = caption_var.get()
            result["label"] = label_var.get()
            result["width"] = width_var.get()
            result["filename"] = image_info["filename"]
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)
        
        ok_button = ttk.Button(button_frame, text="OK", command=on_ok)
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Configure grid
        frame.columnconfigure(1, weight=1)
        
        # Wait for dialog to close
        self.root.wait_window(dialog)
        
        if result["cancelled"]:
            return None
        
        return result
    
    def insert_image_from_file(self):
        """Insert an image from a file"""
        # Ask for image file
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return
        
        try:
            # Process the image
            success, result = self.image_converter.process_image(file_path)
            
            if not success:
                messagebox.showerror("Image Processing Error", result)
                return
            
            # Create a dialog to get caption and width
            image_info = self.get_image_details(result)
            if not image_info:
                return  # User cancelled
            
            # Check if document is empty or lacks structure
            content = self.editor.get_content().strip()
            needs_structure = not content or not any(tag in content for tag in ["#problem", "#question", "#solution"])
            
            # If document needs structure, add a minimal structure before the figure
            if needs_structure:
                # Add a problem section before the image
                self.editor.editor.insert(tk.INSERT, "#problem\n\n")
            
            # Create LaTeX figure code
            latex_figure = self.image_converter.create_latex_figure(
                image_path=image_info["filename"],  # Use just the filename
                caption=image_info["caption"],
                label=image_info["label"],
                width=image_info["width"]
            )
            
            # Insert at cursor position
            self.editor.editor.insert(tk.INSERT, latex_figure)
            
            # Update preview
            self.update_preview()
            
        except Exception as e:
            messagebox.showerror("Image Error", str(e))
    
    def adjust_image_size(self):
        """Show dialog to adjust the size of the image in the document"""
        # Check if there's an image in the document
        content = self.editor.get_content()
        
        # More robust pattern to match includegraphics command with optional width parameter
        image_pattern = r'\\includegraphics(?:\[.*?width=(.*?)\\textwidth.*?\]|\[\])?\{([^{}]+)\}'
        match = re.search(image_pattern, content)
        
        if not match:
            # Try alternate pattern without the width parameter extraction
            image_pattern = r'\\includegraphics(?:\[.*?\])?\{([^{}]+)\}'
            match = re.search(image_pattern, content)
            if match:
                # Found image without width parameter
                filename = match.group(1)
                current_width = 0.8  # Default width
            else:
                messagebox.showinfo("No Image Found", "No image was found in the document.")
                return
        else:
            # Extract current width and filename
            current_width_str = match.group(1) if match.group(1) else "0.8"
            try:
                current_width = float(current_width_str)
            except ValueError:
                current_width = 0.8
            
            filename = match.group(2)
        
        # Log current state for debugging
        print(f"Image found: {filename}")
        print(f"Current width: {current_width}")
        
        # Create a dialog for size adjustment
        dialog = tk.Toplevel(self.root)
        dialog.title("Adjust Image Size")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Create variables
        width_var = tk.DoubleVar(value=current_width)
        
        # Create widgets
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Width
        ttk.Label(frame, text=f"Image: {filename}").pack(anchor=tk.W, padx=5, pady=5)
        ttk.Label(frame, text="Width (0.1-1.0 × text width):").pack(anchor=tk.W, padx=5, pady=5)
        width_scale = ttk.Scale(frame, from_=0.1, to=1.0, variable=width_var, orient=tk.HORIZONTAL)
        width_scale.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a label to show the current value
        value_label = ttk.Label(frame, text=f"Current width: {current_width:.2f} × text width")
        value_label.pack(anchor=tk.E, padx=5)
        
        # Update the label when the scale changes
        def update_value_label(event=None):
            value_label.config(text=f"Current width: {width_var.get():.2f} × text width")
        
        width_scale.bind("<Motion>", update_value_label)
        width_scale.bind("<ButtonRelease-1>", update_value_label)
        
        # Preview image (if available)
        try:
            success, image = self.image_converter.image_db.get_image(filename)
            if success:
                # Resize image for preview
                max_size = (350, 200)
                image.thumbnail(max_size)
                photo = ImageTk.PhotoImage(image)
                
                # Store reference to prevent garbage collection
                dialog.photo = photo
                
                # Display image
                image_label = ttk.Label(frame, image=photo)
                image_label.pack(padx=5, pady=10)
        except Exception as e:
            print(f"Error loading image preview: {str(e)}")
        
        def on_ok():
            # Update the image size in the document
            new_width = width_var.get()
            
            print(f"New width: {new_width}")
            
            # Find the original includegraphics tag
            original_pattern = r'\\includegraphics(?:\[.*?\])?\{' + re.escape(filename) + r'\}'
            match = re.search(original_pattern, content)
            
            if not match:
                print("Could not find the image tag in the document")
                messagebox.showerror("Error", "Could not locate the image in the document for updating.")
                dialog.destroy()
                return
            
            # Get the exact original tag
            original_tag = match.group(0)
            print(f"Original tag: {original_tag}")
            
            # Create new tag - use string concatenation to avoid regex interpretation issues
            new_image_tag = "\\includegraphics[width=" + str(new_width) + "\\textwidth]{" + filename + "}"
            print(f"New image tag: {new_image_tag}")
            
            # Use simple string replacement instead of regex replacement
            new_content = content.replace(original_tag, new_image_tag)
            
            # Check if replacement worked
            if new_content == content:
                print("Warning: Content was not modified by string replacement")
                messagebox.showerror("Error", "Failed to update the image size.")
                dialog.destroy()
                return
            
            # Update editor content
            self.editor.set_content(new_content)
            
            # Update preview
            self.update_preview()
            
            dialog.destroy()
            self.status_var.set(f"Image size updated to {new_width:.2f}×textwidth")
        
        def on_cancel():
            dialog.destroy()
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ok_button = ttk.Button(button_frame, text="Apply", command=on_ok)
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
    
    def open_file_with_default_app(self, filepath):
        """Open a file with the default application"""
        import platform
        import subprocess
        
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', filepath], check=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open the file: {str(e)}")
    
    def check_save_changes(self):
        """Check if there are unsaved changes and prompt user to save"""
        if self.current_file:
            try:
                with open(self.current_file, "r", encoding="utf-8") as file:
                    original_content = file.read()
                current_content = self.editor.get_content()
                
                if original_content != current_content:
                    response = messagebox.askyesnocancel(
                        "Unsaved Changes",
                        "Do you want to save changes to the current file?"
                    )
                    if response is None:  # Cancel
                        return False
                    elif response:  # Yes
                        return self.save_file()
            except:
                pass  # Ignore errors reading file
        return True
    
    def insert_basic_template(self):
        """Insert a basic problem template"""
        template = """#problem
Solve the following equation:

#eq
2x + 3 = 7

#question
What is the value of x?
"""
        self.editor.set_content(template)
        self.update_preview()
    
    def insert_two_equations_template(self):
        """Insert a two equations problem template"""
        template = """#problem
Solve the system of equations:

#eq
3x + 2y = 12

#eq
x - y = 1

#question
Find the values of x and y.
"""
        self.editor.set_content(template)
        self.update_preview()
    
    def insert_image_template(self):
        """Insert a problem with image template"""
        template = """#problem
Consider the triangle shown in the figure:

[Insert figure reference here]

#question
Calculate the area of the triangle.
"""
        self.editor.set_content(template)
    
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