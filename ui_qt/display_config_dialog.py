# display_config_dialog.py
"""
Display Configuration dialog for the Problem Display Panel.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QDialogButtonBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
from ui_qt.style_config import (
    FONT_FAMILY, LABEL_FONT_SIZE, BUTTON_FONT_SIZE,
    NEUMORPH_TEXT_COLOR, WINDOW_BG_COLOR, BUTTON_TEXT_PADDING
)


class DisplayConfigDialog(QDialog):
    """Dialog for configuring display options"""
    
    # Signal emitted when configuration changes
    config_changed = pyqtSignal(dict)
    
    def __init__(self, current_font_size=14, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Display Configuration")
        self.setModal(True)
        self.setFixedWidth(300)
        
        # Store current settings
        self.current_font_size = current_font_size
        
        # Setup UI
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Font size section
        font_row = QHBoxLayout()
        font_row.setSpacing(10)
        
        font_label = QLabel("Font size:")
        label_font = QFont(FONT_FAMILY)
        label_font.setPointSizeF(LABEL_FONT_SIZE)
        font_label.setFont(label_font)
        font_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(i) for i in range(10, 33)])
        self.font_size_combo.setCurrentText(str(self.current_font_size))
        combo_font = QFont(FONT_FAMILY)
        combo_font.setPointSizeF(LABEL_FONT_SIZE)
        self.font_size_combo.setFont(combo_font)
        self.font_size_combo.setStyleSheet(f"""
            QComboBox {{
                background-color: #e0e0e3;
                color: {NEUMORPH_TEXT_COLOR};
                border: 1px solid #b0b0b3;
                border-radius: 4px;
                padding: 5px;
                min-width: 60px;
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {NEUMORPH_TEXT_COLOR};
                width: 0;
                height: 0;
                margin-right: 5px;
            }}
        """)
        
        font_row.addWidget(font_label)
        font_row.addWidget(self.font_size_combo)
        font_row.addStretch()
        
        layout.addLayout(font_row)
        
        # Save button
        self.save_btn = QPushButton("Save as Default")
        save_font = QFont(FONT_FAMILY)
        save_font.setPointSizeF(BUTTON_FONT_SIZE)
        self.save_btn.setFont(save_font)
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #e0e0e3;
                color: {NEUMORPH_TEXT_COLOR};
                border: 1px solid #b0b0b3;
                border-radius: 4px;
                padding: 5px 15px;
            }}
            QPushButton:hover {{
                background-color: #d0d0d3;
            }}
            QPushButton:pressed {{
                background-color: #c0c0c3;
            }}
        """)
        layout.addWidget(self.save_btn)
        
        # Dialog buttons
        button_box = QDialogButtonBox()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        # Style the dialog buttons
        for btn in [self.ok_button, self.cancel_button]:
            btn_font = QFont(FONT_FAMILY)
            btn_font.setPointSizeF(BUTTON_FONT_SIZE)
            btn.setFont(btn_font)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #e0e0e3;
                    color: {NEUMORPH_TEXT_COLOR};
                    border: 1px solid #b0b0b3;
                    border-radius: 4px;
                    padding: 5px 15px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: #d0d0d3;
                }}
                QPushButton:pressed {{
                    background-color: #c0c0c3;
                }}
            """)
        
        button_box.addButton(self.ok_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addSpacing(10)
        layout.addWidget(button_box)
        
        # Connect save button
        self.save_btn.clicked.connect(self._on_save_clicked)
        
    def _on_save_clicked(self):
        """Handle save button click"""
        # Emit signal to save the configuration
        config = self.get_config()
        self.config_changed.emit(config)
        
        # Update button text to show it was saved
        self.save_btn.setText("Saved!")
        # Reset text after a moment
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(1500, lambda: self.save_btn.setText("Save as Default"))
    
    def get_config(self):
        """Get the current configuration"""
        return {
            'font_size': int(self.font_size_combo.currentText())
        }