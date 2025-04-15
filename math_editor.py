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
import base64
import io
import shutil
import re

from editor import EditorComponent
from preview.latex_compiler import LaTeXCompiler
from preview.pdf_viewer import PDFViewer
from converters.image_converter import ImageConverter
from PIL import Image, ImageTk

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
        
        # Load the LaTeX template
        self.template = self.load_template()
        
        # Set up the UI components
        self.create_menu()
        self.create_layout()
        
        # Initialize current file path
        self.current_file = None
    
    def load_template(self):
        """Load the default LaTeX template"""
        # Look for template in resources directory first
        resources_dir = Path(__file__).parent / "resources"
        template_path = resources_dir / "default_template.tex"
        
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                return f.read()
        
        # Fallback to a basic template
        return """\\documentclass{article}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{graphicx}

% Set up image path - adjust if needed
\\graphicspath{{./}{./images/}}

\\begin{document}

#CONTENT#

\\end{document}
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
        self.menubar.add_cascade(label="Insert", menu=insert_menu)
        
        # View menu
        view_menu = tk.Menu(self.menubar, tearoff=0)
        view_menu.add_command(label="Increase Font Size", command=lambda: self.editor.increase_font_size())
        view_menu.add_command(label="Decrease Font Size", command=lambda: self.editor.decrease_font_size())
        view_menu.add_separator()
        view_menu.add_command(label="Update Preview", command=self.update_preview)
        self.menubar.add_cascade(label="View", menu=view_menu)
        
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
        
        self.preview_button = ttk.Button(
            self.toolbar,
            text="Update Preview",
            command=self.update_preview
        )
        self.preview_button.pack(side=tk.LEFT, padx=5)
        
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
                filetypes=[("Text files", "*.txt"), ("TeX files", "*.tex"), ("All files", "*.*")]
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
            defaultextension=".tex",
            filetypes=[("TeX files", "*.tex"), ("Text files", "*.txt"), ("All files", "*.*")]
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
            # Get the editor content
            content = self.editor.get_content()
            
            # Insert content into the template
            latex_document = self.template.replace("#CONTENT#", content)
            
            # Update status
            self.status_var.set("Preparing images for LaTeX compilation...")
            self.root.update_idletasks()  # Force UI update
            
            # Extract images from the database for compilation
            if not self.extract_images_for_compilation():
                self.status_var.set("Failed to extract images from database")
                messagebox.showerror("Image Error", "Failed to extract one or more images from the database for LaTeX compilation.")
                return
            
            # Update status for compilation
            self.status_var.set("Compiling LaTeX document...")
            self.root.update_idletasks()  # Force UI update
            
            # Compile the LaTeX document
            success, result = self.latex_compiler.compile_latex(latex_document)
            
            if success:
                # Display the PDF
                if self.pdf_viewer.display_pdf(result):
                    self.status_var.set("Preview updated successfully")
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
            
            # Insert content into the template
            latex_document = self.template.replace("#CONTENT#", content)
            
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
        dialog.geometry("400x300")
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
            max_size = (300, 200)
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