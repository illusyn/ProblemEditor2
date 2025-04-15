"""
Test script that matches the main application's workflow exactly
"""

from pathlib import Path
import tempfile
import os
import subprocess
import re
from PIL import Image, ImageDraw

# Create a copy of your main working directory structure
working_dir = Path(tempfile.gettempdir()) / "simplified_math_editor_test"
working_dir.mkdir(exist_ok=True)
print(f"Working directory: {working_dir}")

# Create images directory
images_dir = working_dir / "images"
images_dir.mkdir(exist_ok=True)
print(f"Images directory: {images_dir}")

# Create a simple test image
img = Image.new('RGB', (300, 200), color='white')
draw = ImageDraw.Draw(img)
draw.rectangle([(20, 20), (280, 180)], outline='black')
draw.text((100, 100), "Test Image", fill='black')

# Image filename formatted like your application
image_name = "image_test123.png"

# Save the image directly to BOTH directories
main_img_path = working_dir / image_name
img.save(main_img_path)
print(f"Saved image to main directory: {main_img_path}")

subdir_img_path = images_dir / image_name
img.save(subdir_img_path)
print(f"Saved image to images subdirectory: {subdir_img_path}")

# This is the template from math_editor.py load_template method
template = """\\documentclass{article}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{graphicx}

% Set up image path - adjust if needed
\\graphicspath{{./}{./images/}}

\\begin{document}

#CONTENT#

\\end{document}
"""

# Create the LaTeX figure content - EXACTLY like your editor output
figure_content = """
\\begin{figure}
\\centering
\\includegraphics{""" + image_name + """}
\\caption{Figure caption}
\\label{fig:test}
\\end{figure}
"""

# Replace #CONTENT# with the figure content
latex_document = template.replace("#CONTENT#", figure_content)

# Write the LaTeX document to the working directory
tex_path = working_dir / "app_exact_test.tex"
with open(tex_path, "w", encoding="utf-8") as f:
    f.write(latex_document)
print(f"Created LaTeX document at: {tex_path}")

# Print the exact document content for comparison
print("\nLaTeX Document Content:")
print("-----------------------")
print(latex_document)
print("-----------------------\n")

# Compile the LaTeX document using the demo script's approach
current_dir = os.getcwd()
print(f"Current directory before change: {current_dir}")

# Change to the working directory
os.chdir(working_dir)
print(f"Changed to working directory: {os.getcwd()}")

# Run pdflatex with verbose output
print("Running pdflatex command...")
result = subprocess.run(
    ["pdflatex", "-interaction=nonstopmode", "app_exact_test.tex"],
    capture_output=True,
    text=True
)

# Process the output for readability
print(f"pdflatex return code: {result.returncode}")
if result.returncode != 0:
    print("\nCompilation Error:")
    # Extract just the error message parts
    error_lines = []
    lines = result.stdout.split('\n')
    for i, line in enumerate(lines):
        if "! " in line:  # LaTeX error marker
            error_lines.append(line)
            # Add a few lines after the error for context
            for j in range(1, min(3, len(lines) - i)):
                if lines[i + j].strip():
                    error_lines.append(lines[i + j])
    
    if error_lines:
        print("\n".join(error_lines))
    else:
        print("No specific error found. Last 10 lines of output:")
        print("\n".join(lines[-10:]))

# Return to original directory
os.chdir(current_dir)
print(f"Changed back to original directory: {current_dir}")

# Check the result
pdf_path = working_dir / "app_exact_test.pdf"
if pdf_path.exists():
    print(f"Success! PDF created at: {pdf_path}")
else:
    print("Compilation failed! No PDF was created.")