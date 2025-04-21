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


class ImageManager:
    """Manages image operations for the Simplified Math Editor"""
    
    def __init__(self, app):
        """
        Initialize the image manager
        
        Args:
            app: Reference to the MathEditor instance
        """
        self.app = app
    
    def get_clipboard_image(self):
        """
        Get image from clipboard
        
        Returns:
            PIL.Image or None: Image object if found, None otherwise
        """
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
        """
        Paste image from clipboard as LaTeX figure
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Try to get image from clipboard
            clipboard_image = self.get_clipboard_image()
            
            if not clipboard_image:
                messagebox.showinfo("No Image", 
                                   "No image found in clipboard.\n\n"
                                   "Note: The application can only access images that are\n"
                                   "copied as images, not as files or other formats.")
                return False
            
            # Process the image (store in database)
            success, result = self.app.image_converter.process_image(clipboard_image)
            
            if not success:
                messagebox.showerror("Image Processing Error", result)
                return False
            
            # Create a dialog to get caption and width
            image_info = self.get_image_details(result)
            if not image_info:
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
            return True
            
        except Exception as e:
            messagebox.showerror("Image Error", str(e))
            return False
    
    def insert_image_from_file(self):
        """
        Insert an image from a file
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Ask for image file
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return False
        
        try:
            # Process the image
            success, result = self.app.image_converter.process_image(file_path)
            
            if not success:
                messagebox.showerror("Image Processing Error", result)
                return False
            
            # Create a dialog to get caption and width
            image_info = self.get_image_details(result)
            if not image_info:
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
            return True
            
        except Exception as e:
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
        dialog.geometry("400x500")
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
        Show dialog to adjust the size of the image in the document
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Check if there's an image in the document
        content = self.app.editor.get_content()
        
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
                return False
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
        dialog = tk.Toplevel(self.app.root)
        dialog.title("Adjust Image Size")
        dialog.geometry("400x300")
        dialog.transient(self.app.root)
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
            success, image = self.app.image_converter.image_db.get_image(filename)
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
                return False
            
            # Get the exact original tag
            original_tag = match.group(0)
            print(f"Original tag: {original_tag}")
            
            # Create new tag - use string concatenation to avoid regex interpretation issues
            max_height = self.app.config_manager.get_value("image", "default_max_height", 800)
            new_image_tag = "\\includegraphics[width=" + str(new_width) + "\\textwidth,height=" + str(max_height) + "px,keepaspectratio]{" + filename + "}"
            print(f"New image tag: {new_image_tag}")
            
            # Use simple string replacement instead of regex replacement
            new_content = content.replace(original_tag, new_image_tag)
            
            # Check if replacement worked
            if new_content == content:
                print("Warning: Content was not modified by string replacement")
                messagebox.showerror("Error", "Failed to update the image size.")
                dialog.destroy()
                return False
            
            # Update editor content
            self.app.editor.set_content(new_content)
            
            # Update preview
            self.app.update_preview()
            
            dialog.destroy()
            self.app.status_var.set(f"Image size updated to {new_width:.2f}×textwidth")
            return True
        
        def on_cancel():
            dialog.destroy()
            return False
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        ok_button = ttk.Button(button_frame, text="Apply", command=on_ok)
        ok_button.pack(side=tk.RIGHT, padx=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=on_cancel)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Wait for dialog to close (the result will be determined by the callbacks)
        return True