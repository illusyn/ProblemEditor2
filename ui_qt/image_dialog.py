"""
Image dialogs for the Simplified Math Editor (PyQt5).

This module provides dialog windows for image operations, including advanced image size adjustment.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QCheckBox, QPushButton
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from pathlib import Path
from PIL import Image
import os

class ImageSizeAdjustDialog(QDialog):
    """Dialog for adjusting image height (in cm) with aspect ratio, PyQt5 version."""
    def __init__(self, parent, image_path, current_height_cm=6.0, apply_callback=None):
        super().__init__(parent)
        self.setWindowTitle("Adjust Image Height")
        self.setMinimumSize(600, 600)
        self.image_path = image_path
        self.apply_callback = apply_callback
        self.result = None

        # Widgets
        self.height_spin = QDoubleSpinBox()
        self.height_spin.setRange(1.00, 12.00)
        self.height_spin.setSingleStep(0.10)
        self.height_spin.setValue(current_height_cm)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedSize(500, 400)
        self.apply_button = QPushButton("Apply")
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")

        self._setup_ui()
        self._connect_signals()
        self._update_preview()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        # Height control
        height_layout = QHBoxLayout()
        height_layout.addWidget(QLabel("Height (cm):"))
        height_layout.addWidget(self.height_spin)
        layout.addLayout(height_layout)
        # Preview
        layout.addWidget(QLabel("Preview:"))
        layout.addWidget(self.preview_label)
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.apply_button)
        btn_layout.addWidget(self.ok_button)
        btn_layout.addWidget(self.cancel_button)
        layout.addLayout(btn_layout)

    def _connect_signals(self):
        self.height_spin.valueChanged.connect(self._update_preview)
        self.apply_button.clicked.connect(self._on_apply)
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)

    def _update_preview(self):
        try:
            print(f"Trying to open image: {self.image_path}")
            if not os.path.exists(self.image_path):
                self.preview_label.setText(f"[Image not found: {self.image_path}]")
                print(f"Image not found: {self.image_path}")
                return
            img = Image.open(self.image_path)
            print(f"Image opened: {img.size}, mode: {img.mode}")
            img = img.convert("RGB")  # Ensure RGB mode
            # For preview, just scale to fit the label, keeping aspect ratio
            qimg = QImage(
                img.tobytes("raw", "RGB"),
                img.width,
                img.height,
                img.width * 3,  # bytes per line (stride)
                QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(qimg)
            scaled_pixmap = pixmap.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
            print("Image displayed in dialog.")
        except Exception as e:
            self.preview_label.setText(f"[Preview error: {e}]")
            print(f"Preview error: {e}")

    def _on_apply(self):
        if self.apply_callback:
            self.apply_callback(self.height_spin.value())
        self._update_preview()

    def _on_ok(self):
        self.result = self.height_spin.value()
        if self.apply_callback:
            self.apply_callback(self.height_spin.value())
        self.accept()

    def get_result(self):
        return self.result 