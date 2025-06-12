"""
Keyboard Shortcuts Dialog for the Simplified Math Editor.
Displays all available keyboard shortcuts in a formatted dialog.
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QScrollArea, QWidget, QPushButton, QGroupBox,
                             QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui_qt.style_config import (NEUMORPH_BG_COLOR, LABEL_FONT_COLOR, BUTTON_HIGHLIGHT_COLOR,
                                 FONT_FAMILY, BUTTON_FONT_SIZE, BUTTON_HOVER_COLOR,
                                 LABEL_FONT_SIZE)


class KeyboardShortcutsDialog(QDialog):
    """Dialog displaying all keyboard shortcuts in the application."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts")
        self.setModal(True)
        self.setMinimumSize(700, 500)  # Increased width to ensure shortcuts are visible
        self.resize(800, 600)  # Set initial size
        self.setup_ui()
        self.apply_styling()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Keyboard Shortcuts")
        title_font = QFont(FONT_FAMILY, BUTTON_FONT_SIZE + 4, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Scroll area for shortcuts
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.NoFrame)
        
        # Container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        
        # Define shortcut groups
        shortcut_groups = [
            ("Math Insertion (without dollar signs)", [
                ("Ctrl+F", "Insert fraction: \\frac{}{}"),
                ("Ctrl+D", "Insert degree symbol: ^\\circ"),
                ("Ctrl+R", "Insert half power: ^.5"),
                ("Ctrl+S", "Insert square root: \\sqrt{}"),
                ("Ctrl+T", "Insert triangle: \\bigtriangleup"),
                ("Ctrl+O", "Overline selection: \\overline{SELECTION}"),
                ("Alt+A", "Wide hat selection: \\widehat{SELECTION}"),
                ("Ctrl+A", "Insert angle: \\angle"),
                ("Ctrl+L", "Paste LaTeX as equation"),
            ]),
            ("Math Insertion (with dollar signs)", [
                ("Ctrl+Shift+F", "Insert fraction: $\\frac{}{}$"),
                ("Ctrl+Shift+D", "Insert degree: $^\\circ$"),
                ("Ctrl+Shift+R", "Insert half power: $^.5$"),
                ("Ctrl+Shift+S", "Insert square root: $\\sqrt{}$"),
                ("Ctrl+Shift+T", "Insert triangle: $\\bigtriangleup$"),
                ("Ctrl+Shift+O", "Overline selection: $\\overline{SELECTION}$"),
                ("Alt+Shift+A", "Wide hat selection: $\\widehat{SELECTION}$"),
                ("Ctrl+Shift+A", "Insert angle: $\\angle$"),
            ]),
            ("Section Markers", [
                ("Ctrl+P", "Insert problem section: #problem"),
                ("Ctrl+Alt+T", "Insert text section: #text"),
                ("Ctrl+Shift+N", "Insert vertical space: \\\\[2mm]"),
            ]),
            ("Problem Selection", [
                ("Ctrl+Click", "Toggle selection of individual problems"),
                ("Shift+Click", "Extend selection from anchor"),
                ("Shift+Drag", "Add to existing selection (rubber band)"),
            ]),
            ("Standard Editor", [
                ("Ctrl+C", "Copy"),
                ("Ctrl+V", "Paste (with LaTeX cleaning)"),
                ("Ctrl+X", "Cut"),
                ("Ctrl+Z", "Undo"),
                ("Ctrl+Y", "Redo"),
            ]),
            ("Context Menu", [
                ("Right-click", "Access context menu options"),
                ("", "• Paste LaTeX as Equation (same as Ctrl+L)"),
                ("", "• Wrap Math (for selected text)"),
                ("", "• Overline Selection (same as Ctrl+O)"),
                ("", "• Overline Selection with $ (same as Ctrl+Shift+O)"),
                ("", "• Wide Hat Selection (same as Alt+A)"),
                ("", "• Wide Hat Selection with $ (same as Alt+Shift+A)"),
            ]),
        ]
        
        # Create groups
        for group_name, shortcuts in shortcut_groups:
            group_box = QGroupBox(group_name)
            group_layout = QGridLayout()
            group_layout.setContentsMargins(10, 10, 10, 10)  # Add margins inside the group
            group_layout.setColumnMinimumWidth(0, 150)  # Minimum width for shortcut column
            group_layout.setColumnMinimumWidth(1, 300)  # Minimum width for description column
            group_layout.setColumnStretch(0, 0)  # Don't stretch shortcut column
            group_layout.setColumnStretch(1, 1)  # Stretch description column
            group_layout.setHorizontalSpacing(20)  # Add spacing between columns
            
            for row, (shortcut, description) in enumerate(shortcuts):
                if shortcut:  # Regular shortcut
                    shortcut_label = QLabel(shortcut)
                    shortcut_label.setFont(QFont(FONT_FAMILY, LABEL_FONT_SIZE, QFont.Bold))
                    shortcut_label.setStyleSheet(f"color: {LABEL_FONT_COLOR}; font-weight: bold;")
                    group_layout.addWidget(shortcut_label, row, 0, Qt.AlignLeft)
                    
                    desc_label = QLabel(description)
                    desc_label.setFont(QFont(FONT_FAMILY, LABEL_FONT_SIZE))
                    group_layout.addWidget(desc_label, row, 1, Qt.AlignLeft)
                else:  # Sub-item (no shortcut key, just description)
                    desc_label = QLabel(description)
                    desc_label.setFont(QFont(FONT_FAMILY, LABEL_FONT_SIZE))
                    desc_label.setStyleSheet("padding-left: 20px;")
                    group_layout.addWidget(desc_label, row, 0, 1, 2, Qt.AlignLeft)  # Span both columns
            
            group_box.setLayout(group_layout)
            container_layout.addWidget(group_box)
        
        # Add stretch at the bottom
        container_layout.addStretch()
        
        # Set container to scroll area
        scroll_area.setWidget(container)
        layout.addWidget(scroll_area)
        
        # Close button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.setMinimumWidth(100)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
    def apply_styling(self):
        """Apply styling to the dialog."""
        self.setStyleSheet(f"""
            QDialog {{
                background-color: {NEUMORPH_BG_COLOR};
                color: {LABEL_FONT_COLOR};
            }}
            QLabel {{
                color: {LABEL_FONT_COLOR};
            }}
            QPushButton {{
                background-color: {BUTTON_HIGHLIGHT_COLOR};
                color: {LABEL_FONT_COLOR};
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-family: {FONT_FAMILY};
                font-size: {BUTTON_FONT_SIZE}px;
            }}
            QPushButton:hover {{
                background-color: {BUTTON_HOVER_COLOR};
            }}
            QGroupBox {{
                border: 1px solid {LABEL_FONT_COLOR};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                font-family: {FONT_FAMILY};
            }}
            QGroupBox::title {{
                color: {LABEL_FONT_COLOR};
                font-weight: bold;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            QScrollArea {{
                background-color: transparent;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {NEUMORPH_BG_COLOR};
                width: 12px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical {{
                background-color: {BUTTON_HIGHLIGHT_COLOR};
                border-radius: 6px;
                min-height: 20px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {BUTTON_HOVER_COLOR};
            }}
        """)