"""
Preview panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel

class PreviewPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Preview"))
        self.preview_label = QLabel("[Preview output will appear here]")
        self.preview_label.setMinimumSize(400, 300)
        layout.addWidget(self.preview_label) 