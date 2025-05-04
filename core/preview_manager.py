"""
Preview management for the Simplified Math Editor.

This module provides functionality to generate and display previews
of the markdown content as compiled LaTeX documents.
"""

import os
import re
import tkinter as tk
from tkinter import messagebox
from pathlib import Path
from typing import Optional, Dict, Any


class PreviewManager:
    """Manages the preview generation and display for the Simplified Math Editor"""
    
    def __init__(self, app):
        """
        Initialize the preview manager
        
        Args:
            app: Reference to the MathEditor instance
        """
        self.app = app
        self.current_preview_file = None
    
    def update_preview(self):
        """Generate and display a preview of the current content"""
        try:
            # Update status
            self.app.status_var.set("Processing markdown...")
            self.app.root.update_idletasks()  # Force UI update
            
            # Get the editor content
            content = self.app.editor.get_content()
            
            # Parse the markdown to LaTeX
            latex_content = self.app.markdown_parser.parse(content, context='preview')
            full_latex = self.app.template.replace("#CONTENT#", latex_content)
            
            # Check if graphicx package is in the template
            if "\\usepackage{graphicx}" not in full_latex:
                print("WARNING: graphicx package missing from template!")
                # Add it immediately before \begin{document}
                full_latex = full_latex.replace("\\begin{document}", 
                    "\\usepackage{graphicx}\n\\graphicspath{{./}{./images/}}\n\n\\begin{document}")
                print("Added graphicx package to template")
            
            # Update status
            self.app.status_var.set("Preparing images for LaTeX compilation...")
            self.app.root.update_idletasks()  # Force UI update
            
            # Extract images from the database for compilation
            if not self.extract_images_for_compilation():
                self.app.status_var.set("Failed to extract images from database")
                messagebox.showerror("Image Error", "Failed to extract one or more images from the database for LaTeX compilation.")
                return
            
            # Write debug LaTeX file
            debug_file = self.app.working_dir / "debug_latex.tex"
            with open(debug_file, "w", encoding="utf-8") as f:
                f.write(full_latex)
            print(f"Debug LaTeX document written to: {debug_file}")
            
            # Update status for compilation
            self.app.status_var.set("Compiling LaTeX document...")
            self.app.root.update_idletasks()  # Force UI update
            
            # Compile the LaTeX document
            success, result = self.app.latex_compiler.compile_latex(full_latex)
            
            if success:
                # Display the PDF
                if self.app.pdf_viewer.display_pdf(result):
                    self.app.status_var.set("Preview updated successfully")
                    self.current_preview_file = result
                    
                    # Rebind the right-click event to any new elements in the preview
                    for child in self.app.pdf_viewer.pdf_frame.winfo_children():
                        child.bind("<Button-3>", self.app.show_preview_context_menu)
                else:
                    self.app.status_var.set("Error displaying PDF")
            else:
                # Show compilation error
                self.app.status_var.set("LaTeX compilation failed")
                messagebox.showerror("Compilation Error", result)
        
        except Exception as e:
            self.app.status_var.set("Preview error")
            messagebox.showerror("Preview Error", str(e))
    
    def extract_images_for_compilation(self):
        """
        Extract images from the database for LaTeX compilation
        
        Returns:
            bool: Success or failure
        """
        try:
            # Extract image filenames from the LaTeX content
            content = self.app.editor.get_content()
            # Modified pattern to be more robust in catching image filenames
            image_pattern = r'\\includegraphics(?:\[.*?\])?\{([^{}]+)\}'
            image_filenames = re.findall(image_pattern, content)
            
            if not image_filenames:
                # No images to extract
                return True
                
            # Debugging information
            print(f"Found {len(image_filenames)} images in LaTeX content: {image_filenames}")
            
            # Create images subdirectory in compilation directory if it doesn't exist
            dest_dir = self.app.working_dir
            images_dir = dest_dir / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Extract and save each image
            for image_name in image_filenames:
                print(f"Extracting image: {image_name}")
                # Remove any extra whitespace or newlines
                image_name = image_name.strip()
                
                # Get the image from the database
                success, img = self.app.image_converter.image_db.get_image(image_name)
                
                if not success:
                    # Try with common image extensions if the name doesn't have one
                    if '.' not in image_name:
                        extensions = ['.png', '.jpg', '.jpeg', '.gif']
                        for ext in extensions:
                            success, img = self.app.image_converter.image_db.get_image(image_name + ext)
                            if success:
                                image_name = image_name + ext
                                break
                
                if not success:
                    self.app.status_var.set(f"Error retrieving image from database: {image_name}")
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
                    self.app.status_var.set(f"Error saving image: {str(e)}")
                    print(f"Failed to save image: {str(e)}")
                    return False
            
            return True
        except Exception as e:
            self.app.status_var.set(f"Error extracting images: {str(e)}")
            print(f"Error extracting images for compilation: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def setup_preview_context_menu(self):
        """Set up context menu for the preview panel"""
        self.preview_context_menu = tk.Menu(self.app.root, tearoff=0)
        self.preview_context_menu.add_command(
            label="Adjust Image", 
            command=self.app.adjust_image_size
        )
        
        # Bind right-click to show context menu to multiple components in the preview
        # This ensures we catch the right-click regardless of where it happens in the preview
        self.app.pdf_viewer.frame.bind("<Button-3>", self.show_preview_context_menu)
        self.app.pdf_viewer.canvas.bind("<Button-3>", self.show_preview_context_menu)
        self.app.pdf_viewer.pdf_frame.bind("<Button-3>", self.show_preview_context_menu)
        
        # Bind to canvas_frame too as it contains the scrollable view
        self.app.pdf_viewer.canvas_frame.bind("<Button-3>", self.show_preview_context_menu)
        
        # Also bind to any existing children
        for child in self.app.pdf_viewer.pdf_frame.winfo_children():
            child.bind("<Button-3>", self.show_preview_context_menu)
        
        return self.preview_context_menu
    
    def show_preview_context_menu(self, event):
        """Show the context menu at the current mouse position"""
        try:
            self.preview_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.preview_context_menu.grab_release()

    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        indent = params.get("indent", self._parameters["indent"]["default"])
        vspace = params.get('vspace', self._parameters['vspace']['default'])
        if indent > 0:
            return f"\\hspace{{{indent}em}}{content}\\par\n\\vspace{{{vspace}em}}\n"
        return f"{content}\\par\n\\vspace{{{vspace}em}}\n"