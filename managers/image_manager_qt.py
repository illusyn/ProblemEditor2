"""
Image management for the Simplified Math Editor (PyQt5 version).

This module provides functionality to handle images in the editor,
including clipboard operations, file operations, and image details dialogs.
"""

import os
from pathlib import Path
from PIL import Image
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QPushButton, QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QImage
from db.math_image_db import MathImageDB

class ImageDetailsDialog(QDialog):
    """Dialog for getting image details"""
    
    def __init__(self, parent=None, image_info=None):
        super().__init__(parent)
        self.image_info = image_info
        self.result = None
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI"""
        self.setWindowTitle("Image Details")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Image preview
        if self.image_info and 'preview' in self.image_info:
            preview_label = QLabel()
            preview_label.setPixmap(QPixmap.fromImage(self.image_info['preview']))
            preview_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(preview_label)
        
        # Caption
        caption_layout = QHBoxLayout()
        caption_label = QLabel("Caption:")
        self.caption_edit = QLineEdit()
        caption_layout.addWidget(caption_label)
        caption_layout.addWidget(self.caption_edit)
        layout.addLayout(caption_layout)
        
        # Label
        label_layout = QHBoxLayout()
        label_label = QLabel("Label:")
        self.label_edit = QLineEdit()
        self.label_edit.setText(f"fig:{Path(self.image_info['filename']).stem}")
        label_layout.addWidget(label_label)
        label_layout.addWidget(self.label_edit)
        layout.addLayout(label_layout)
        
        # Width
        width_layout = QHBoxLayout()
        width_label = QLabel("Width (0.1-1.0):")
        self.width_spin = QDoubleSpinBox()
        self.width_spin.setRange(0.1, 1.0)
        self.width_spin.setSingleStep(0.1)
        self.width_spin.setValue(0.8)
        width_layout.addWidget(width_label)
        width_layout.addWidget(self.width_spin)
        layout.addLayout(width_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("Cancel")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
    
    def get_result(self):
        """Get the dialog result"""
        if self.result() == QDialog.Accepted:
            return {
                "caption": self.caption_edit.text(),
                "label": self.label_edit.text(),
                "width": self.width_spin.value(),
                "filename": self.image_info["filename"]
            }
        return None

class ImageManagerQt:
    """Manages image operations for the Simplified Math Editor (PyQt5 version)"""
    
    def __init__(self, app):
        """
        Initialize the image manager
        
        Args:
            app: Reference to the MainWindow instance
        """
        self.app = app
        self.image_db = MathImageDB()
    
    def paste_image(self):
        """
        Paste image from clipboard as LaTeX figure
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if currently using a font that requires XeLaTeX
            current_font = self.app.config_manager.get_value("preview", "font_family", "Computer Modern")
            uses_xelatex = current_font in ["Calibri", "Cambria Math"]
            
            # If using a font that requires XeLaTeX, temporarily switch to Computer Modern
            if uses_xelatex:
                original_font = current_font
                self.app.config_manager.set_value("preview", "font_family", "Computer Modern")
                needs_restore = True
            else:
                needs_restore = False
            
            # Try to get image from clipboard
            success, clipboard_image = self.app.image_converter.get_image_from_clipboard()
            
            if not success:
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                    
                QMessageBox.information(self.app, "No Image", 
                    "No image found in clipboard.\n\n"
                    "Note: The application can only access images that are\n"
                    "copied as images, not as files or other formats.")
                return False
            
            # Process the image
            success, result = self.app.image_converter.process_image(clipboard_image)
            
            if not success:
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                    
                QMessageBox.critical(self.app, "Image Processing Error", result)
                return False
            
            # Get image details
            image_info = self.get_image_details(result)
            if not image_info:
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                return False
            
            # Create LaTeX figure code
            latex_figure = self.app.image_converter.create_latex_figure(
                image_path=image_info["filename"],
                caption=image_info["caption"],
                label=image_info["label"],
                width=image_info["width"]
            )
            
            # Insert at cursor position
            self.app.editor.insert_text(latex_figure)
            
            # Update preview
            self.app.update_preview()
            
            # Restore original font if needed
            if needs_restore:
                self.app.config_manager.set_value("preview", "font_family", original_font)
                self.app.update_preview()
                
            return True
                
        except Exception as e:
            if 'needs_restore' in locals() and needs_restore and 'original_font' in locals():
                self.app.config_manager.set_value("preview", "font_family", original_font)
                
            QMessageBox.critical(self.app, "Image Error", str(e))
            return False
    
    def insert_image_from_file(self):
        """
        Insert an image from a file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if currently using a font that requires XeLaTeX
            current_font = self.app.config_manager.get_value("preview", "font_family", "Computer Modern")
            uses_xelatex = current_font in ["Calibri", "Cambria Math"]
            
            if uses_xelatex:
                original_font = current_font
                self.app.config_manager.set_value("preview", "font_family", "Computer Modern")
                needs_restore = True
            else:
                needs_restore = False
            
            # Ask for image file
            file_path, _ = QFileDialog.getOpenFileName(
                self.app,
                "Select Image",
                "",
                "Image files (*.png *.jpg *.jpeg *.gif *.bmp);;All files (*.*)"
            )
            
            if not file_path:
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                return False
            
            # Process the image
            success, result = self.app.image_converter.process_image(file_path)
            
            if not success:
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                    
                QMessageBox.critical(self.app, "Image Processing Error", result)
                return False
            
            # Get image details
            image_info = self.get_image_details(result)
            if not image_info:
                if needs_restore:
                    self.app.config_manager.set_value("preview", "font_family", original_font)
                return False
            
            # Create LaTeX figure code
            latex_figure = self.app.image_converter.create_latex_figure(
                image_path=image_info["filename"],
                caption=image_info["caption"],
                label=image_info["label"],
                width=image_info["width"]
            )
            
            # Insert at cursor position
            self.app.editor.insert_text(latex_figure)
            
            # Update preview
            self.app.update_preview()
            
            # Restore original font if needed
            if needs_restore:
                self.app.config_manager.set_value("preview", "font_family", original_font)
                self.app.update_preview()
                
            return True
                
        except Exception as e:
            if 'needs_restore' in locals() and needs_restore and 'original_font' in locals():
                self.app.config_manager.set_value("preview", "font_family", original_font)
                
            QMessageBox.critical(self.app, "Image Error", str(e))
            return False
    
    def get_image_details(self, image_info):
        """
        Show dialog to get image details
        
        Args:
            image_info (dict): Dictionary with image information
            
        Returns:
            dict or None: Dictionary with image details or None if cancelled
        """
        # Create preview image for dialog
        if 'path' in image_info:
            img = Image.open(image_info['path'])
            img.thumbnail((300, 300))  # Resize for preview
            qimg = QImage(img.tobytes(), img.width, img.height, img.width * 3, QImage.Format_RGB888)
            image_info['preview'] = qimg
        
        # Show dialog
        dialog = ImageDetailsDialog(self.app, image_info)
        if dialog.exec_() == QDialog.Accepted:
            return dialog.get_result()
        return None 