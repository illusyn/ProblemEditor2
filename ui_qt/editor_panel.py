"""
Editor panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui_qt.style_config import (EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE, EDITOR_BG_COLOR,
                                 BUTTON_HOVER_COLOR, FONT_FAMILY, BUTTON_FONT_SIZE, BUTTON_HIGHLIGHT_COLOR,
                                 LABEL_FONT_SIZE, SMALL_BUTTON_FONT_SIZE, NEUMORPH_TEXT_COLOR)
from ui_qt.math_text_edit import MathTextEdit
from ui_qt.keyboard_shortcuts_dialog import KeyboardShortcutsDialog
from ui_qt.neumorphic_components import NeumorphicButton

class EditorPanel(QWidget):
    def __init__(self, parent=None, main_window=None, font_family=EDITOR_FONT_FAMILY, font_size=EDITOR_FONT_SIZE):
        super().__init__(parent)
        self.main_window = main_window
        self.delete_problem_callback = None  # Will be set by main window
        layout = QVBoxLayout(self)
        layout.setSpacing(4)  # Reduce spacing
        
        # Header with title and shortcuts button
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        
        # Delete Problem button (left side)
        delete_btn = NeumorphicButton("Delete Problem", font_size=SMALL_BUTTON_FONT_SIZE)
        delete_btn.setMinimumWidth(180)  # Added padding for better visual comfort
        delete_btn.setMaximumWidth(180)
        delete_btn.setMinimumHeight(32)  # Smaller height
        delete_btn.setMaximumHeight(32)
        delete_btn.setToolTip("Delete the current problem")
        # Add red tint to indicate danger action
        delete_btn.setStyleSheet("""
            QPushButton {
                color: #d32f2f;
            }
            QPushButton:hover {
                color: #b71c1c;
            }
        """)
        delete_btn.clicked.connect(self.delete_problem)
        header_layout.addWidget(delete_btn)
        
        header_layout.addStretch()
        
        # Keyboard shortcuts button (neumorphic style with small button font size)
        shortcuts_button = NeumorphicButton("Shortcuts", font_size=SMALL_BUTTON_FONT_SIZE)
        shortcuts_button.setToolTip("Show keyboard shortcuts")
        shortcuts_button.clicked.connect(self.show_shortcuts_dialog)
        shortcuts_button.setMinimumWidth(140)  # Added padding for better visual comfort
        shortcuts_button.setMinimumHeight(32)
        shortcuts_button.setMaximumHeight(32)
        header_layout.addWidget(shortcuts_button)
        
        # Paste Image button
        paste_image_button = NeumorphicButton("Paste Image", font_size=SMALL_BUTTON_FONT_SIZE)
        paste_image_button.setToolTip("Paste image from clipboard")
        paste_image_button.clicked.connect(self.paste_image)
        paste_image_button.setMinimumWidth(150)
        paste_image_button.setMinimumHeight(32)
        paste_image_button.setMaximumHeight(32)
        header_layout.addWidget(paste_image_button)
        
        layout.addLayout(header_layout)
        
        # Text editor
        self.text_edit = MathTextEdit()
        self.text_edit.setMinimumSize(400, 300)
        font = QFont(font_family)
        font.setPointSizeF(font_size)
        self.text_edit.setFont(font)
        self.text_edit.setStyleSheet(f"background: {EDITOR_BG_COLOR};")
        layout.addWidget(self.text_edit)

    def get_content(self):
        """
        Get the current content of the editor
        
        Returns:
            str: The current text content
        """
        return self.text_edit.toPlainText()

    def set_content(self, content):
        """
        Set the content of the editor
        
        Args:
            content (str): The text content to set
        """
        self.text_edit.setPlainText(content)
    
    def show_shortcuts_dialog(self):
        """Show the keyboard shortcuts dialog."""
        dialog = KeyboardShortcutsDialog(self)
        dialog.exec_()
    
    def paste_image(self):
        """Paste image from clipboard using the image manager."""
        if self.main_window and hasattr(self.main_window, 'image_manager'):
            self.main_window.image_manager.paste_image()
        else:
            # Fallback if main_window is not set
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Image manager not available")
    
    def delete_problem(self):
        """Delete the current problem using the callback from main window."""
        if self.delete_problem_callback:
            self.delete_problem_callback()
        else:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Delete function not available") 