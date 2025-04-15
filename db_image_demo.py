"""
Simple demonstration of storing and retrieving images in an SQLite database.

This script:
1. Creates a database
2. Stores a test image in the database
3. Retrieves the image from the database
4. Saves it to disk for verification

Usage:
- Run the script with a path to any image file: python db_image_demo.py path/to/image.jpg
- The script will store the image in the database and then extract it again
"""

import sqlite3
import io
import sys
import os
from PIL import Image
from pathlib import Path

def create_database(db_path):
    """Create an SQLite database for storing images"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create image table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            data BLOB,
            width INTEGER,
            height INTEGER,
            format TEXT
        )
    ''')
    conn.commit()
    
    return conn, cursor

def store_image(conn, cursor, image_path, image_name=None):
    """Store an image in the database"""
    # Open the image
    img = Image.open(image_path)
    width, height = img.size
    format = img.format or "PNG"
    
    # If no name provided, use the filename
    if not image_name:
        image_name = Path(image_path).name
    
    # Convert image to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=format)
    img_data = img_bytes.getvalue()
    
    # Store in database
    cursor.execute(
        "INSERT OR REPLACE INTO images (name, data, width, height, format) VALUES (?, ?, ?, ?, ?)",
        (image_name, img_data, width, height, format)
    )
    conn.commit()
    
    print(f"Stored image: {image_name} ({width}x{height}, {format})")
    return image_name

def retrieve_image(cursor, image_name):
    """Retrieve an image from the database"""
    cursor.execute("SELECT data, width, height, format FROM images WHERE name = ?", (image_name,))
    result = cursor.fetchone()
    
    if not result:
        print(f"Image not found: {image_name}")
        return None
    
    img_data, width, height, format = result
    img = Image.open(io.BytesIO(img_data))
    
    print(f"Retrieved image: {image_name} ({width}x{height}, {format})")
    return img

def export_image(img, output_path):
    """Save the image to a file"""
    img.save(output_path)
    print(f"Saved image to: {output_path}")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python db_image_demo.py path/to/image.jpg")
        return
    
    image_path = sys.argv[1]
    if not os.path.exists(image_path):
        print(f"File not found: {image_path}")
        return
    
    # Create database
    db_path = "image_test.db"
    conn, cursor = create_database(db_path)
    
    # Store image
    image_name = store_image(conn, cursor, image_path)
    
    # Retrieve image
    img = retrieve_image(cursor, image_name)
    
    if img:
        # Export to a file with "_retrieved" added to the name
        output_path = f"{Path(image_path).stem}_retrieved{Path(image_path).suffix}"
        export_image(img, output_path)
    
    # Close connection
    conn.close()
    
    print("Done!")

if __name__ == "__main__":
    main()