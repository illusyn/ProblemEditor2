"""
Preview manager for the Simplified Math Editor (PyQt5).

This module handles converting markdown to LaTeX and displaying the preview.
"""

from markdown_parser import MarkdownParser
from preview.latex_compiler import LaTeXCompiler
import os
import uuid
import re
import shutil
from pathlib import Path

class PreviewManager:
    """Manages preview generation and display for the Simplified Math Editor"""
    
    def __init__(self, config_manager=None):
        """Initialize the preview manager"""
        self.parser = MarkdownParser(config_manager=config_manager)
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
        unique_id = str(uuid.uuid4())[:8]
        output_filename = f"preview_{unique_id}"
        try:
            # Parse markdown to LaTeX content only
            latex_content = self.parser.parse(markdown_text)
            # Assemble full LaTeX document using the parser's method
            full_latex = self.parser.create_latex_document(latex_content)
            # Compile LaTeX to PDF
            success, result = self.compiler.compile_latex(full_latex, output_filename)
            if success:
                if self.current_preview_file:
                    try:
                        os.remove(self.current_preview_file)
                    except:
                        pass
                self.current_preview_file = result
                return True, result
            else:
                return False, result
        except Exception as e:
            return False, str(e) 