"""
Image to LaTeX figure conversion for the Simplified Math Editor.

This module provides functionality to convert images to LaTeX figure environments
and handle image storage and references using a database.
"""

import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import base64
import uuid
from pathlib import Path
import shutil
import tempfile
from db.math_image_db import MathImageDB

class ImageConverter:
    """Converts images to LaTeX figure environments with database storage"""
    
    def __init__(self, working_dir=None, config_manager=None):
        """
        Initialize the image converter
        
        Args:
            working_dir (str, optional): Working directory for temporary image storage.
                                       If None, './temp' will be used.
            config_manager: Configuration manager instance for accessing app settings
        """
        if working_dir:
            self.working_dir = Path(working_dir)
        else:
            self.working_dir = Path("temp")
        
        # Create the images directory if it doesn't exist
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        # Store the configuration manager
        self.config_manager = config_manager
        
        # Initialize the image database
        self.image_db = MathImageDB()
        
        # Keep track of images used in the current document
        self.document_images = {}
    
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
    
    def get_image_from_clipboard(self):
        """
        Get an image from the clipboard
        
        Returns:
            tuple: (success, image_data or error_message)
        """
        try:
            # Try to get image from clipboard
            image = self.get_clipboard_image()
            
            if not image:
                return (False, "No image found in clipboard")
            
            return (True, image)
            
        except Exception as e:
            return (False, str(e))
    
    def create_latex_figure(self, image_path, caption="", label="", width=0.8, align=None, margin=None):
        """
        Create a LaTeX figure environment for an image using adjustbox for placement.
        Args:
            image_path (str): Path or name of the image file
            caption (str): Figure caption
            label (str): Figure label (for referencing)
            width (float): Width as a fraction of the text width (0.0-1.0)
            align (str, optional): adjustbox alignment option ('left', 'center', 'right'). Defaults to config or 'left'.
            margin (str, optional): adjustbox margin option (e.g., '1cm 0pt 0pt 0pt'). Defaults to config or None.
        Returns:
            str: LaTeX figure environment code
        """
        # Create a default label if none provided
        if not label:
            label = f"fig:{Path(image_path).stem}"

        # Use only filename instead of full path to avoid LaTeX issues
        image_filename = Path(image_path).name

        # Get the configured maximum height (default to 800 if not configured)
        max_height = 800
        if self.config_manager:
            max_height = self.config_manager.get_value("image", "default_max_height", 800)

        # Get the configured caption behavior
        caption_behavior = "none"
        if self.config_manager:
            caption_behavior = self.config_manager.get_value("image", "caption_behavior", "none")

        # If caption behavior is "filename" and no caption provided, use the filename
        if caption_behavior == "filename" and not caption:
            caption = Path(image_filename).stem

        # Get alignment and margin from config if not provided
        if align is None:
            align = self.config_manager.get_value("image", "default_align", "left") if self.config_manager else "left"
        if margin is None:
            margin = self.config_manager.get_value("image", "default_margin", None) if self.config_manager else None

        # Use new default: height=6.00cm, left, margin=4.00cm 0.00cm 0cm 0.50cm
        height = 6.00
        left_margin = 4.00
        top_margin = 0.00
        bottom_margin = 0.00
        right_margin = 0.50
        adjustbox_opts = [f"height={height:.2f}cm", "left", f"margin={left_margin:.2f}cm {bottom_margin:.2f}cm {top_margin:.2f}cm {right_margin:.2f}cm"]
        adjustbox_opts_str = ",".join(adjustbox_opts)

        # Use adjustbox for image placement
        latex = (
            f"\\begin{{figure}}[htbp]\n"
            f"    \\centering\n"
            f"    \\adjustbox{{{adjustbox_opts_str}}}{{\\includegraphics[keepaspectratio]{{{image_filename}}}}}\n"
        )
        # Add caption based on caption behavior
        if caption_behavior != "none" and (caption or caption_behavior == "empty"):
            latex += "    \\caption{" + caption + "}\n"
        # Add label if provided
        if label:
            latex += "    \\label{" + label + "}\n"
        # Close the figure environment
        latex += "\\end{figure}\n"
        return latex
    
    def process_image(self, image_data, filename=None):
        """
        Process an image and store it in the database
        
        Args:
            image_data: PIL Image object or path to image file
            filename (str, optional): Desired filename (without extension)
            
        Returns:
            tuple: (success, image_info or error_message)
        """
        try:
            # Generate a unique filename if none provided
            if not filename:
                filename = f"image_{uuid.uuid4().hex[:8]}"
            
            # Ensure the filename is safe
            filename = ''.join(c for c in filename if c.isalnum() or c in '-_')
            
            # Load the image if path is provided
            if isinstance(image_data, str):
                image = Image.open(image_data)
            else:
                image = image_data
            
            # Get image dimensions
            width, height = image.size
            
            # Store in database only, not as file
            image_name = f"{filename}.png"
            success, result = self.image_db.store_image(image, image_name)
            
            if not success:
                return (False, result)
            
            # Create a virtual path reference (no actual file created)
            virtual_path = self.working_dir / image_name
            
            # Return the image information
            image_info = {
                "path": str(virtual_path),  # Virtual path for reference only
                "filename": image_name,
                "width": width,
                "height": height
            }
            
            # Add to document images
            self.document_images[filename] = image_info
            
            return (True, image_info)
            
        except Exception as e:
            return (False, str(e))
    
    def clean_unused_images(self, used_images):
        """
        Remove images that are no longer used in the document
        
        Args:
            used_images (list): List of image filenames used in the document
        """
        # This method now cleans temporary files only
        # Get all image files in the working directory
        image_files = list(self.working_dir.glob("*.png"))
        
        # Remove unused images (temporary files)
        for image_file in image_files:
            if image_file.name not in used_images:
                try:
                    image_file.unlink()
                except:
                    pass  # Ignore errors deleting files
    
    def export_images(self, target_dir):
        """
        Export all images used in the document from database to a target directory
        
        Args:
            target_dir (str): Target directory path
            
        Returns:
            tuple: (success, message)
        """
        try:
            target_path = Path(target_dir)
            target_path.mkdir(parents=True, exist_ok=True)
            
            # Export all images from database to files
            exported = 0
            failed = 0
            
            for image_info in self.document_images.values():
                image_name = image_info["filename"]
                target_file = target_path / image_name
                
                # Export from database
                success, result = self.image_db.export_to_file(image_name, str(target_file))
                
                if success:
                    exported += 1
                else:
                    failed += 1
            
            return (True, f"Exported {exported} images to {target_dir}, {failed} failed")
            
        except Exception as e:
            return (False, str(e))