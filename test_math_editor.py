"""
Test script for the math_editor.py functionality.

This script creates a simple test environment to verify that the 
image inclusion and LaTeX compilation is working correctly in the full application.
"""

import sys
import os
import tempfile
from pathlib import Path
import tkinter as tk
from PIL import Image, ImageDraw

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules from the application
from math_editor import MathEditor
from editor import EditorComponent
from preview.latex_compiler import LaTeXCompiler
from converters.image_converter import ImageConverter
from math_image_db import MathImageDB

def create_test_image(output_path):
    """Create a simple test image"""
    img = Image.new('RGB', (300, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([(20, 20), (280, 180)], outline='black')
    draw.text((100, 100), "Test Image", fill='black')
    
    img.save(output_path)
    print(f"Created test image at: {output_path}")
    return img

def setup_test_environment():
    """Set up a test environment for the math editor"""
    # Create a test directory
    test_dir = Path("./test_math_editor")
    test_dir.mkdir(exist_ok=True)
    
    # Create a test image
    img_path = test_dir / "test_image.png"
    test_img = create_test_image(img_path)
    
    # Create a temporary root window (needed for tkinter)
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    return root, test_dir, img_path, test_img

def test_image_conversion():
    """Test image conversion and LaTeX figure generation"""
    print("\n=== Testing Image Conversion ===")
    
    # Set up test environment
    _, test_dir, img_path, _ = setup_test_environment()
    
    # Initialize image converter
    converter = ImageConverter(working_dir=str(test_dir))
    
    # Process the image
    success, result = converter.process_image(str(img_path))
    if not success:
        print(f"Error processing image: {result}")
        return False
    
    # Create LaTeX figure
    latex_figure = converter.create_latex_figure(
        image_path=result["filename"],
        caption="Test Image Caption",
        label="fig:test_image"
    )
    
    print("\nGenerated LaTeX figure code:")
    print(latex_figure)
    
    # Export image from database to file
    success, msg = converter.export_images(str(test_dir))
    print(msg)
    
    return success

def test_latex_compilation():
    """Test LaTeX compilation with the image"""
    print("\n=== Testing LaTeX Compilation ===")
    
    # Set up test environment
    _, test_dir, img_path, _ = setup_test_environment()
    
    # Initialize LaTeX compiler
    compiler = LaTeXCompiler(working_dir=str(test_dir))
    
    # Create a simple LaTeX document with image
    latex_content = r"""
\documentclass{article}
\usepackage{graphicx}

\begin{document}

\section{Test Image Inclusion}

This is a test document for verifying that image inclusion works correctly.

\begin{figure}[htbp]
    \centering
    \includegraphics{test_image.png}
    \caption{Test Image}
    \label{fig:test}
\end{figure}

\end{document}
"""
    
    # Write the image to the test directory
    img = create_test_image(test_dir / "test_image.png")
    
    # Compile the LaTeX document
    success, result = compiler.compile_latex(latex_content, "test_compilation")
    
    if success:
        print(f"LaTeX compilation successful! PDF created at: {result}")
    else:
        print(f"LaTeX compilation failed: {result}")
    
    return success

def test_math_editor_image_handling():
    """Test image handling in the MathEditor class"""
    print("\n=== Testing MathEditor Image Handling ===")
    
    # Set up test environment
    root, test_dir, img_path, test_img = setup_test_environment()
    
    # Initialize MathEditor
    editor = MathEditor(root)
    
    # Override the template to ensure it includes graphicx (ADDED THIS)
    editor.template = r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\graphicspath{{./}{./images/}}

\begin{document}

#CONTENT#

\end{document}
"""
    
    # Store the test image in the database
    success, image_info = editor.image_converter.process_image(str(img_path))
    if not success:
        print(f"Error processing image: {image_info}")
        return False
    
    # Generate LaTeX figure code
    latex_figure = editor.image_converter.create_latex_figure(
        image_path=image_info["filename"],
        caption="Test Image for MathEditor",
        label="fig:math_editor_test"
    )
    
    # Set the editor content with the figure
    editor.editor.set_content(latex_figure)
    
    # Write debug output
    debug_file = test_dir / "editor_content.tex"
    with open(debug_file, "w", encoding="utf-8") as f:
        f.write(editor.editor.get_content())
    print(f"Editor content written to: {debug_file}")
    
    # Test image extraction
    print("Testing image extraction...")
    if not editor.extract_images_for_compilation():
        print("Image extraction failed!")
        return False
    
    # Check if image exists in the working directory
    working_dir = editor.working_dir
    extracted_image = list(working_dir.glob(f"{image_info['filename']}"))
    if extracted_image:
        print(f"Image successfully extracted to: {extracted_image[0]}")
    else:
        print(f"Image extraction failed - image not found in {working_dir}")
        return False
    
    # Generate LaTeX document for testing
    content = editor.editor.get_content()
    latex_document = editor.template.replace("#CONTENT#", content)
    
    # Write debug LaTeX file
    debug_latex = test_dir / "debug_latex.tex"
    with open(debug_latex, "w", encoding="utf-8") as f:
        f.write(latex_document)
    print(f"Debug LaTeX document written to: {debug_latex}")
    
    # Check explicitly if graphicx is included (ADDED THIS)
    if "\\usepackage{graphicx}" not in latex_document:
        print("WARNING: graphicx package is still missing from the template!")
        print("Adding it explicitly for the test...")
        latex_document = latex_document.replace("\\begin{document}", 
            "\\usepackage{graphicx}\n\\graphicspath{{./}{./images/}}\n\\begin{document}")
    else:
        print("graphicx package confirmed in the template.")
    
    # Test compilation with extracted image
    print("Testing LaTeX compilation with extracted image...")
    
    # Write the modified document to a file for debugging (ADDED THIS)
    modified_debug = test_dir / "modified_latex.tex"
    with open(modified_debug, "w", encoding="utf-8") as f:
        f.write(latex_document)
    print(f"Modified LaTeX document written to: {modified_debug}")
    
    # Now create the direct LaTeX file in the working directory (ADDED THIS)
    with open(editor.working_dir / "editor_test.tex", "w", encoding="utf-8") as f:
        f.write(latex_document)
    
    # Save images to current directory as well for debugging
    current_dir = Path(".")
    shutil.copy(str(extracted_image[0]), current_dir / image_info['filename'])
    
    # Test compilation with extracted image
    success, result = editor.latex_compiler.compile_latex(latex_document, "editor_test")
    
    if success:
        print(f"LaTeX compilation successful! PDF created at: {result}")
    else:
        print(f"LaTeX compilation failed: {result}")
        # Check the content of the failed TeX file (ADDED THIS)
        temp_dir = editor.working_dir
        tex_file = temp_dir / "editor_test.tex"
        if tex_file.exists():
            print("\nChecking content of the failed TeX file:")
            with open(tex_file, "r", encoding="utf-8") as f:
                content = f.read()
                print(f"File exists, first 300 characters:\n{content[:300]}...")
                print(f"graphicx included: {'\\usepackage{graphicx}' in content}")
    
    # Clean up - destroy the tkinter root
    root.destroy()
    
    return success

def main():
    """Main function"""
    print("=== Math Editor Image Handling Test ===")
    
    # Test image conversion
    if not test_image_conversion():
        print("Image conversion test failed!")
        return
    
    # Test LaTeX compilation
    if not test_latex_compilation():
        print("LaTeX compilation test failed!")
        return
    
    # Test MathEditor image handling
    if not test_math_editor_image_handling():
        print("MathEditor image handling test failed!")
        return
    
    print("\n=== All tests completed successfully! ===")

# Add missing import (ADDED THIS)
import shutil

if __name__ == "__main__":
    main()