"""
Editor panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtGui import QFont

class EditorPanel(QWidget):
    def __init__(self, parent=None, font_family="Courier", font_size=14):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Editor"))
        self.text_edit = QTextEdit()
        self.text_edit.setMinimumSize(400, 300)
        font = QFont(font_family, font_size)
        self.text_edit.setFont(font)
        layout.addWidget(self.text_edit) 