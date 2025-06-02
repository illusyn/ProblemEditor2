"""
PyQt5 entry point for the Simplified Math Editor (migration skeleton).
"""

import sys
import re
# Parse --scale flag before any UI imports
scale = 1.0
for arg in sys.argv:
    m = re.match(r"--scale=([0-9.]+)", arg)
    if m:
        scale = float(m.group(1))
        break
# Now import the rest of the modules
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QGraphicsDropShadowEffect
from PyQt5.QtGui import QColor, QGuiApplication
from PyQt5.QtCore import Qt, QTimer
from ui_qt.main_window import MainWindow
from ui_qt.style_config import set_scale

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Get the primary screen's DPI
    screen = QGuiApplication.primaryScreen()
    dpi = screen.logicalDotsPerInch() if screen else 96
    set_scale('main')  # Or 'laptop' if running on laptop; add DPI logic if needed
    window = MainWindow(laptop_mode=(scale < 1.0))
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

    def print_main_window_size_hints():
        print("[DEBUG] MainWindow minimumSizeHint:", window.minimumSizeHint())
        print("[DEBUG] MainWindow sizeHint:", window.sizeHint())
        if hasattr(window, 'problem_manager_screen'):
            print("[DEBUG] ProblemManager minimumSizeHint:", window.problem_manager_screen.minimumSizeHint())
            print("[DEBUG] ProblemManager sizeHint:", window.problem_manager_screen.sizeHint())
            if hasattr(window.problem_manager_screen, 'query_panel'):
                print("[DEBUG] QueryPanel minimumSizeHint:", window.problem_manager_screen.query_panel.minimumSizeHint())
                print("[DEBUG] QueryPanel sizeHint:", window.problem_manager_screen.query_panel.sizeHint())
            if hasattr(window.problem_manager_screen, 'problem_display_panel'):
                print("[DEBUG] ProblemDisplayPanel minimumSizeHint:", window.problem_manager_screen.problem_display_panel.minimumSizeHint())
                print("[DEBUG] ProblemDisplayPanel sizeHint:", window.problem_manager_screen.problem_display_panel.sizeHint())
            if hasattr(window.problem_manager_screen.query_panel, 'problem_set_panel'):
                print("[DEBUG] ProblemSetPanel minimumSizeHint:", window.problem_manager_screen.query_panel.problem_set_panel.minimumSizeHint())
                print("[DEBUG] ProblemSetPanel sizeHint:", window.problem_manager_screen.query_panel.problem_set_panel.sizeHint())

    # QTimer.singleShot(1000, print_main_window_size_hints)
    sys.exit(app.exec_()) 