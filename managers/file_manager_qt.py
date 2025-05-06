"""
File management for the Simplified Math Editor.

This module provides functionality to load, save, and export files
within the application using PyQt5 dialogs.
"""

import os
import platform
import subprocess
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog, QMessageBox
from PyQt5.QtCore import QObject


class FileManager(QObject):
    """Manages file operations for the Simplified Math Editor"""
    
    def __init__(self, app):
        """
        Initialize the file manager
        
        Args:
            app: Reference to the MathEditor instance
        """
        super().__init__()
        self.app = app
        self.current_file = None
    
    def new_file(self):
        """Create a new file"""
        if self.check_save_changes():
            self.app.editor.set_content("")
            self.current_file = None
            self.app.setWindowTitle("Simplified Math Editor - Untitled")
            self.app.status_bar.showMessage("New file created")
            return True
        return False
    
    def open_file(self):
        """Open a file"""
        if self.check_save_changes():
            filepath, _ = QFileDialog.getOpenFileName(
                self.app,
                "Open File",
                "",
                "Text files (*.txt);;TeX files (*.tex);;Markdown files (*.md);;All files (*.*)"
            )
            if filepath:
                try:
                    with open(filepath, "r", encoding="utf-8") as file:
                        content = file.read()
                        self.app.editor.set_content(content)
                        self.current_file = filepath
                        self.app.setWindowTitle(f"Simplified Math Editor - {os.path.basename(filepath)}")
                        self.app.status_bar.showMessage(f"Opened {filepath}")
                        
                        # Update preview
                        self.app.update_preview()
                        return True
                except Exception as e:
                    QMessageBox.critical(self.app, "Error", f"Could not open file: {str(e)}")
            return False
        return False
    
    def save_file(self):
        """Save the current file"""
        if self.current_file:
            return self._save_to_file(self.current_file)
        else:
            return self.save_as()
    
    def save_as(self):
        """Save the file with a new name"""
        filepath, _ = QFileDialog.getSaveFileName(
            self.app,
            "Save As",
            "",
            "Markdown files (*.md);;TeX files (*.tex);;Text files (*.txt);;All files (*.*)"
        )
        if filepath:
            return self._save_to_file(filepath)
        return False
    
    def _save_to_file(self, filepath):
        """
        Save content to the specified file
        
        Args:
            filepath (str): Path to the file to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            content = self.app.editor.get_content()
            with open(filepath, "w", encoding="utf-8") as file:
                file.write(content)
            self.current_file = filepath
            self.app.setWindowTitle(f"Simplified Math Editor - {os.path.basename(filepath)}")
            self.app.status_bar.showMessage(f"Saved to {filepath}")
            return True
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Could not save file: {str(e)}")
            return False
    
    def export_to_pdf(self):
        """Export the current document to PDF"""
        filepath, _ = QFileDialog.getSaveFileName(
            self.app,
            "Export to PDF",
            "",
            "PDF files (*.pdf);;All files (*.*)"
        )
        if not filepath:
            return False
        
        try:
            # Get the editor content
            content = self.app.editor.get_content()
            
            # Parse the markdown to LaTeX
            latex_document = self.app.markdown_parser.parse(content)
            
            # Ensure graphicx package is included
            if "\\usepackage{graphicx}" not in latex_document:
                # Add it immediately before \begin{document}
                latex_document = latex_document.replace("\\begin{document}", 
                    "\\usepackage{graphicx}\n\\graphicspath{{./}{./images/}}\n\n\\begin{document}")
            
            # Update status
            self.app.status_bar.showMessage("Extracting images for LaTeX compilation...")
            self.app.processEvents()  # Force UI update
            
            # Extract images from the database for compilation
            if not self.app.extract_images_for_compilation():
                self.app.status_bar.showMessage("Failed to extract images from database")
                QMessageBox.critical(self.app, "Image Error", 
                    "Failed to extract one or more images from the database for PDF export.")
                return False
            
            # Update status for compilation
            self.app.status_bar.showMessage("Compiling LaTeX for PDF export...")
            self.app.processEvents()  # Force UI update
            
            # Compile the LaTeX document
            success, result = self.app.latex_compiler.compile_latex(latex_document, "export")
            
            if success:
                # Copy the PDF to the target location
                import shutil
                shutil.copy2(result, filepath)
                self.app.status_bar.showMessage(f"Exported to {filepath}")
                
                # Ask if the user wants to open the PDF
                response = QMessageBox.question(
                    self.app,
                    "Export Complete",
                    "PDF exported successfully. Open the PDF?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if response == QMessageBox.Yes:
                    self.open_file_with_default_app(filepath)
                return True
            else:
                # Show compilation error
                self.app.status_bar.showMessage("PDF export failed")
                QMessageBox.critical(self.app, "Export Error", result)
                return False
        
        except Exception as e:
            self.app.status_bar.showMessage("Export error")
            QMessageBox.critical(self.app, "Export Error", str(e))
            return False
    
    def check_save_changes(self):
        """
        Check if there are unsaved changes and prompt user to save
        
        Returns:
            bool: True if operation should continue, False if cancelled
        """
        if self.current_file:
            try:
                with open(self.current_file, "r", encoding="utf-8") as file:
                    original_content = file.read()
                current_content = self.app.editor.get_content()
                
                if original_content != current_content:
                    response = QMessageBox.question(
                        self.app,
                        "Unsaved Changes",
                        "Do you want to save changes to the current file?",
                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
                    )
                    if response == QMessageBox.Cancel:
                        return False
                    elif response == QMessageBox.Yes:
                        return self.save_file()
            except:
                pass  # Ignore errors reading file
        return True
    
    def open_file_with_default_app(self, filepath):
        """
        Open a file with the default application
        
        Args:
            filepath (str): Path to the file to open
        """
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath], check=True)
            else:  # Linux
                subprocess.run(['xdg-open', filepath], check=True)
        except Exception as e:
            QMessageBox.critical(self.app, "Error", f"Failed to open the file: {str(e)}")
    
    def get_current_file(self):
        """
        Get the path of the currently open file
        
        Returns:
            str or None: Path to the current file or None if no file is open
        """
        return self.current_file 