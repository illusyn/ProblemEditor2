"""
Preview panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QMenu, QSpinBox, QPushButton, QShortcut
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QFont, QKeySequence
from managers.preview_manager_qt import PreviewManager
import fitz  # PyMuPDF
import os
from ui_qt.style_config import PREVIEW_LABEL_MIN_WIDTH, PREVIEW_LABEL_MIN_HEIGHT, FONT_FAMILY, LABEL_FONT_SIZE
from ui_qt.neumorphic_components import NeumorphicButton

class PreviewPanel(QWidget):
    def __init__(self, parent=None, config_manager=None):
        super().__init__(parent)
        self.config_manager = config_manager
        layout = QVBoxLayout(self)
        
        # Create zoom control panel
        zoom_control_panel = QWidget()
        zoom_control_layout = QHBoxLayout(zoom_control_panel)
        zoom_control_layout.setContentsMargins(5, 5, 5, 5)
        
        # Zoom label
        zoom_label = QLabel("Zoom:")
        zoom_font = QFont(FONT_FAMILY)
        zoom_font.setPointSizeF(LABEL_FONT_SIZE)
        zoom_label.setFont(zoom_font)
        zoom_control_layout.addWidget(zoom_label)
        
        # Zoom out button
        self.zoom_out_button = NeumorphicButton("-", font_size=LABEL_FONT_SIZE)
        self.zoom_out_button.setFixedWidth(40)
        self.zoom_out_button.clicked.connect(self.zoom_out)
        zoom_control_layout.addWidget(self.zoom_out_button)
        
        # Zoom percentage label
        self.zoom_label = QLabel("100%")
        zoom_font2 = QFont(FONT_FAMILY)
        zoom_font2.setPointSizeF(LABEL_FONT_SIZE)
        self.zoom_label.setFont(zoom_font2)
        self.zoom_label.setMinimumWidth(60)
        self.zoom_label.setAlignment(Qt.AlignCenter)
        zoom_control_layout.addWidget(self.zoom_label)
        
        # Zoom in button
        self.zoom_in_button = NeumorphicButton("+", font_size=LABEL_FONT_SIZE)
        self.zoom_in_button.setFixedWidth(40)
        self.zoom_in_button.clicked.connect(self.zoom_in)
        zoom_control_layout.addWidget(self.zoom_in_button)
        
        # Reset zoom button
        self.reset_zoom_button = NeumorphicButton("Reset", font_size=LABEL_FONT_SIZE)
        self.reset_zoom_button.setFixedWidth(80)
        self.reset_zoom_button.clicked.connect(self.reset_zoom)
        zoom_control_layout.addWidget(self.reset_zoom_button)
        
        # Add some spacing
        zoom_control_layout.addStretch()
        
        # Save as default button
        self.save_default_button = NeumorphicButton("Save as Default", font_size=LABEL_FONT_SIZE)
        self.save_default_button.setFixedWidth(150)
        self.save_default_button.clicked.connect(self.save_zoom_as_default)
        zoom_control_layout.addWidget(self.save_default_button)
        
        # Add zoom control panel to layout
        layout.addWidget(zoom_control_panel)
        
        # Create scroll area for preview
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(False)  # Changed to False so label can be larger than viewport
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create preview label
        self.preview_label = QLabel("[Preview output will appear here]")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumSize(PREVIEW_LABEL_MIN_WIDTH, PREVIEW_LABEL_MIN_HEIGHT)
        self.preview_label.setContextMenuPolicy(Qt.CustomContextMenu)
        self.preview_label.customContextMenuRequested.connect(self.show_context_menu)
        
        # Add preview label to scroll area
        self.scroll_area.setWidget(self.preview_label)
        
        # Add scroll area to layout
        layout.addWidget(self.scroll_area)
        
        # Initialize preview manager
        self.preview_manager = PreviewManager(config_manager=config_manager)
        
        # Store current preview path
        self.current_preview = None
        
        # Store reference to main window for image adjustment
        self.main_window = None
        
        # Initialize zoom level (default 100%)
        self.zoom_level = 100
        # Load saved zoom level from config
        if config_manager:
            self.zoom_level = config_manager.get_value("preview", "zoom_level", 100)
        self.update_zoom_label()
        
        # Track if settings have been modified
        self.settings_modified = False
        
        # Add keyboard shortcuts for zoom
        zoom_in_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        zoom_in_shortcut.activated.connect(self.zoom_in)
        
        zoom_in_shortcut2 = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in_shortcut2.activated.connect(self.zoom_in)
        
        zoom_out_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out_shortcut.activated.connect(self.zoom_out)
        
        reset_zoom_shortcut = QShortcut(QKeySequence("Ctrl+0"), self)
        reset_zoom_shortcut.activated.connect(self.reset_zoom)
    
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
                
                # Convert to image with zoom applied
                zoom_factor = self.zoom_level / 100.0 * 2  # Base 2x for quality, multiplied by zoom
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))
                
                # Convert to QPixmap
                img_path = result.replace(".pdf", ".png")
                pix.save(img_path)
                pixmap = QPixmap(img_path)
                
                # Update the label size and pixmap
                self.preview_label.setPixmap(pixmap)
                self.preview_label.resize(pixmap.size())
                
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
                zoom_factor = self.zoom_level / 100.0 * 2
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))
                img_path = self.current_preview.replace(".pdf", ".png")
                pix.save(img_path)
                pixmap = QPixmap(img_path)
                # Update the label size and pixmap
                self.preview_label.setPixmap(pixmap)
                self.preview_label.resize(pixmap.size())
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
    
    def zoom_in(self):
        """Increase zoom level"""
        if self.zoom_level < 300:  # Max 300%
            self.zoom_level += 10  # Changed from 25 to 10
            self.update_zoom_display()
            self.refresh_preview()
            self.settings_modified = True
            self.update_save_button_state()
    
    def zoom_out(self):
        """Decrease zoom level"""
        if self.zoom_level > 50:  # Min 50%
            self.zoom_level -= 10  # Changed from 25 to 10
            self.update_zoom_display()
            self.refresh_preview()
            self.settings_modified = True
            self.update_save_button_state()
    
    def reset_zoom(self):
        """Reset zoom to 100%"""
        self.zoom_level = 100
        self.update_zoom_display()
        self.refresh_preview()
        self.settings_modified = True
        self.update_save_button_state()
    
    def update_zoom_label(self):
        """Update the zoom percentage label"""
        self.zoom_label.setText(f"{self.zoom_level}%")
    
    def update_zoom_display(self):
        """Update zoom label and button states"""
        self.update_zoom_label()
        # Disable buttons at limits
        self.zoom_out_button.setEnabled(self.zoom_level > 50)
        self.zoom_in_button.setEnabled(self.zoom_level < 300)
    
    def refresh_preview(self):
        """Refresh the preview with current zoom level"""
        if self.current_preview and os.path.exists(self.current_preview):
            try:
                # Re-render with new zoom
                doc = fitz.open(self.current_preview)
                page = doc[0]
                zoom_factor = self.zoom_level / 100.0 * 2
                pix = page.get_pixmap(matrix=fitz.Matrix(zoom_factor, zoom_factor))
                img_path = self.current_preview.replace(".pdf", ".png")
                pix.save(img_path)
                pixmap = QPixmap(img_path)
                
                # Update the label size and pixmap
                self.preview_label.setPixmap(pixmap)
                self.preview_label.resize(pixmap.size())
                
                # Always scroll to top after zoom to keep top of document visible
                from PyQt5.QtCore import QTimer
                def scroll_to_top():
                    self.scroll_area.verticalScrollBar().setValue(0)
                    # Also reset horizontal scroll to left
                    self.scroll_area.horizontalScrollBar().setValue(0)
                
                # Use a timer to scroll after Qt has updated the scroll bars
                QTimer.singleShot(10, scroll_to_top)
                
                doc.close()
                try:
                    os.remove(img_path)
                except:
                    pass
            except Exception as e:
                print(f"Error refreshing preview: {e}")
    
    def update_save_button_state(self):
        """Update the save button to indicate if there are unsaved changes"""
        if self.settings_modified:
            self.save_default_button.setText("Save as Default*")
        else:
            self.save_default_button.setText("Save as Default")
    
    def save_zoom_as_default(self):
        """Save current zoom level as default"""
        if self.config_manager:
            # Save zoom level to config
            self.config_manager.set_value("preview", "zoom_level", self.zoom_level)
            
            # Save config to file
            if self.config_manager.save_config():
                # Mark settings as no longer modified
                self.settings_modified = False
                self.update_save_button_state()
                # Show confirmation using QMessageBox
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Settings Saved", 
                    f"Zoom level saved as default: {self.zoom_level}%")
            else:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Save Failed", 
                    "Failed to save zoom level as default.") 