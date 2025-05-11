"""
PyQt5 entry point for the Simplified Math Editor (migration skeleton).
"""

import sys
import re
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QGuiApplication
from PyQt5.QtCore import Qt
from ui_qt.main_window import MainWindow
from ui_qt.style_config import set_scale_from_dpi, set_laptop_mode

class NeumorphicButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 16px;
                color: #333;
                font-size: 18px;
                padding: 16px 32px;
            }
            QPushButton:pressed {
                background-color: #d1d9e6;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(24)
        shadow.setXOffset(4)
        shadow.setYOffset(4)
        shadow.setColor(QColor(163, 177, 198, 120))
        self.setGraphicsEffect(shadow)

class NeumorphicLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QLineEdit {
                background-color: #e0e0e0;
                border: none;
                border-radius: 16px;
                color: #333;
                font-size: 16px;
                padding: 12px 20px;
            }
        """)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(16)
        shadow.setXOffset(2)
        shadow.setYOffset(2)
        shadow.setColor(QColor(163, 177, 198, 100))
        self.setGraphicsEffect(shadow)

class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: #f0f0f3;")
        layout = QVBoxLayout(self)
        layout.setSpacing(30)
        layout.setContentsMargins(60, 60, 60, 60)
        self.button = NeumorphicButton("Sign Up")
        self.input = NeumorphicLineEdit()
        self.input.setPlaceholderText("Enter your username")
        layout.addWidget(self.input)
        layout.addWidget(self.button)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Get the primary screen's DPI
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch() if screen else 96
    set_scale_from_dpi(dpi)
    laptop_mode = any(arg == "--laptop" for arg in sys.argv)
    set_laptop_mode(laptop_mode)
    window = MainWindow(laptop_mode=laptop_mode)
    # Print the minimum window size for debugging
    print(f"Minimum window size: {window.minimumSize().width()} x {window.minimumSize().height()}")
    print(f"Minimum size hint: {window.minimumSizeHint().width()} x {window.minimumSizeHint().height()}")
    # Parse --resolution=WIDTHxHEIGHT from command line
    res_match = None
    for arg in sys.argv:
        res_match = re.match(r"--resolution=(\d+)x(\d+)", arg)
        if res_match:
            break
    if res_match:
        width, height = int(res_match.group(1)), int(res_match.group(2))
        window.resize(width, height)
    window.show()
    sys.exit(app.exec_()) 