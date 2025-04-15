"""
Demo of storing images in a database and using them in LaTeX documents.

This script:
1. Creates a database
2. Stores a test image in the database
3. Creates a LaTeX document that references the image
4. Extracts the image from the database for LaTeX compilation
5. Compiles the LaTeX document

Usage:
- Run the script with a path to any image file: python latex_db_image_demo.py path/to/image.jpg
- The script will store the image in the database, generate a LaTeX document, 
  and compile it to a PDF.
"""

import sqlite3
import io
import sys
import os
import re
import subprocess
import tempfile
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
    return output_path

def create_latex_document(image_name, caption="Test Image"):
    """Create a LaTeX document that includes the image"""
    latex = r"""
\documentclass{article}
\usepackage{graphicx}
\usepackage{amsmath}
\usepackage{amssymb}

% Set up image path
\graphicspath{{./}}

\begin{document}

\section{Test Document}

This is a test document that includes an image from the database.

\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{""" + image_name + r"""}
    \caption{""" + caption + r"""}
    \label{fig:test-image}
\end{figure}

The figure above shows our test image.

\end{document}
"""
    
    return latex

def compile_latex(latex_content, output_dir):
    """Compile a LaTeX document to PDF"""
    # Create a temporary directory for compilation
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Write the LaTeX content to a file
    tex_file = os.path.join(output_dir, "test_document.tex")
    with open(tex_file, "w", encoding="utf-8") as f:
        f.write(latex_content)
    
    # Run pdflatex
    try:
        # Save current directory
        current_dir = os.getcwd()
        
        # Change to the output directory
        os.chdir(output_dir)
        
        # Run pdflatex
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "test_document.tex"],
            capture_output=True,
            text=True
        )
        
        # Restore original directory
        os.chdir(current_dir)
        
        # Check if compilation was successful
        pdf_file = os.path.join(output_dir, "test_document.pdf")
        if os.path.exists(pdf_file):
            print(f"LaTeX compilation successful. PDF saved to: {pdf_file}")
            return pdf_file
        else:
            print("LaTeX compilation failed.")
            print("Error output:")
            print(result.stdout)
            print(result.stderr)
            return None
            
    except Exception as e:
        print(f"Error compiling LaTeX: {str(e)}")
        return None

def extract_images_from_latex(cursor, latex_content, output_dir):
    """Extract images from the database for LaTeX compilation"""
    # Find all image filenames in the LaTeX content
    image_pattern = r'\\includegraphics\[.*?\]{(.*?)}'
    image_filenames = re.findall(image_pattern, latex_content)
    
    if not image_filenames:
        print("No images found in LaTeX content")
        return
    
    print(f"Found {len(image_filenames)} images in LaTeX content")
    
    # Extract each image from the database and save to output directory
    for image_name in image_filenames:
        print(f"Extracting image: {image_name}")
        img = retrieve_image(cursor, image_name)
        
        if img:
            output_path = os.path.join(output_dir, image_name)
            export_image(img, output_path)
        else:
            print(f"WARNING: Image {image_name} not found in database")

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("Usage: python latex_db_image_demo.py path/to/image.jpg")
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
    
    # Create a directory in the current working directory for output
    output_dir = os.path.join(os.getcwd(), "latex_test_output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    print(f"Using output directory: {output_dir}")
    
    # Create LaTeX document
    latex_content = create_latex_document(image_name)
    
    # Extract images for compilation
    extract_images_from_latex(cursor, latex_content, output_dir)
    
    # Compile LaTeX document
    pdf_file = compile_latex(latex_content, output_dir)
    
    # Close connection
    conn.close()
    
    if pdf_file:
        print(f"\nSuccess! PDF created at: {pdf_file}")
        print("Please open the PDF manually at the path shown above")
    
    print("Done!")

if __name__ == "__main__":
    main()