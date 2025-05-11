"""
Image dialogs for the Simplified Math Editor (PyQt5).

This module provides dialog windows for image operations, including advanced image size adjustment.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QCheckBox, QPushButton, QSlider
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
from pathlib import Path
from PIL import Image
import os

class ImageSizeAdjustDialog(QDialog):
    """Dialog for adjusting image height (in cm) with aspect ratio, PyQt5 version."""
    def __init__(self, parent, image_path, current_height_cm=6.0, apply_callback=None, margin_top=0.0, margin_left=0.0, margin_bottom=0.0):
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
        # Add slider for height
        self.height_slider = QSlider(Qt.Horizontal)
        self.height_slider.setRange(100, 1200)  # Represents 1.00 to 12.00 cm
        self.height_slider.setSingleStep(1)
        self.height_slider.setValue(int(current_height_cm * 100))
        # Margin controls
        self.margin_top_spin = QDoubleSpinBox()
        self.margin_top_spin.setRange(0.00, 5.00)
        self.margin_top_spin.setSingleStep(0.05)
        self.margin_top_spin.setValue(margin_top)
        self.margin_left_spin = QDoubleSpinBox()
        self.margin_left_spin.setRange(0.00, 5.00)
        self.margin_left_spin.setSingleStep(0.05)
        self.margin_left_spin.setValue(margin_left)
        self.margin_bottom_spin = QDoubleSpinBox()
        self.margin_bottom_spin.setRange(0.00, 5.00)
        self.margin_bottom_spin.setSingleStep(0.05)
        self.margin_bottom_spin.setValue(margin_bottom)
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
        # Add slider below spinbox
        layout.addWidget(self.height_slider)
        # Margin controls
        margin_layout = QHBoxLayout()
        margin_layout.addWidget(QLabel("Top margin (cm):"))
        margin_layout.addWidget(self.margin_top_spin)
        margin_layout.addWidget(QLabel("Left margin (cm):"))
        margin_layout.addWidget(self.margin_left_spin)
        margin_layout.addWidget(QLabel("Bottom margin (cm):"))
        margin_layout.addWidget(self.margin_bottom_spin)
        layout.addLayout(margin_layout)
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
        self.height_spin.valueChanged.connect(self._on_spinbox_changed)
        self.height_slider.valueChanged.connect(self._on_slider_changed)
        self.apply_button.clicked.connect(self._on_apply)
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)

    def _on_spinbox_changed(self, value):
        slider_val = int(round(value * 100))
        if self.height_slider.value() != slider_val:
            self.height_slider.setValue(slider_val)
        self._update_preview()

    def _on_slider_changed(self, value):
        spin_val = value / 100.0
        if abs(self.height_spin.value() - spin_val) > 0.005:
            self.height_spin.setValue(spin_val)
        # self._update_preview()  # Already called by spinbox if needed

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

    def get_margin_values(self):
        return {
            'top': self.margin_top_spin.value(),
            'left': self.margin_left_spin.value(),
            'bottom': self.margin_bottom_spin.value()
        } 