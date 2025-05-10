"""
Category panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import QWidget, QGridLayout, QToolButton
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont, QLinearGradient
from PyQt5.QtCore import Qt
from db.problem_database import ProblemDatabase
from ui_qt.style_config import CATEGORY_BTN_WIDTH, CATEGORY_BTN_HEIGHT, CATEGORY_BTN_SELECTED_COLOR, CATEGORY_PANEL_SPACING, FONT_FAMILY, BUTTON_FONT_SIZE, NEUMORPH_RADIUS, NEUMORPH_BG_COLOR, NEUMORPH_SHADOW_DARK, NEUMORPH_SHADOW_LIGHT, NEUMORPH_GRADIENT_START, NEUMORPH_GRADIENT_END

class NeumorphicToolButton(QToolButton):
    def __init__(self, text, parent=None, radius=NEUMORPH_RADIUS, font_family=FONT_FAMILY, font_size=BUTTON_FONT_SIZE):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self.radius = radius
        self.font_family = font_family
        self.font_size = font_size
        self.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        self.setMinimumWidth(CATEGORY_BTN_WIDTH)
        self.setMinimumHeight(CATEGORY_BTN_HEIGHT)
        self.setStyleSheet("color: #664103;")

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(6, 6, -6, -6)
        if self.isChecked():
            # Inset effect for checked state
            for i, alpha in zip([8, 6, 4], [40, 60, 90]):
                shadow = QColor(NEUMORPH_SHADOW_DARK)
                shadow.setAlpha(alpha)
                painter.setBrush(QBrush(shadow))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
            for i, alpha in zip([8, 6, 4], [30, 50, 80]):
                highlight = QColor(NEUMORPH_SHADOW_LIGHT)
                highlight.setAlpha(alpha)
                painter.setBrush(QBrush(highlight))
                painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
            grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
            grad.setColorAt(0, QColor(NEUMORPH_GRADIENT_END))
            grad.setColorAt(1, QColor(NEUMORPH_GRADIENT_START))
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(rect, self.radius, self.radius)
        else:
            # Raised effect for normal state
            for i, alpha in zip([8, 6, 4], [40, 60, 90]):
                shadow = QColor(NEUMORPH_SHADOW_DARK)
                shadow.setAlpha(alpha)
                painter.setBrush(QBrush(shadow))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
            for i, alpha in zip([8, 6, 4], [30, 50, 80]):
                highlight = QColor(NEUMORPH_SHADOW_LIGHT)
                highlight.setAlpha(alpha)
                painter.setBrush(QBrush(highlight))
                painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
            grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
            grad.setColorAt(0, QColor(NEUMORPH_GRADIENT_START))
            grad.setColorAt(1, QColor(NEUMORPH_BG_COLOR))
            painter.setBrush(QBrush(grad))
            painter.drawRoundedRect(rect, self.radius, self.radius)
        # Text
        painter.setPen(QColor("#664103"))
        painter.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, self.text())

class CategoryPanelQt(QWidget):
    def __init__(self, categories=None, parent=None):
        super().__init__(parent)
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