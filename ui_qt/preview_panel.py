"""
Preview panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from managers.preview_manager_qt import PreviewManager
import fitz  # PyMuPDF
import os
from ui_qt.style_config import PREVIEW_LABEL_MIN_WIDTH, PREVIEW_LABEL_MIN_HEIGHT

class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # Create scroll area for preview
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create preview label
        self.preview_label = QLabel("[Preview output will appear here]")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(PREVIEW_LABEL_MIN_WIDTH, PREVIEW_LABEL_MIN_HEIGHT)
        self.preview_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.preview_label.customContextMenuRequested.connect(self.show_context_menu)
        
        # Add preview label to scroll area
        scroll_area.setWidget(self.preview_label)
        
        # Add scroll area to layout
        layout.addWidget(scroll_area)
        
        # Initialize preview manager
        self.preview_manager = PreviewManager()
        
        # Store current preview path
        self.current_preview = None
        
        # Store reference to main window for image adjustment
        self.main_window = None
    
    def set_main_window(self, main_window):
        """Set reference to main window for image adjustment"""
        self.main_window = main_window
    
    def show_context_menu(self, pos):
        """Show context menu for image adjustment"""
        if not self.main_window:
            return
            
        menu = QMenu(self)
        adjust_action = menu.addAction("Adjust Image")
        action = menu.exec_(self.preview_label.mapToGlobal(pos))
        
        if action == adjust_action:
            self.main_window.adjust_image_size()
    
    def update_preview(self, markdown_text):
        """
        Update the preview with new markdown content
        
        Args:
            markdown_text (str): Markdown content to preview
        """
        # Generate PDF preview
        success, result = self.preview_manager.update_preview(markdown_text)
        
        if success:
            try:
                # Open PDF with PyMuPDF
                doc = fitz.open(result)
                
                # Get first page
                page = doc[0]
                
                # Convert to image
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                
                # Convert to QPixmap
                img_path = result.replace(".pdf", ".png")
                pix.save(img_path)
                pixmap = QPixmap(img_path)
                
                # Scale pixmap to fit preview label while maintaining aspect ratio
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                
                # Update preview label
                self.preview_label.setPixmap(scaled_pixmap)
                
                # Clean up
                doc.close()
                try:
                    os.remove(img_path)
                except:
                    pass
                
                # Store current preview path
                self.current_preview = result
                
            except Exception as e:
                self.preview_label.setText(f"Error displaying preview: {str(e)}")
        else:
            self.preview_label.setText(f"Error generating preview: {result}")
    
    def resizeEvent(self, event):
        """Handle resize events to scale the preview image"""
        super().resizeEvent(event)
        if self.current_preview and os.path.exists(self.current_preview):
            try:
                # Re-render the current preview at the new size
                doc = fitz.open(self.current_preview)
                page = doc[0]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
                img_path = self.current_preview.replace(".pdf", ".png")
                pix.save(img_path)
                pixmap = QPixmap(img_path)
                scaled_pixmap = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled_pixmap)
                doc.close()
                try:
                    os.remove(img_path)
                except:
                    pass
            except:
                pass  # Ignore errors during resize 

    def clear(self):
        # Clear the preview display (e.g., set to blank or default message)
        self.preview_label.setText("")
        self.preview_label.clear() 