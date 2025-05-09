"""
Editor panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtGui import QFont
from ui_qt.style_config import EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE

class EditorPanel(QWidget):
    def __init__(self, parent=None, font_family=EDITOR_FONT_FAMILY, font_size=EDITOR_FONT_SIZE):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Editor"))
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumSize(400, 300)
        font = QFont(font_family, font_size)
        self.text_edit.setFont(font)
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