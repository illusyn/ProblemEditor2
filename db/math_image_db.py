"""
Simple image database for the Simplified Math Editor.

This module provides functionality to store and retrieve images as BLOBs
in an SQLite database.
"""

import sqlite3
import io
from PIL import Image
from pathlib import Path
import os
import tempfile

class MathImageDB:
    """Simple database for storing images as BLOBs"""
    
    def __init__(self, db_path=None):
        """
        Initialize the image database
        
        Args:
            db_path (str, optional): Path to the SQLite database file.
                                    If None, a default path will be used.
        """
        if db_path is None:
            # Use a default location in the /db folder
            db_dir = Path("db")
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "math_images.db"
            
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        
        # Create tables if they don't exist
        self._create_tables()
    
    def _create_tables(self):
        """Create the necessary database tables if they don't exist"""
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                data BLOB,
                width INTEGER,
                height INTEGER,
                format TEXT
            )
        ''')
        self.conn.commit()
    
    def store_image(self, image, name=None):
        """
        Store an image in the database
        
        Args:
            image: PIL Image object or path to image file
            name (str, optional): Name for the image. If None, a name will be generated.
            
        Returns:
            tuple: (success, image_name or error_message)
        """
        try:
            # Convert to PIL Image if path provided
            if isinstance(image, str) and os.path.isfile(image):
                image = Image.open(image)
                
            # Get image properties
            width, height = image.size
            format = image.format or "PNG"
            
            # Convert image to bytes
            img_bytes = io.BytesIO()
            image.save(img_bytes, format=format)
            img_data = img_bytes.getvalue()
            
            # Generate a name if not provided
            if not name:
                # Query for the highest ID to generate the next one
                self.cur.execute("SELECT MAX(id) FROM images")
                result = self.cur.fetchone()
                next_id = 1 if result[0] is None else result[0] + 1
                name = f"image_{next_id:08d}.{format.lower()}"
            
            # Store in database
            self.cur.execute('''
                INSERT OR REPLACE INTO images (name, data, width, height, format)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, img_data, width, height, format))
            self.conn.commit()
            
            return (True, name)
            
        except Exception as e:
            return (False, str(e))
    
    def get_image(self, name):
        """
        Get an image by name
        
        Args:
            name (str): The image name
            
        Returns:
            tuple: (success, PIL Image or error_message)
        """
        try:
            self.cur.execute("SELECT data, format FROM images WHERE name = ?", (name,))
            result = self.cur.fetchone()
            
            if not result:
                return (False, f"Image not found in database: {name}")
            
            img_data, format = result
            img = Image.open(io.BytesIO(img_data))
            
            # Store original format information
            if format and not img.format:
                img.format = format
            
            return (True, img)
            
        except Exception as e:
            return (False, str(e))
    
    def export_to_file(self, name, output_path):
        """
        Export an image from the database to a file
        
        Args:
            name (str): The image name
            output_path (str): Path to save the file
            
        Returns:
            tuple: (success, file_path or error_message)
        """
        try:
            success, result = self.get_image(name)
            if not success:
                return (False, result)
            
            # Ensure parent directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Get format from image name if available
            format = None
            file_ext = os.path.splitext(name)[1].lower()
            if file_ext:
                # Remove the dot and convert to uppercase
                format = file_ext[1:].upper()
            
            # Use image's format if available
            if not format and hasattr(result, 'format') and result.format:
                format = result.format
                
            # Default to PNG if no format is determined
            if not format:
                format = 'PNG'
            
            # Save to file
            result.save(output_path, format=format)
            
            return (True, output_path)
            
        except Exception as e:
            return (False, str(e))
    
    def get_all_image_names(self):
        """
        Get a list of all image names in the database
        
        Returns:
            list: List of image names
        """
        self.cur.execute("SELECT name FROM images ORDER BY id")
        return [row[0] for row in self.cur.fetchall()]
    
    def delete_image(self, name):
        """
        Delete an image from the database
        
        Args:
            name (str): The image name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.cur.execute("DELETE FROM images WHERE name = ?", (name,))
            self.conn.commit()
            return True
        except:
            return False
    
    def close(self):
        """Close the database connection"""
        if self.conn:
            self.conn.close()