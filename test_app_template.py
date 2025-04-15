"""
Test script that uses the main application's LaTeX template with the demo script's approach
"""

from pathlib import Path
import tempfile
import os
import subprocess
from PIL import Image, ImageDraw

# Create a test directory
test_dir = Path("./test_app_template")
test_dir.mkdir(exist_ok=True)

# Create a simple test image
img = Image.new('RGB', (300, 200), color='white')
draw = ImageDraw.Draw(img)
draw.rectangle([(20, 20), (280, 180)], outline='black')
draw.text((100, 100), "Test Image", fill='black')

# Save the image directly to the test directory
img_path = test_dir / "app_test.png"
img.save(img_path)
print(f"Created test image at: {img_path}")

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

# Create the LaTeX figure content
figure_content = """
\\begin{figure}
\\centering
\\includegraphics{app_test.png}
\\caption{App Template Test Image}
\\label{fig:app_test}
\\end{figure}
"""

# Create the complete LaTeX document using the application's template
latex_document = template.replace("#CONTENT#", figure_content)

# Write the LaTeX document to the test directory
tex_path = test_dir / "app_test.tex"
with open(tex_path, "w", encoding="utf-8") as f:
    f.write(latex_document)
print(f"Created LaTeX document at: {tex_path}")

# Compile the LaTeX document using the demo script's approach
current_dir = os.getcwd()
os.chdir(test_dir)

result = subprocess.run(
    ["pdflatex", "-interaction=nonstopmode", "app_test.tex"],
    capture_output=True,
    text=True
)

os.chdir(current_dir)

# Check the result
pdf_path = test_dir / "app_test.pdf"
if pdf_path.exists():
    print(f"Success! PDF created at: {pdf_path}")
else:
    print("Compilation failed!")
    print("Error output:")
    print(result.stdout)