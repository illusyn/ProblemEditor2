"""
Image manager for the Simplified Math Editor.

This module provides functionality to handle image operations including:
- Processing and storing images
- Converting images to LaTeX figure environments
- Managing image dimensions and constraints
"""

import os
import uuid
from pathlib import Path
import tempfile
from PIL import Image
from math_image_db import MathImageDB

class ImageManager:
    """Manages all image operations for the Math Editor"""
    
    def __init__(self, working_dir=None, max_width=600, max_height=800):
        """
        Initialize the image manager
        
        Args:
            working_dir (str, optional): Working directory for temporary image storage.
                                       If None, a temporary directory will be used.
            max_width (int): Maximum default width for images
            max_height (int): Maximum default height for images
        """
        if working_dir:
            self.working_dir = Path(working_dir)
        else:
            # Create a temporary directory for image storage
            self.working_dir = Path(tempfile.gettempdir()) / "simplified_math_editor" / "images"
        
        # Create the images directory if it doesn't exist
        self.working_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize the image database
        self.image_db = MathImageDB()
        
        # Keep track of images used in the current document
        self.document_images = {}
        
        # Default size constraints
        self.max_width = max_width
        self.max_height = max_height
    
    def get_clipboard_image(self):
        """
        Get image from clipboard
        
        Returns:
            PIL.Image or None: Image from clipboard or None if not found
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
            print("PIL ImageGrab module not available")
            return None
        except Exception as e:
            print(f"Clipboard error: {str(e)}")
            return None
    
    def process_image(self, image_data, filename=None):
        """
        Process an image and store it in the database, resizing if necessary
        
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
            
            # Get original image dimensions
            orig_width, orig_height = image.size
            
            # Calculate if resizing is needed while preserving aspect ratio
            if orig_width > self.max_width or orig_height > self.max_height:
                # Calculate scaling factors
                width_ratio = self.max_width / orig_width
                height_ratio = self.max_height / orig_height
                
                # Use the smaller ratio to ensure both dimensions fit within limits
                scale_factor = min(width_ratio, height_ratio)
                
                # Calculate new dimensions
                new_width = int(orig_width * scale_factor)
                new_height = int(orig_height * scale_factor)
                
                # Resize the image
                image = image.resize((new_width, new_height), Image.LANCZOS)
                
                # Get new dimensions after resize
                width, height = image.size
            else:
                width, height = orig_width, orig_height
            
            # Store in database
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
                "height": height,
                "original_width": orig_width,
                "original_height": orig_height,
                "was_resized": (orig_width != width or orig_height != height)
            }
            
            # Add to document images
            self.document_images[filename] = image_info
            
            return (True, image_info)
            
        except Exception as e:
            return (False, str(e))
    
    def update_image_dimensions(self, image_name, width, height):
        """
        Update the dimensions of an image in the database
        
        Args:
            image_name (str): Name of the image
            width (int): New width in pixels
            height (int): New height in pixels
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Get the image from database
            success, image = self.image_db.get_image(image_name)
            
            if not success:
                return (False, f"Image not found: {image_name}")
            
            # Resize the image
            resized_img = image.resize((width, height), Image.LANCZOS)
            
            # Store the resized image
            success, result = self.image_db.store_image(resized_img, image_name)
            
            if not success:
                return (False, result)
                
            return (True, f"Image dimensions updated to {width}×{height}px")
            
        except Exception as e:
            return (False, str(e))
    
    def create_latex_figure(self, image_path, caption="", label="", width=0.8):
        """
        Create a LaTeX figure environment for an image
        
        Args:
            image_path (str): Path or name of the image file
            caption (str): Figure caption
            label (str): Figure label (for referencing)
            width (float): Width as a fraction of the text width (0.0-1.0)
            
        Returns:
            str: LaTeX figure environment code
        """
        # Create a default label if none provided
        if not label:
            label = f"fig:{Path(image_path).stem}"

        # Use only filename instead of full path to avoid LaTeX issues
        image_filename = Path(image_path).name
        
        # Create the LaTeX figure environment
        latex = r"""
    \begin{figure}[htbp]
        \centering
        \includegraphics[width=""" + str(width) + r"""\textwidth]{""" + image_filename + r"""}
        \caption{""" + caption + r"""}
        \label{""" + label + r"""}
    \end{figure}
    """
        
        return latex
    
    def extract_images_for_compilation(self, destination_dir, image_filenames):
        """
        Extract images from the database to the specified directory for LaTeX compilation
        
        Args:
            destination_dir (str or Path): Directory to save the images
            image_filenames (list): List of image filenames to extract
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Create destination directory if it doesn't exist
            dest_dir = Path(destination_dir)
            dest_dir.mkdir(exist_ok=True)
            
            # Create images subdirectory
            images_dir = dest_dir / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Extract and save each image
            success_count = 0
            error_messages = []
            
            for image_name in image_filenames:
                # Remove any extra whitespace or newlines
                image_name = image_name.strip()
                
                # Get the image from the database
                success, img = self.image_db.get_image(image_name)
                
                if not success:
                    # Try with common image extensions if the name doesn't have one
                    if '.' not in image_name:
                        for ext in ['.png', '.jpg', '.jpeg', '.gif']:
                            success, img = self.image_db.get_image(image_name + ext)
                            if success:
                                image_name = image_name + ext
                                break
                
                if not success:
                    error_messages.append(f"Failed to retrieve image from database: {image_name}")
                    continue
                
                try:
                    # Save to main directory
                    main_path = dest_dir / image_name
                    # Get format from file extension or use PNG as default
                    format_ext = os.path.splitext(image_name)[1][1:].upper() or 'PNG'
                    img.save(str(main_path), format=format_ext)
                    
                    # Save to images subdirectory
                    subdir_path = images_dir / image_name
                    img.save(str(subdir_path), format=format_ext)
                    
                    success_count += 1
                except Exception as e:
                    error_messages.append(f"Failed to save image {image_name}: {str(e)}")
            
            # Return success if at least one image was extracted, otherwise False
            if success_count > 0:
                message = f"Extracted {success_count} of {len(image_filenames)} images"
                if error_messages:
                    message += f" with {len(error_messages)} errors"
                return (True, message)
            else:
                return (False, "\n".join(error_messages))
            
        except Exception as e:
            return (False, str(e))
    
    def clean_unused_images(self, used_images):
        """
        Remove images that are no longer used in the document
        
        Args:
            used_images (list): List of image filenames used in the document
        """
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