"""
Image management for the Simplified Math Editor.

This module provides functionality to handle images in the editor,
including clipboard operations, file operations, and image details dialogs.
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import re
from pathlib import Path
from PIL import Image, ImageTk
from ui.dialogs.image_adjustbox_dialog import AdjustboxImageDialog


class ImageManager:
    """Manages image operations for the Simplified Math Editor"""
    
    def __init__(self, app):
        """
        Initialize the image manager
        
        Args:
            app: Reference to the MathEditor instance
        """
        self.app = app
    
    def paste_image(self):
        """
        Paste image from clipboard as LaTeX figure
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if currently using a font that requires XeLaTeX
            current_font = self.app.config_manager.get_value("preview", "font_family", "Computer Modern")
            uses_xelatex = current_font in ["Calibri", "Cambria Math"]
            
            # If using a font that requires XeLaTeX, temporarily switch to Computer Modern
            if uses_xelatex:
                # Store original font
                original_font = current_font
                # Temporarily set to Computer Modern
                self.app.config_manager.set_value("preview", "font_family", "Computer Modern")
                # Flag to restore later
                needs_restore = True
            else:
                needs_restore = False
            
            # Try to get image from clipboard - use ImageConverter method
            success, clipboard_image = self.app.image_converter.get_image_from_clipboard()
            
            if not success:
                # Restore font if needed before returning
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                    
                messagebox.showinfo("No Image", 
                                   "No image found in clipboard.\n\n"
                                   "Note: The application can only access images that are\n"
                                   "copied as images, not as files or other formats.")
                return False
            
            # Process the image (store in database)
            success, result = self.app.image_converter.process_image(clipboard_image)
            
            if not success:
                # Restore font if needed before returning
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                    
                messagebox.showerror("Image Processing Error", result)
                return False
            
            # Create a dialog to get caption and width
            image_info = self.get_image_details(result)
            if not image_info:
                # Restore font if needed before returning
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                    
                return False  # User cancelled
            
            # Check if document is empty or lacks structure
            content = self.app.editor.get_content().strip()
            needs_structure = not content or not any(tag in content for tag in ["#problem", "#question", "#solution"])
            
            # If document needs structure, add a minimal structure before the figure
            if needs_structure:
                # Add a problem section before the image
                self.app.editor.editor.insert(tk.INSERT, "#problem\n\n")
            
            # Create LaTeX figure code
            latex_figure = self.app.image_converter.create_latex_figure(
                image_path=image_info["filename"],  # Use just the filename
                caption=image_info["caption"],
                label=image_info["label"],
                width=image_info["width"]
            )
            
            # Insert at cursor position
            self.app.editor.editor.insert(tk.INSERT, latex_figure)
            
            # Immediately extract image and update preview
            self.app.update_preview()
            
            # Restore original font if needed
            if needs_restore:
                self.app.config_manager.set_value("preview", "font_family", original_font)
                # Refresh preview again with the original font
                self.app.update_preview()
                
            return True
                
        except Exception as e:
            # Restore original font if needed before returning
            if 'needs_restore' in locals() and needs_restore and 'original_font' in locals():
                self.app.config_manager.set_value("preview", "font_family", original_font)
                
            messagebox.showerror("Image Error", str(e))
            return False
    
    def insert_image_from_file(self):
        """
        Insert an image from a file
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if currently using a font that requires XeLaTeX
        current_font = self.app.config_manager.get_value("preview", "font_family", "Computer Modern")
        uses_xelatex = current_font in ["Calibri", "Cambria Math"]
        
        # If using a font that requires XeLaTeX, temporarily switch to Computer Modern
        if uses_xelatex:
            # Store original font
            original_font = current_font
            # Temporarily set to Computer Modern
            self.app.config_manager.set_value("preview", "font_family", "Computer Modern")
            # Flag to restore later
            needs_restore = True
        else:
            needs_restore = False
            
        try:
            # Ask for image file
            file_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[
                    ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                    ("All files", "*.*")
                ]
            )
            
            if not file_path:
                # Restore font if needed before returning
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                    
                return False
            
            # Process the image
            success, result = self.app.image_converter.process_image(file_path)
            
            if not success:
                # Restore font if needed before returning
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                    
                messagebox.showerror("Image Processing Error", result)
                return False
            
            # Create a dialog to get caption and width
            image_info = self.get_image_details(result)
            if not image_info:
                # Restore font if needed before returning
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                    
                return False  # User cancelled
            
            # Check if document is empty or lacks structure
            content = self.app.editor.get_content().strip()
            needs_structure = not content or not any(tag in content for tag in ["#problem", "#question", "#solution"])
            
            # If document needs structure, add a minimal structure before the figure
            if needs_structure:
                # Add a problem section before the image
                self.app.editor.editor.insert(tk.INSERT, "#problem\n\n")
            
            # Create LaTeX figure code
            latex_figure = self.app.image_converter.create_latex_figure(
                image_path=image_info["filename"],  # Use just the filename
                caption=image_info["caption"],
                label=image_info["label"],
                width=image_info["width"]
            )
            
            # Insert at cursor position
            self.app.editor.editor.insert(tk.INSERT, latex_figure)
            
            # Update preview
            self.app.update_preview()
            
            # Restore original font if needed
            if needs_restore:
                self.app.config_manager.set_value("preview", "font_family", original_font)
                # Refresh preview again with the original font
                self.app.update_preview()
                
            return True
                
        except Exception as e:
            # Restore original font if needed before returning
            if 'needs_restore' in locals() and needs_restore and 'original_font' in locals():
                self.app.config_manager.set_value("preview", "font_family", original_font)
                
            messagebox.showerror("Image Error", str(e))
            return False
    
    def get_image_details(self, image_info):
        """
        Show dialog to get image details
        
        Args:
            image_info (dict): Dictionary with image information
            
        Returns:
            dict or None: Dictionary with image details or None if cancelled
        """
        # Create a dialog
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Image Details")
        dialog.geometry("400x700")
        dialog.transient(self.app.root)
        dialog.grab_set()
        
        # Create variables
        caption_var = tk.StringVar(value="")  # Empty by default
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
        success, image = self.app.image_converter.image_db.get_image(image_info["filename"])
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
        self.app.root.wait_window(dialog)
        
        if result["cancelled"]:
            return None
        
        return result
    
    def adjust_image_size(self):
        """
        Show the new Adjustbox-based dialog to adjust the image in the document.
        Returns:
            bool: True if successful, False otherwise
        """
        content = self.app.editor.get_content()
        # Try to match adjustbox-wrapped images first
        adjustbox_pattern = r'\\adjustbox\{[^}]*\}\s*\{\s*\\includegraphics\[.*?\]\{([^{}]+)\}\s*\}'
        match = re.search(adjustbox_pattern, content, re.DOTALL)
        if match:
            filename = match.group(1)
            print(f"Launching AdjustboxImageDialog for: {filename}")
            AdjustboxImageDialog(self.app.root, self.app.editor, self, filename)
            return True
        else:
            print("No image match found in document.")
            messagebox.showinfo("No Image Found", "No image was found in the document.")
            return False