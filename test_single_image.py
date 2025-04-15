from pathlib import Path
import tempfile
import os
import subprocess
from PIL import Image, ImageDraw

# Create a test directory
test_dir = Path("./test_single_image")
test_dir.mkdir(exist_ok=True)

# Create a simple test image
img = Image.new('RGB', (300, 200), color='white')
draw = ImageDraw.Draw(img)
draw.rectangle([(20, 20), (280, 180)], outline='black')
draw.text((100, 100), "Test Image", fill='black')

# Save the image directly to the test directory
img_path = test_dir / "simple_test.png"
img.save(img_path)
print(f"Created test image at: {img_path}")

# Create a basic LaTeX document
latex = r"""
\documentclass{article}
\usepackage{graphicx}

\begin{document}

\section{Simple Test}

\begin{figure}
\centering
\includegraphics{simple_test.png}
\caption{Simple Test Image}
\label{fig:simple}
\end{figure}

\end{document}
"""

# Write the LaTeX document to the test directory
tex_path = test_dir / "simple_test.tex"
with open(tex_path, "w", encoding="utf-8") as f:
    f.write(latex)
print(f"Created LaTeX document at: {tex_path}")

# Compile the LaTeX document
current_dir = os.getcwd()
os.chdir(test_dir)

result = subprocess.run(
    ["pdflatex", "-interaction=nonstopmode", "simple_test.tex"],
    capture_output=True,
    text=True
)

os.chdir(current_dir)

# Check the result
pdf_path = test_dir / "simple_test.pdf"
if pdf_path.exists():
    print(f"Success! PDF created at: {pdf_path}")
else:
    print("Compilation failed!")
    print("Error output:")
    print(result.stdout)