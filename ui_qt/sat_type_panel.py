"""
SAT Problem Type panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox
from PyQt5.QtGui import QFont
from ui_qt.style_config import FONT_FAMILY, SAT_TYPE_FONT_SIZE, SAT_TYPE_FONT_COLOR, SAT_TYPE_PANEL_SPACING

EXAMPLE_SAT_TYPES = [
    "Efficiency", "Math Concept", "SAT Problem"
]

class SatTypePanelQt(QWidget):
    def __init__(self, types=None, parent=None):
        super().__init__(parent)
        self.types = types or EXAMPLE_SAT_TYPES
        self.checkboxes = {}
        layout = QVBoxLayout(self)
        layout.setSpacing(SAT_TYPE_PANEL_SPACING)
        for t in self.types:
            cb = QCheckBox(t)
            cb.setFont(QFont(FONT_FAMILY, SAT_TYPE_FONT_SIZE, QFont.Bold))
            cb.setStyleSheet(f"color: {SAT_TYPE_FONT_COLOR};")
            layout.addWidget(cb)
            self.checkboxes[t] = cb

    def get_selected_types(self):
        return [t for t, cb in self.checkboxes.items() if cb.isChecked()] 