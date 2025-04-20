"""
Image dialogs for the Simplified Math Editor.

This module provides dialog windows for image operations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
from pathlib import Path
import re

class ImageDetailsDialog:
    """Dialog for configuring image details after insertion"""
    
    def __init__(self, parent, image_info, image_manager, on_apply=None):
        """
        Initialize the image details dialog
        
        Args:
            parent: Parent widget
            image_info (dict): Information about the image
            image_manager: The ImageManager instance
            on_apply (function, optional): Callback function for when changes are applied
        """
        self.parent = parent
        self.image_info = image_info
        self.image_manager = image_manager
        self.on_apply = on_apply
        self.result = {"cancelled": True}
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Image Details")
        self.dialog.geometry("450x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create variables
        self.caption_var = tk.StringVar(value="Figure caption")
        self.label_var = tk.StringVar(value=f"fig:{Path(image_info['filename']).stem}")
        self.width_var = tk.DoubleVar(value=0.8)  # LaTeX width
        
        # Image dimension variables
        current_width = image_info.get("width", 0)
        current_height = image_info.get("height", 0)
        self.original_width = image_info.get("original_width", current_width)
        self.original_height = image_info.get("original_height", current_height)
        
        self.px_width_var = tk.IntVar(value=current_width)
        self.px_height_var = tk.IntVar(value=current_height)
        self.maintain_aspect_var = tk.BooleanVar(value=True)
        
        # Create the dialog UI
        self.create_widgets()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
    
    def create_widgets(self):
        """Create the dialog widgets"""
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Caption
        ttk.Label(frame, text="Caption:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        caption_entry = ttk.Entry(frame, textvariable=self.caption_var, width=40)
        caption_entry.grid(row=0, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Label
        ttk.Label(frame, text="Label:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        label_entry = ttk.Entry(frame, textvariable=self.label_var, width=40)
        label_entry.grid(row=1, column=1, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # LaTeX Width
        ttk.Label(frame, text="LaTeX Width (0.1-1.0):").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        width_scale = ttk.Scale(frame, from_=0.1, to=1.0, variable=self.width_var, orient=tk.HORIZONTAL)
        width_scale.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        width_label = ttk.Label(frame, textvariable=self.width_var)
        width_label.grid(row=2, column=2, padx=5, pady=5)
        
        # Image Dimensions section
        dimension_frame = ttk.LabelFrame(frame, text="Image Dimensions (pixels)")
        dimension_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W+tk.E, padx=5, pady=10)
        
        # Original dimensions info
        if "was_resized" in self.image_info and self.image_info["was_resized"]:
            resize_info = f"Original: {self.original_width}×{self.original_height} - Resized to fit within 600×800"
            ttk.Label(dimension_frame, text=resize_info, foreground="blue").grid(
                row=0, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Width input
        ttk.Label(dimension_frame, text="Width:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        width_entry = ttk.Entry(dimension_frame, textvariable=self.px_width_var, width=6)
        width_entry.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(dimension_frame, text="px").grid(row=1, column=2, sticky=tk.W)
        
        # Height input
        ttk.Label(dimension_frame, text="Height:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        height_entry = ttk.Entry(dimension_frame, textvariable=self.px_height_var, width=6)
        height_entry.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        ttk.Label(dimension_frame, text="px").grid(row=2, column=2, sticky=tk.W)
        
        # Maintain aspect ratio checkbox
        aspect_check = ttk.Checkbutton(dimension_frame, text="Maintain aspect ratio", 
                                      variable=self.maintain_aspect_var)
        aspect_check.grid(row=3, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Reset button
        if "was_resized" in self.image_info and self.image_info["was_resized"]:
            reset_button = ttk.Button(dimension_frame, text="Reset to Original", command=self.reset_to_original)
            reset_button.grid(row=4, column=0, columnspan=3, sticky=tk.W, padx=5, pady=5)
        
        # Preview
        ttk.Label(frame, text="Preview:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Create a frame for the preview image
        preview_frame = ttk.Frame(frame)
        preview_frame.grid(row=5, column=0, columnspan=3, padx=5, pady=5)
        
        # Image preview label
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack()
        
        # Initial preview update
        self.update_preview()
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ok_button = ttk.Button(button_frame, text="OK", command=self.on_ok)
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Configure grid
        frame.columnconfigure(1, weight=1)
        
        # Bind the trace callbacks
        self.px_width_var.trace_add("write", self.on_width_change)
        self.px_height_var.trace_add("write", self.on_height_change)
    
    def on_width_change(self, *args):
        """Handle width change while preserving aspect ratio"""
        if self.maintain_aspect_var.get() and self.original_width > 0 and self.original_height > 0:
            # Calculate new height based on width while preserving aspect ratio
            aspect_ratio = self.original_height / self.original_width
            new_height = int(self.px_width_var.get() * aspect_ratio)
            self.px_height_var.set(new_height)
            
            # Update preview
            self.update_preview()
    
    def on_height_change(self, *args):
        """Handle height change while preserving aspect ratio"""
        if self.maintain_aspect_var.get() and self.original_width > 0 and self.original_height > 0:
            # Calculate new width based on height while preserving aspect ratio
            aspect_ratio = self.original_width / self.original_height
            new_width = int(self.px_height_var.get() * aspect_ratio)
            self.px_width_var.set(new_width)
            
            # Update preview
            self.update_preview()
    
    def reset_to_original(self):
        """Reset dimensions to original values"""
        self.px_width_var.set(self.original_width)
        self.px_height_var.set(self.original_height)
        
        # Update image preview
        self.update_preview()
    
    def update_preview(self):
        """Update the image preview"""
        try:
            success, image = self.image_manager.image_db.get_image(self.image_info["filename"])
            if success:
                new_width = self.px_width_var.get()
                new_height = self.px_height_var.get()
                
                if new_width > 0 and new_height > 0:
                    # Create a copy before resizing to avoid modifying the original
                    preview_img = image.copy()
                    preview_img = preview_img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Scale down further if needed for display
                    max_preview_size = (400, 300)
                    if preview_img.width > max_preview_size[0] or preview_img.height > max_preview_size[1]:
                        preview_img.thumbnail(max_preview_size)
                    
                    # Convert to PhotoImage for display
                    photo = ImageTk.PhotoImage(preview_img)
                    
                    # Store reference to prevent garbage collection
                    self.dialog.photo = photo
                    
                    # Update display
                    self.preview_label.config(image=photo)
        except Exception as e:
            print(f"Error updating preview: {str(e)}")
    
    def on_ok(self):
        """Handle OK button click"""
        self.result["cancelled"] = False
        self.result["caption"] = self.caption_var.get()
        self.result["label"] = self.label_var.get()
        self.result["width"] = self.width_var.get()  # LaTeX width
        self.result["filename"] = self.image_info["filename"]
        
        # Get pixel dimensions
        new_width = self.px_width_var.get()
        new_height = self.px_height_var.get()
        
        # Check if dimensions changed
        current_width = self.image_info.get("width", 0)
        current_height = self.image_info.get("height", 0)
        
        if (new_width != current_width or new_height != current_height) and new_width > 0 and new_height > 0:
            # Update the image in the database
            success, message = self.image_manager.update_image_dimensions(
                self.image_info["filename"], new_width, new_height)
            
            if success:
                self.result["dimensions_changed"] = True
            else:
                messagebox.showerror("Error", f"Failed to update image dimensions: {message}")
        
        # Call the on_apply callback if provided
        if self.on_apply:
            self.on_apply(self.result)
        
        self.dialog.destroy()
    
    def on_cancel(self):
        """Handle Cancel button click"""
        self.dialog.destroy()


class ImageSizeAdjustDialog:
    """Dialog for adjusting the size of an existing image in the document"""
    
    def __init__(self, parent, editor, image_manager, image_filename, current_width=0.8):
        """
        Initialize the image size adjustment dialog
        
        Args:
            parent: Parent widget
            editor: Editor component to update
            image_manager: The ImageManager instance
            image_filename (str): Filename of the image to adjust
            current_width (float): Current LaTeX width (0.0-1.0)
        """
        self.parent = parent
        self.editor = editor
        self.image_manager = image_manager
        self.filename = image_filename
        
        # Get current image dimensions
        success, image = image_manager.image_db.get_image(image_filename)
        self.current_pixel_width = 0
        self.current_pixel_height = 0
        self.original_width = 0
        self.original_height = 0
        
        if success:
            self.current_pixel_width, self.current_pixel_height = image.size
            self.original_width, self.original_height = self.current_pixel_width, self.current_pixel_height
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Adjust Image Size")
        self.dialog.geometry("450x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create variables
        self.width_var = tk.DoubleVar(value=current_width)
        self.px_width_var = tk.IntVar(value=self.current_pixel_width)
        self.px_height_var = tk.IntVar(value=self.current_pixel_height)
        self.maintain_aspect_var = tk.BooleanVar(value=True)
        
        # Create the dialog UI
        self.create_widgets()
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
    
    def create_widgets(self):
        """Create the dialog widgets"""
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Image info
        ttk.Label(frame, text=f"Image: {self.filename}").pack(anchor=tk.W, padx=5, pady=5)
        
        # LaTeX Width adjustment
        latex_frame = ttk.LabelFrame(frame, text="LaTeX Document Width")
        latex_frame.pack(fill=tk.X, padx=5, pady=10)
        
        ttk.Label(latex_frame, text="Width (0.1-1.0 × text width):").pack(anchor=tk.W, padx=5, pady=5)
        width_scale = ttk.Scale(latex_frame, from_=0.1, to=1.0, variable=self.width_var, orient=tk.HORIZONTAL)
        width_scale.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a label to show the current value
        value_label = ttk.Label(latex_frame, text=f"Current width: {self.width_var.get():.2f} × text width")
        value_label.pack(anchor=tk.E, padx=5, pady=5)
        
        # Update the label when the scale changes
        def update_value_label(event=None):
            value_label.config(text=f"Current width: {self.width_var.get():.2f} × text width")
        
        width_scale.bind("<Motion>", update_value_label)
        width_scale.bind("<ButtonRelease-1>", update_value_label)
        
        # Pixel dimensions section
        dimension_frame = ttk.LabelFrame(frame, text="Image Dimensions (pixels)")
        dimension_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Width input
        width_frame = ttk.Frame(dimension_frame)
        width_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(width_frame, text="Width:").pack(side=tk.LEFT, padx=5)
        width_entry = ttk.Entry(width_frame, textvariable=self.px_width_var, width=6)
        width_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(width_frame, text="px").pack(side=tk.LEFT)
        
        # Height input
        height_frame = ttk.Frame(dimension_frame)
        height_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(height_frame, text="Height:").pack(side=tk.LEFT, padx=5)
        height_entry = ttk.Entry(height_frame, textvariable=self.px_height_var, width=6)
        height_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(height_frame, text="px").pack(side=tk.LEFT)
        
        # Maintain aspect ratio checkbox
        aspect_check = ttk.Checkbutton(dimension_frame, text="Maintain aspect ratio", 
                                     variable=self.maintain_aspect_var)
        aspect_check.pack(anchor=tk.W, padx=5, pady=5)
        
        # Original dimensions info
        if self.original_width > 0 and self.original_height > 0:
            original_label = ttk.Label(dimension_frame, 
                                    text=f"Original dimensions: {self.original_width}×{self.original_height} px")
            original_label.pack(anchor=tk.W, padx=5, pady=5)
            
            # Reset button
            reset_button = ttk.Button(dimension_frame, text="Reset to Original", command=self.reset_to_original)
            reset_button.pack(pady=5)
        
        # Preview
        preview_frame = ttk.LabelFrame(frame, text="Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=10)
        
        # Create a frame for the preview image
        image_frame = ttk.Frame(preview_frame)
        image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image preview label
        self.preview_label = ttk.Label(image_frame)
        self.preview_label.pack(expand=True)
        
        # Initial preview update
        self.update_preview()
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ok_button = ttk.Button(button_frame, text="Apply", command=self.on_ok)
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self.on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Bind the trace callbacks
        self.px_width_var.trace_add("write", self.on_width_change)
        self.px_height_var.trace_add("write", self.on_height_change)
    
    def on_width_change(self, *args):
        """Handle width change while preserving aspect ratio"""
        if self.maintain_aspect_var.get() and self.original_width > 0 and self.original_height > 0:
            # Calculate new height based on width while preserving aspect ratio
            aspect_ratio = self.original_height / self.original_width
            new_height = int(self.px_width_var.get() * aspect_ratio)
            self.px_height_var.set(new_height)
            
            # Update preview
            self.update_preview()
    
    def on_height_change(self, *args):
        """Handle height change while preserving aspect ratio"""
        if self.maintain_aspect_var.get() and self.original_width > 0 and self.original_height > 0:
            # Calculate new width based on height while preserving aspect ratio
            aspect_ratio = self.original_width / self.original_height
            new_width = int(self.px_height_var.get() * aspect_ratio)
            self.px_width_var.set(new_width)
            
            # Update preview
            self.update_preview()
    
    def reset_to_original(self):
        """Reset dimensions to original values"""
        self.px_width_var.set(self.original_width)
        self.px_height_var.set(self.original_height)
        
        # Update image preview
        self.update_preview()
    
    def update_preview(self):
        """Update the image preview"""
        try:
            success, image = self.image_manager.image_db.get_image(self.filename)
            if success:
                new_width = self.px_width_var.get()
                new_height = self.px_height_var.get()
                
                if new_width > 0 and new_height > 0:
                    # Create a copy before resizing to avoid modifying the original
                    preview_img = image.copy()
                    preview_img = preview_img.resize((new_width, new_height), Image.LANCZOS)
                    
                    # Scale down further if needed for display
                    max_preview_size = (400, 300)
                    if preview_img.width > max_preview_size[0] or preview_img.height > max_preview_size[1]:
                        preview_img.thumbnail(max_preview_size)
                    
                    # Convert to PhotoImage for display
                    photo = ImageTk.PhotoImage(preview_img)
                    
                    # Store reference to prevent garbage collection
                    self.dialog.photo = photo
                    
                    # Update display
                    self.preview_label.config(image=photo)
        except Exception as e:
            print(f"Error updating preview: {str(e)}")
    
    def on_ok(self):
        """Handle OK button click"""
        try:
            # Get LaTeX width
            new_latex_width = self.width_var.get()
            
            # Get pixel dimensions
            new_width = self.px_width_var.get()
            new_height = self.px_height_var.get()
            
            # Check if dimensions changed
            dimensions_changed = (new_width != self.current_pixel_width or new_height != self.current_pixel_height) and new_width > 0 and new_height > 0
            
            # Get the content from the editor
            content = self.editor.get_content()
            
            # Try with a more direct search
            include_pattern = r'\\includegraphics(\[.*?\])?\{' + re.escape(self.filename) + r'\}'
            match = re.search(include_pattern, content)
            
            if not match:
                print("Could not find the image tag in the document")
                print(f"Searching for pattern: {include_pattern}")
                print(f"In content of length: {len(content)}")
                
                # Try a more basic search as last resort
                simple_pattern = r'\\includegraphics.*?\{' + re.escape(self.filename) + r'\}'
                match = re.search(simple_pattern, content)
                
                if not match:
                    messagebox.showerror("Error", "Could not locate the image in the document for updating.")
                    self.dialog.destroy()
                    return
            
            # Get the exact original tag
            original_tag = match.group(0)
            print(f"Original tag: {original_tag}")
            
            # Create new tag with width
            new_image_tag = f"\\includegraphics[width={new_latex_width}\\textwidth]{{{self.filename}}}"
            print(f"New image tag: {new_image_tag}")
            
            # Use simple string replacement
            new_content = content.replace(original_tag, new_image_tag)
            
            # Check if replacement worked
            if new_content == content:
                print("Warning: Content was not modified by string replacement")
                print(f"Original tag length: {len(original_tag)}")
                print(f"New tag length: {len(new_image_tag)}")
                messagebox.showerror("Error", "Failed to update the image size.")
                self.dialog.destroy()
                return
            
            # If pixel dimensions changed, resize the image in the database
            if dimensions_changed:
                success, result = self.image_manager.update_image_dimensions(
                    self.filename, new_width, new_height)
                
                if not success:
                    messagebox.showerror("Error", f"Failed to update image dimensions: {result}")
            
            # Update editor content
            self.editor.set_content(new_content)
            
            # Close the dialog
            self.dialog.destroy()
            
            # Return success message
            if dimensions_changed:
                return f"Image resized to {new_width}×{new_height}px and LaTeX width set to {new_latex_width:.2f}×textwidth"
            else:
                return f"Image LaTeX width updated to {new_latex_width:.2f}×textwidth"
            
        except Exception as e:
            print(f"Error updating image: {str(e)}")
            messagebox.showerror("Error", f"Failed to update image: {str(e)}")
            return None
    
    def on_cancel(self):
        """Handle Cancel button click"""
        self.dialog.destroy()