"""
LaTeX compilation utilities for the Simplified Math Editor.

This module provides functionality to compile LaTeX documents into PDF
and handle compilation errors.
"""

import os
import subprocess
import tempfile
from pathlib import Path

def clean_pasted_text(text):
    """Clean text pasted from various sources"""
    if not text:
        return text
    # Replace Windows line endings
    text = text.replace('\r\n', '\n')
    # Replace other line endings
    text = text.replace('\r', '\n')
    return text

class LaTeXCompiler:
    """Handles compiling LaTeX documents to PDF"""
    
    def __init__(self, working_dir=None):
        """
        Initialize the LaTeX compiler
        
        Args:
            working_dir (str, optional): Working directory for compilation.
                                        If None, './temp' will be used.
        """
        if working_dir:
            self.working_dir = Path(working_dir)
        else:
            self.working_dir = Path("temp")
        self.working_dir.mkdir(parents=True, exist_ok=True)
    
    def compile_latex(self, latex_content, output_filename="preview"):
        """
        Compile LaTeX content to PDF
        
        Args:
            latex_content (str): LaTeX document content
            output_filename (str): Base name for output files (without extension)
            
        Returns:
            tuple: (success, pdf_path or error_message)
        """
        # Create a temporary file for the LaTeX content
        tex_file = self.working_dir / f"{output_filename}.tex"
        pdf_file = self.working_dir / f"{output_filename}.pdf"
        
        try:
            # Clean LaTeX content for Unicode before writing
            latex_content = clean_pasted_text(latex_content)
            # Write the LaTeX content to the file
            with open(tex_file, "w", encoding="utf-8") as f:
                f.write(latex_content)
            
            print(f"LaTeX file created at: {tex_file}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Changing to working directory: {self.working_dir}")
            
            # Save the current directory
            current_dir = os.getcwd()
            
            # Change to the working directory
            os.chdir(self.working_dir)
            
            # Check if we need to use XeLaTeX (based on fontspec being in the document)
            lower_content = latex_content.lower()
            use_xelatex = ("\\usepackage{fontspec}" in lower_content) or ("\\setmainfont" in latex_content)
            
            # Determine which LaTeX engine to use
            latex_engine = "xelatex" if use_xelatex else "pdflatex"
            
            # Print debugging information
            print(f"Using {latex_engine} for compilation")
            print(f"Running command: {latex_engine} -interaction=nonstopmode {tex_file.name}")
            
            # Run with nonstopmode to prevent interactive prompts
            result = subprocess.run(
                [latex_engine, "-interaction=nonstopmode", tex_file.name],
                capture_output=True,
                text=True
            )
            
            # Print more debugging information
            print(f"Return code: {result.returncode}")
            if result.returncode != 0:
                print(f"Error output: {result.stderr}")
                print(f"Standard output excerpt: {result.stdout[:500]}...")
            
            # Restore the original directory
            print(f"Changing back to original directory: {current_dir}")
            os.chdir(current_dir)
            
            # Check if the compilation was successful
            if result.returncode != 0:
                # Compilation failed, return the error message
                error_msg = self.parse_error(result.stdout + "\n" + result.stderr)
                return (False, error_msg)
            
            # Check if the PDF file was created
            if not pdf_file.exists():
                return (False, "PDF file was not created. Check LaTeX installation.")
            
            print(f"PDF file created successfully at: {pdf_file}")
            
            # Return the path to the PDF file
            return (True, str(pdf_file))
            
        except Exception as e:
            # Make sure we restore the original directory
            try:
                os.chdir(current_dir)
            except:
                pass
            
            return (False, str(e))
    
    def parse_error(self, error_output):
        """
        Parse LaTeX compilation error output to extract relevant error messages
        
        Args:
            error_output (str): Raw output from pdflatex
            
        Returns:
            str: Formatted error message
        """
        # Extract just the relevant part of the error message
        error_lines = []
        
        # Look for common error patterns in LaTeX output
        lines = error_output.split('\n')
        for i, line in enumerate(lines):
            if "! " in line:  # LaTeX error marker
                error_lines.append(line)
                
                # Add a few lines after the error for context
                for j in range(1, min(3, len(lines) - i)):
                    if lines[i + j].strip():
                        error_lines.append(lines[i + j])
        
        if not error_lines:
            # If no specific error was identified, return a generic message
            # with the last few lines of output
            error_lines = ["LaTeX compilation failed with no specific error message."]
            if len(lines) > 5:
                error_lines.append("Last output lines:")
                error_lines.extend(lines[-5:])
        
        return "\n".join(error_lines)
    
    def cleanup(self, base_filename="preview", keep_pdf=True):
        """
        Clean up temporary files created during compilation
        
        Args:
            base_filename (str): Base name of files to clean up
            keep_pdf (bool): Whether to keep the PDF file
        """
        extensions = [".aux", ".log", ".out"]
        if not keep_pdf:
            extensions.append(".pdf")
        
        # Add .tex if it's not the output we want to keep
        if base_filename != "preview":
            extensions.append(".tex")
        
        for ext in extensions:
            file_path = self.working_dir / f"{base_filename}{ext}"
            if file_path.exists():
                try:
                    file_path.unlink()
                except:
                    pass  # Ignore errors deleting temporary files