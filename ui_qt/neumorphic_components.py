"""
Shared neumorphic components for the Simplified Math Editor (PyQt5).

This module contains reusable neumorphic UI components that can be used
across different parts of the application.
"""

from PyQt5.QtWidgets import QPushButton, QLineEdit, QTextEdit
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QRectF
from ui_qt.style_config import (
    FONT_FAMILY, BUTTON_FONT_SIZE, ENTRY_FONT_SIZE, NOTES_FONT_SIZE,
    NEUMORPH_BG_COLOR, NEUMORPH_SHADOW_DARK, NEUMORPH_SHADOW_LIGHT, 
    NEUMORPH_RADIUS, BUTTON_BORDER_RADIUS, BUTTON_BG_COLOR, BUTTON_FONT_COLOR, 
    ENTRY_BORDER_RADIUS, ENTRY_BG_COLOR, ENTRY_FONT_COLOR, NOTES_BG_COLOR, 
    NOTES_FONT_COLOR, NOTES_BORDER_RADIUS, BUTTON_MIN_WIDTH, BUTTON_MIN_HEIGHT, 
    ENTRY_MIN_HEIGHT, ENTRY_PADDING_LEFT, TEXTEDIT_PADDING, SHADOW_RECT_ADJUST, 
    SHADOW_OFFSETS, NOTES_FIXED_HEIGHT, CATEGORY_BTN_SELECTED_COLOR
)

class NeumorphicButton(QPushButton):
    """Neumorphic styled button with multi-layered shadow effects"""
    
    def __init__(self, text, parent=None, radius=NEUMORPH_RADIUS, bg_color=NEUMORPH_BG_COLOR, 
                 shadow_dark=NEUMORPH_SHADOW_DARK, shadow_light=NEUMORPH_SHADOW_LIGHT, 
                 font_family=FONT_FAMILY, font_size=BUTTON_FONT_SIZE, font_color=BUTTON_FONT_COLOR):
        super().__init__(text, parent)
        self.radius = radius
        self.bg_color = bg_color
        self.shadow_dark = shadow_dark
        self.shadow_light = shadow_light
        self.setFont(QFont(font_family, font_size, QFont.Bold))
        self.setStyleSheet(f"color: {font_color}; background: transparent;")
        self.setCursor(Qt.PointingHandCursor)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        # Draw shadows
        shadow_rect = rect.adjusted(2, 2, -2, -2)
        painter.setBrush(QColor(self.shadow_light))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(shadow_rect.translated(-2, -2), self.radius, self.radius)
        painter.setBrush(QColor(self.shadow_dark))
        painter.drawRoundedRect(shadow_rect.translated(2, 2), self.radius, self.radius)
        # Draw main button
        painter.setBrush(QColor(self.bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, self.radius, self.radius)
        # Draw text
        painter.setPen(QColor(self.palette().buttonText().color()))
        painter.setFont(self.font())
        painter.drawText(rect, Qt.AlignCenter, self.text())

class NeumorphicEntry(QLineEdit):
    """Neumorphic styled entry field with inset shadow effects"""
    
    def __init__(self, parent=None, radius=ENTRY_BORDER_RADIUS, bg_color=ENTRY_BG_COLOR, 
                 shadow_dark=NEUMORPH_SHADOW_DARK, shadow_light=NEUMORPH_SHADOW_LIGHT, 
                 font_family=FONT_FAMILY, font_size=ENTRY_FONT_SIZE, font_color=ENTRY_FONT_COLOR):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = bg_color
        self.shadow_dark = shadow_dark
        self.shadow_light = shadow_light
        self.setFont(QFont(font_family, font_size))
        self.setStyleSheet(f"color: {font_color}; background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        # Draw shadows
        shadow_rect = rect.adjusted(2, 2, -2, -2)
        painter.setBrush(QColor(self.shadow_light))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(shadow_rect.translated(-2, -2), self.radius, self.radius)
        painter.setBrush(QColor(self.shadow_dark))
        painter.drawRoundedRect(shadow_rect.translated(2, 2), self.radius, self.radius)
        # Draw main entry
        painter.setBrush(QColor(self.bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, self.radius, self.radius)
        # Draw text and cursor
        super().paintEvent(event)

class NeumorphicTextEdit(QTextEdit):
    """Neumorphic styled text edit area with inset shadow effects"""
    
    def __init__(self, parent=None, radius=NOTES_BORDER_RADIUS, bg_color=NOTES_BG_COLOR, 
                 shadow_dark=NEUMORPH_SHADOW_DARK, shadow_light=NEUMORPH_SHADOW_LIGHT, 
                 font_family=FONT_FAMILY, font_size=NOTES_FONT_SIZE, font_color=NOTES_FONT_COLOR):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = bg_color
        self.shadow_dark = shadow_dark
        self.shadow_light = shadow_light
        self.setFont(QFont(font_family, font_size))
        self.setStyleSheet(f"color: {font_color}; background: transparent;")

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()
        # Draw shadows
        shadow_rect = rect.adjusted(2, 2, -2, -2)
        painter.setBrush(QColor(self.shadow_light))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(shadow_rect.translated(-2, -2), self.radius, self.radius)
        painter.setBrush(QColor(self.shadow_dark))
        painter.drawRoundedRect(shadow_rect.translated(2, 2), self.radius, self.radius)
        # Draw main text edit
        painter.setBrush(QColor(self.bg_color))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, self.radius, self.radius)
        # Draw text and cursor
        super().paintEvent(event)