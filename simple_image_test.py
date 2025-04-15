"""
Simplified test of LaTeX image handling with the graphicx package.
This script tests ONLY image inclusion in LaTeX, isolating the issue.
"""

import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw

def create_test_directory():
    """Create a test directory"""
    test_dir = Path("./simple_image_test")
    test_dir.mkdir(exist_ok=True)
    # Print absolute path for debugging
    print(f"Test directory absolute path: {test_dir.absolute()}")
    return test_dir

def create_test_image(path):
    """Create a simple test image"""
    img = Image.new('RGB', (300, 200), color='white')
    draw = ImageDraw.Draw(img)
    draw.rectangle([(20, 20), (280, 180)], outline='black')
    draw.text((100, 100), "Test Image", fill='black')
    img.save(path)
    print(f"Created test image at: {path}")
    return img

def create_latex_document():
    """Create a LaTeX document with image inclusion"""
    # This is the simplest possible document with graphicx package
    return r"""
\documentclass{article}
\usepackage{graphicx}

\begin{document}

\section{Simple Image Test}

Testing image inclusion with the graphicx package.

\begin{figure}[htbp]
    \centering
    \includegraphics{test_image.png}
    \caption{Test Image}
    \label{fig:test}
\end{figure}

\end{document}
"""

def compile_latex(tex_file):
    """Compile a LaTeX file to PDF"""
    # Get the directory and filename
    tex_dir = os.path.dirname(tex_file)
    tex_filename = os.path.basename(tex_file)
    
    # Remember current directory
    current_dir = os.getcwd()
    
    try:
        # Change to the directory with the tex file
        print(f"Changing to directory: {tex_dir}")
        os.chdir(tex_dir)
        
        # List files in directory before compilation
        print("Files in directory before compilation:")
        for file in os.listdir("."):
            print(f"  {file}")
        
        # Run pdflatex
        print(f"Running: pdflatex -interaction=nonstopmode {tex_filename}")
        result = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", tex_filename],
            capture_output=True,
            text=True
        )
        
        # Print output for debugging
        print(f"Return code: {result.returncode}")
        if result.returncode != 0:
            print("Error output:")
            print(result.stdout[:500])  # Show first 500 chars of output
            print("...")
        else:
            print("Compilation succeeded with no errors")
        
        # List files in directory after compilation
        print("Files in directory after compilation:")
        for file in os.listdir("."):
            print(f"  {file}")
        
        # Check for PDF
        pdf_filename = tex_filename.replace(".tex", ".pdf")
        if os.path.exists(pdf_filename):
            print(f"Success! PDF found at: {pdf_filename}")
            # Get absolute path
            pdf_absolute = os.path.abspath(pdf_filename)
            print(f"Absolute path: {pdf_absolute}")
            return True
        else:
            print(f"PDF not found: {pdf_filename}")
            return False
            
    finally:
        # Always return to original directory
        os.chdir(current_dir)

def main():
    """Main function"""
    print("=== Simple Image LaTeX Test ===")
    
    # Create test directory
    test_dir = create_test_directory()
    
    # Create test image
    img_path = test_dir / "test_image.png"
    create_test_image(img_path)
    
    # Create LaTeX document
    latex_content = create_latex_document()
    
    # Write LaTeX document to file
    tex_path = test_dir / "simple_test.tex"
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)
    print(f"Created LaTeX document at: {tex_path}")
    
    # Compile LaTeX document
    success = compile_latex(str(tex_path))
    
    if success:
        print("\nTest completed successfully!")
    else:
        print("\nTest failed.")

if __name__ == "__main__":
    main()