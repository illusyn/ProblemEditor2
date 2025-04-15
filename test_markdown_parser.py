"""
Test script for the markdown parser and image inclusion in the Simplified Math Editor.

This script tests:
1. Basic markdown parsing
2. Image inclusion in LaTeX
3. Mathematical expressions

Usage:
- Run this script with Python: python test_markdown_parser.py
- It will generate a test file and try to compile it
"""

import os
import sys
from pathlib import Path
import subprocess
import tempfile
from PIL import Image, ImageDraw

# Import your markdown parser - assumes it's in the same directory
try:
    from markdown_parser import MarkdownParser
except ImportError:
    print("ERROR: Could not import MarkdownParser. Make sure markdown_parser.py is in the same directory.")
    sys.exit(1)

def create_test_image():
    """Create a simple test image for the LaTeX document"""
    # Create a test directory
    test_dir = Path("./test_markdown")
    test_dir.mkdir(exist_ok=True)
    
    # Create a simple test image
    img = Image.new('RGB', (300, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([(20, 20), (280, 180)], outline='black')
    draw.text((100, 100), "Test Image", fill='black')
    
    # Save the image
    img_path = test_dir / "test_image.png"
    img.save(img_path)
    print(f"Created test image at: {img_path}")
    
    return img_path, test_dir

def create_test_markdown():
    """Create a test markdown document with various elements"""
    markdown = """#problem Test Problem with Image and Equations

This is a test problem that includes an image and some equations.

#question What is the value of x in the equation below?

#eq 2x + 3 = 7

For reference, here is another equation:

\\[
    \\frac{x^2-4}{3x+6}
\\]

And here is an image:

\\begin{figure}[htbp]
    \\centering
    \\includegraphics{test_image.png}
    \\caption{Test Image}
    \\label{fig:test}
\\end{figure}

#solution

To solve the equation $2x + 3 = 7$, we subtract 3 from both sides:

#eq
2x = 4

Then divide both sides by 2:

#eq
x = 2

Therefore, the answer is $x = 2$.
"""
    return markdown

def test_markdown_parser():
    """Test the markdown parser with image inclusion"""
    # Create a test image
    img_path, test_dir = create_test_image()
    
    # Create the test markdown
    markdown = create_test_markdown()
    
    # Initialize the markdown parser
    parser = MarkdownParser()
    
    # Parse the markdown to LaTeX
    latex = parser.parse(markdown)
    
    # Write the LaTeX to a file
    tex_path = test_dir / "test_markdown.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex)
    print(f"Created LaTeX document at: {tex_path}")
    
    # Compile the LaTeX document
    current_dir = os.getcwd()
    os.chdir(test_dir)
    
    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "test_markdown.tex"],
        capture_output=True,
        text=True
    )
    
    os.chdir(current_dir)
    
    # Check the result
    pdf_path = test_dir / "test_markdown.pdf"
    if pdf_path.exists():
        print(f"Success! PDF created at: {pdf_path}")
        return True
    else:
        print("Compilation failed!")
        print("Error output:")
        print(result.stdout)
        return False

if __name__ == "__main__":
    print("Testing markdown parser with image inclusion...")
    success = test_markdown_parser()
    if success:
        print("All tests passed!")
    else:
        print("Test failed.")