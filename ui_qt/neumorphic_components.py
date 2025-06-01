"""
Shared neumorphic components for the Simplified Math Editor (PyQt5).

This module contains reusable neumorphic UI components that can be used
across different parts of the application.
"""

from PyQt5.QtWidgets import QPushButton, QLineEdit, QTextEdit
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush
from PyQt5.QtCore import Qt
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
    
    def __init__(self, text, parent=None, radius=None, bg_color=None, 
                 shadow_dark=None, shadow_light=None, font_family=None, 
                 font_size=None, font_color=None):
        super().__init__(text, parent)
        
        # Use provided values or defaults
        self.radius = radius or NEUMORPH_RADIUS
        self.bg_color = bg_color or NEUMORPH_BG_COLOR
        self.shadow_dark = shadow_dark or NEUMORPH_SHADOW_DARK
        self.shadow_light = shadow_light or NEUMORPH_SHADOW_LIGHT
        self.font_family = font_family or FONT_FAMILY
        self.font_size = font_size or BUTTON_FONT_SIZE
        self.font_color = font_color or BUTTON_FONT_COLOR
        
        # Set font and basic styling
        self.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        self.setStyleSheet("background: transparent; border: none;")
        self.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect().adjusted(SHADOW_RECT_ADJUST, SHADOW_RECT_ADJUST, 
                                      -SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST)
            
            # Multi-layered blurred shadow (bottom-right)
            for i, alpha in zip(SHADOW_OFFSETS, [40, 60, 90]):
                shadow = QColor(self.shadow_dark)
                shadow.setAlpha(alpha)
                painter.setBrush(QBrush(shadow))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
            
            # Multi-layered highlight (top-left)
            for i, alpha in zip(SHADOW_OFFSETS, [30, 50, 80]):
                highlight = QColor(self.shadow_light)
                highlight.setAlpha(alpha)
                painter.setBrush(QBrush(highlight))
                painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
            
            # Solid background (highlight if checked)
            if self.isCheckable() and self.isChecked():
                painter.setBrush(QBrush(QColor(CATEGORY_BTN_SELECTED_COLOR)))
            else:
                painter.setBrush(QBrush(QColor(self.bg_color)))
            painter.drawRoundedRect(rect, self.radius, self.radius)
            
            # Text
            painter.setPen(QColor(self.font_color))
            painter.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
            painter.drawText(rect, Qt.AlignCenter, self.text())
        finally:
            painter.end()

class NeumorphicEntry(QLineEdit):
    """Neumorphic styled entry field with inset shadow effects"""
    
    def __init__(self, parent=None, radius=None, bg_color=None, 
                 shadow_dark=None, shadow_light=None, font_family=None, 
                 font_size=None, font_color=None):
        super().__init__(parent)
        
        # Use provided values or defaults
        self.radius = radius or ENTRY_BORDER_RADIUS
        self.bg_color = bg_color or ENTRY_BG_COLOR
        self.shadow_dark = shadow_dark or NEUMORPH_SHADOW_DARK
        self.shadow_light = shadow_light or NEUMORPH_SHADOW_LIGHT
        self.font_family = font_family or FONT_FAMILY
        self.font_size = font_size or ENTRY_FONT_SIZE
        self.font_color = font_color or ENTRY_FONT_COLOR
        
        # Set font and basic styling
        self.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        self.setStyleSheet(f"background: transparent; border: none; color: {self.font_color}; padding-left: {ENTRY_PADDING_LEFT}px;")
        self.setMinimumHeight(ENTRY_MIN_HEIGHT)

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect().adjusted(SHADOW_RECT_ADJUST, SHADOW_RECT_ADJUST, 
                                      -SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST)
            
            # Sunken effect: shadow top-left, highlight bottom-right
            for i, alpha in zip(SHADOW_OFFSETS, [40, 60, 90]):
                shadow = QColor(self.shadow_dark)
                shadow.setAlpha(alpha)
                painter.setBrush(QBrush(shadow))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
            
            for i, alpha in zip(SHADOW_OFFSETS, [30, 50, 80]):
                highlight = QColor(self.shadow_light)
                highlight.setAlpha(alpha)
                painter.setBrush(QBrush(highlight))
                painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
            
            # Solid background (no gradient)
            painter.setBrush(QBrush(QColor(self.bg_color)))
            painter.drawRoundedRect(rect, self.radius, self.radius)
            
            # Call base class paint for text/cursor
            super().paintEvent(event)
        finally:
            painter.end()

class NeumorphicTextEdit(QTextEdit):
    """Neumorphic styled text edit area with inset shadow effects"""
    
    def __init__(self, parent=None, radius=None, bg_color=None, 
                 shadow_dark=None, shadow_light=None, font_family=None, 
                 font_size=None, font_color=None, fixed_height=True):
        super().__init__(parent)
        
        # Use provided values or defaults
        self.radius = radius or NOTES_BORDER_RADIUS
        self.bg_color = bg_color or NOTES_BG_COLOR
        self.shadow_dark = shadow_dark or NEUMORPH_SHADOW_DARK
        self.shadow_light = shadow_light or NEUMORPH_SHADOW_LIGHT
        self.font_family = font_family or FONT_FAMILY
        self.font_size = font_size or NOTES_FONT_SIZE
        self.font_color = font_color or NOTES_FONT_COLOR
        
        # Set font and basic styling
        self.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        self.setStyleSheet(f"background: transparent; border: none; color: {self.font_color}; padding: {TEXTEDIT_PADDING}px;")
        
        # Set fixed height if requested
        if fixed_height:
            self.setFixedHeight(NOTES_FIXED_HEIGHT)

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect().adjusted(SHADOW_RECT_ADJUST, SHADOW_RECT_ADJUST, 
                                      -SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST)
            
            # Multi-layered blurred shadow (bottom-right)
            for i, alpha in zip(SHADOW_OFFSETS, [40, 60, 90]):
                shadow = QColor(self.shadow_dark)
                shadow.setAlpha(alpha)
                painter.setBrush(QBrush(shadow))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
            
            # Multi-layered highlight (top-left)
            for i, alpha in zip(SHADOW_OFFSETS, [30, 50, 80]):
                highlight = QColor(self.shadow_light)
                highlight.setAlpha(alpha)
                painter.setBrush(QBrush(highlight))
                painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
            
            # Solid background (no gradient)
            painter.setBrush(QBrush(QColor(self.bg_color)))
            painter.drawRoundedRect(rect, self.radius, self.radius)
            
            super().paintEvent(event)
        finally:
            painter.end()