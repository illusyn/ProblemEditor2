"""
Image dialogs for the Simplified Math Editor (PyQt5).

This module provides dialog windows for image operations, including advanced image size adjustment.
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QDoubleSpinBox, QSpinBox, QCheckBox, QPushButton, QSlider
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
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
        self._debounce_timer = QTimer(self)
        self._debounce_timer.setSingleShot(True)
        self._debounce_timer.setInterval(70)
        self._debounce_timer.timeout.connect(self._on_user_paused)

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
        self.height_slider.sliderReleased.connect(self._on_slider_released)
        self.apply_button.clicked.connect(self._on_apply)
        self.ok_button.clicked.connect(self._on_ok)
        self.cancel_button.clicked.connect(self.reject)
        self.margin_top_spin.valueChanged.connect(self._on_margin_changed)
        self.margin_left_spin.valueChanged.connect(self._on_margin_changed)
        self.margin_bottom_spin.valueChanged.connect(self._on_margin_changed)
        self.margin_top_spin.editingFinished.connect(self._on_margin_editing_finished)
        self.margin_left_spin.editingFinished.connect(self._on_margin_editing_finished)
        self.margin_bottom_spin.editingFinished.connect(self._on_margin_editing_finished)

    def _on_spinbox_changed(self, value):
        slider_val = int(round(value * 100))
        if self.height_slider.value() != slider_val:
            self.height_slider.setValue(slider_val)
        self._update_preview()
        self._debounce_timer.start()

    def _on_slider_changed(self, value):
        spin_val = value / 100.0
        if abs(self.height_spin.value() - spin_val) > 0.005:
            self.height_spin.setValue(spin_val)
        self._update_preview()
        self._debounce_timer.start()

    def _on_slider_released(self):
        self._debounce_timer.start()

    def _on_margin_changed(self, value):
        self._update_preview()
        self._debounce_timer.start()

    def _on_margin_editing_finished(self):
        self._debounce_timer.start()

    def _on_user_paused(self):
        if self.apply_callback:
            self.apply_callback(self.height_spin.value())
        parent = self.parent()
        if hasattr(parent, 'update_preview'):
            parent.update_preview()

    def _update_preview(self):
        try:
            print(f"Trying to open image: {self.image_path}")
            if not os.path.exists(self.image_path):
                self.preview_label.setText(f"[Image not found: {self.image_path}]")
                print(f"Image not found: {self.image_path}")
                return

            # Load and convert image
            img = Image.open(self.image_path).convert("RGB")
            orig_w, orig_h = img.size

            # Get user settings
            height_cm = self.height_spin.value()
            margin_top = self.margin_top_spin.value()
            margin_left = self.margin_left_spin.value()
            margin_bottom = self.margin_bottom_spin.value()

            # Preview label size
            label_w = self.preview_label.width()
            label_h = self.preview_label.height()

            # Assume 1cm = 37.8 px (typical screen, for preview only)
            px_per_cm = 37.8
            target_h = int(height_cm * px_per_cm)
            scale = target_h / orig_h
            target_w = int(orig_w * scale)

            # Margins in px
            margin_top_px = int(margin_top * px_per_cm)
            margin_left_px = int(margin_left * px_per_cm)
            margin_bottom_px = int(margin_bottom * px_per_cm)

            # Create new image with margins
            canvas_w = target_w + margin_left_px * 2
            canvas_h = target_h + margin_top_px + margin_bottom_px

            # Resize image
            img_resized = img.resize((target_w, target_h), Image.LANCZOS)
            canvas = Image.new("RGB", (canvas_w, canvas_h), (240, 240, 240))  # Light gray background
            canvas.paste(img_resized, (margin_left_px, margin_top_px))

            # Convert to QImage/QPixmap for display
            qimg = QImage(
                canvas.tobytes("raw", "RGB"),
                canvas.width,
                canvas.height,
                canvas.width * 3,
                QImage.Format_RGB888
            )
            pixmap = QPixmap.fromImage(qimg)
            scaled_pixmap = pixmap.scaled(label_w, label_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled_pixmap)
            print("Image displayed in dialog with margins and height.")
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