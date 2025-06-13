"""
Category panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import QWidget, QGridLayout, QToolButton
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont, QLinearGradient
from PyQt5.QtCore import Qt
from db.problem_database import ProblemDatabase
from ui_qt.style_config import CATEGORY_BTN_WIDTH, CATEGORY_BTN_HEIGHT, CATEGORY_BTN_SELECTED_COLOR, CATEGORY_PANEL_SPACING, FONT_FAMILY, BUTTON_FONT_SIZE, NEUMORPH_RADIUS, NEUMORPH_BG_COLOR, NEUMORPH_SHADOW_DARK, NEUMORPH_SHADOW_LIGHT, NEUMORPH_SHADOW_BLUE, NEUMORPH_GRADIENT_START, NEUMORPH_GRADIENT_END, NEUMORPH_TEXT_COLOR, SHADOW_OFFSETS, SHADOW_ALPHAS, HIGHLIGHT_OFFSETS, HIGHLIGHT_ALPHAS

class NeumorphicToolButton(QToolButton):
    def __init__(self, text, parent=None, radius=NEUMORPH_RADIUS, font_family=FONT_FAMILY, font_size=BUTTON_FONT_SIZE):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self.radius = radius
        self.font_family = font_family
        self.font_size = font_size
        font = QFont(self.font_family)
        font.setPointSizeF(self.font_size)
        font.setWeight(QFont.Bold)
        self.setFont(font)
        self.setMinimumWidth(CATEGORY_BTN_WIDTH)
        self.setMinimumHeight(CATEGORY_BTN_HEIGHT)
        self.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
 
    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect().adjusted(4, 4, -4, -4)
            full_radius = self.radius
            if self.isChecked():
                # Enhanced inset effect for checked state with blue shadows
                for offset, alpha in zip(SHADOW_OFFSETS, SHADOW_ALPHAS):
                    shadow = QColor(NEUMORPH_SHADOW_BLUE)
                    shadow.setAlpha(alpha)
                    painter.setBrush(QBrush(shadow))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(rect.translated(-offset, -offset), full_radius, full_radius)
                for offset, alpha in zip(HIGHLIGHT_OFFSETS, HIGHLIGHT_ALPHAS):
                    highlight = QColor(NEUMORPH_SHADOW_LIGHT)
                    highlight.setAlpha(alpha)
                    painter.setBrush(QBrush(highlight))
                    painter.drawRoundedRect(rect.translated(offset, offset), full_radius, full_radius)
                # Solid color for checked state
                painter.setBrush(QBrush(QColor(CATEGORY_BTN_SELECTED_COLOR)))
                painter.drawRoundedRect(rect, full_radius, full_radius)
            else:
                # Enhanced raised effect for normal state with blue shadows
                for offset, alpha in zip(SHADOW_OFFSETS, SHADOW_ALPHAS):
                    shadow = QColor(NEUMORPH_SHADOW_BLUE)
                    shadow.setAlpha(alpha)
                    painter.setBrush(QBrush(shadow))
                    painter.setPen(Qt.NoPen)
                    painter.drawRoundedRect(rect.translated(offset, offset), full_radius, full_radius)
                for offset, alpha in zip(HIGHLIGHT_OFFSETS, HIGHLIGHT_ALPHAS):
                    highlight = QColor(NEUMORPH_SHADOW_LIGHT)
                    highlight.setAlpha(alpha)
                    painter.setBrush(QBrush(highlight))
                    painter.drawRoundedRect(rect.translated(-offset, -offset), full_radius, full_radius)
                # Solid color for normal state
                painter.setBrush(QBrush(QColor(NEUMORPH_BG_COLOR)))
                painter.drawRoundedRect(rect, full_radius, full_radius)
            # Text - apply shadow effect only for small font sizes
            paint_font = QFont(self.font_family)
            paint_font.setPointSizeF(self.font_size)
            paint_font.setWeight(QFont.Bold)
            painter.setFont(paint_font)
            
            # Apply shadow effect only for small fonts (14pt and below)
            if self.font_size <= 14:
                # Draw text shadow for bolder effect
                shadow_color = QColor(NEUMORPH_TEXT_COLOR)
                shadow_color.setAlpha(80)  # Semi-transparent shadow
                
                # Draw multiple shadow layers for thicker effect
                shadow_offsets = [(1, 0), (0, 1), (-1, 0), (0, -1)]  # Create outline effect
                for dx, dy in shadow_offsets:
                    painter.setPen(shadow_color)
                    painter.drawText(rect.translated(dx, dy), Qt.AlignCenter, self.text())
            
            # Draw main text on top
            painter.setPen(QColor(NEUMORPH_TEXT_COLOR))
            painter.drawText(rect, Qt.AlignCenter, self.text())
        finally:
            painter.end()

class CategoryPanelQt(QWidget):
    def __init__(self, categories=None, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background: transparent;')
        if categories is None:
            db = ProblemDatabase()
            self.categories = db.get_all_categories()
        else:
            self.categories = categories
        self.selected = set()  # store category_id
        self.buttons = {}      # key: category_id, value: button
        layout = QGridLayout(self)
        layout.setSpacing(CATEGORY_PANEL_SPACING)
        for idx, cat in enumerate(self.categories):
            btn = NeumorphicToolButton(cat["name"], font_size=BUTTON_FONT_SIZE)
            btn.clicked.connect(lambda checked, cid=cat["category_id"]: self.toggle_category(cid))
            layout.addWidget(btn, idx // 2, idx % 2)
            self.buttons[cat["category_id"]] = btn

    def toggle_category(self, category_id):
        btn = self.buttons[category_id]
        if btn.isChecked():
            self.selected.add(category_id)
        else:
            self.selected.discard(category_id)

    def get_selected_categories(self):
        # Return list of selected category dicts
        return [cat for cat in self.categories if cat["category_id"] in self.selected]

    def clear_selection(self):
        """Clear all selected categories"""
        for btn in self.buttons.values():
            btn.setChecked(False)
        self.selected.clear() 