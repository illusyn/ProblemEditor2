"""
Preview manager for the Simplified Math Editor (PyQt5).

This module handles converting markdown to LaTeX and displaying the preview.
"""

from markdown_parser import MarkdownParser
from preview.latex_compiler import LaTeXCompiler
import os
import uuid

class PreviewManager:
    """Manages preview generation and display for the Simplified Math Editor"""
    
    def __init__(self):
        """Initialize the preview manager"""
        self.parser = MarkdownParser()
        self.compiler = LaTeXCompiler()
        self.current_preview_file = None
    
    def update_preview(self, markdown_text):
        """
        Update the preview with new markdown content
        
        Args:
            markdown_text (str): Markdown content to preview
            
        Returns:
            tuple: (success, pdf_path or error_message)
        """
        # Generate a unique filename for this preview
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"preview_{unique_id}"
        
        # LaTeX template with Calibri font
        latex_template = r"""
\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\usepackage{booktabs}
\usepackage{enumitem}
\usepackage{fontspec}

% Set up Calibri font
\setmainfont{Calibri}[
    Path = C:/Windows/Fonts/,
    Extension = .ttf,
    UprightFont = Calibri,
    BoldFont = Calibrib,
    ItalicFont = Calibrii,
    BoldItalicFont = Calibriz
]

% Define custom commands
\newcommand{\mydefaultsize}{\normalsize}

\begin{document}

#CONTENT#

\end{document}
"""
        
        try:
            # Parse markdown to LaTeX
            latex_content = self.parser.parse(markdown_text)
            
            # Insert content into template
            full_latex = latex_template.replace("#CONTENT#", latex_content)
            
            # Compile LaTeX to PDF
            success, result = self.compiler.compile_latex(full_latex, output_filename)
            
            if success:
                # Clean up old preview files
                if self.current_preview_file:
                    try:
                        os.remove(self.current_preview_file)
                    except:
                        pass  # Ignore errors deleting old files
                
                # Update current preview file
                self.current_preview_file = result
                
                return True, result
            else:
                return False, result
                
        except Exception as e:
            return False, str(e) 