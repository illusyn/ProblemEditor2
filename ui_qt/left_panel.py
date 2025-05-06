"""
Left panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QTextEdit, QLineEdit, QPushButton, QCheckBox, QScrollArea, QSizePolicy, QMessageBox
)
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QLinearGradient
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
from PyQt5.QtCore import Qt
from ui_qt.category_panel import CategoryPanelQt
from ui_qt.sat_type_panel import SatTypePanelQt
from ui_qt.style_config import (FONT_FAMILY, LABEL_FONT_SIZE, SECTION_LABEL_FONT_SIZE, BUTTON_FONT_SIZE, ENTRY_FONT_SIZE, NOTES_FONT_SIZE, NEUMORPH_TEXT_COLOR, NEUMORPH_BG_COLOR, NEUMORPH_SHADOW_DARK, NEUMORPH_SHADOW_LIGHT, NEUMORPH_GRADIENT_START, NEUMORPH_GRADIENT_END, NEUMORPH_RADIUS, BUTTON_BORDER_RADIUS, BUTTON_BG_COLOR, BUTTON_FONT_COLOR, ENTRY_BORDER_RADIUS, ENTRY_BG_COLOR, ENTRY_FONT_COLOR, NOTES_BG_COLOR, NOTES_FONT_COLOR, NOTES_BORDER_RADIUS, SAT_TYPE_FONT_COLOR, SAT_TYPE_FONT_SIZE, DOMAIN_BTN_FONT_SIZE, CONTROL_BTN_WIDTH, ENTRY_LABEL_FONT_SIZE)

class NeumorphicButton(QPushButton):
    def __init__(self, text, parent=None, radius=NEUMORPH_RADIUS, bg_color=NEUMORPH_BG_COLOR, shadow_dark=NEUMORPH_SHADOW_DARK, shadow_light=NEUMORPH_SHADOW_LIGHT, font_family=FONT_FAMILY, font_size=BUTTON_FONT_SIZE, font_color=BUTTON_FONT_COLOR):
        super().__init__(text, parent)
        self.radius = radius
        self.bg_color = bg_color
        self.shadow_dark = shadow_dark
        self.shadow_light = shadow_light
        self.font_family = font_family
        self.font_size = font_size
        self.font_color = font_color
        self.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        self.setStyleSheet("background: transparent; border: none;")
        self.setMinimumHeight(56)
        self.setMinimumWidth(140)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(8, 8, -8, -8)
        # Multi-layered blurred shadow (bottom-right)
        for i, alpha in zip([8, 6, 4], [40, 60, 90]):
            shadow = QColor(self.shadow_dark)
            shadow.setAlpha(alpha)
            painter.setBrush(QBrush(shadow))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
        # Multi-layered highlight (top-left)
        for i, alpha in zip([8, 6, 4], [30, 50, 80]):
            highlight = QColor(self.shadow_light)
            highlight.setAlpha(alpha)
            painter.setBrush(QBrush(highlight))
            painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
        # Main gradient background
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0, QColor(NEUMORPH_GRADIENT_START))
        grad.setColorAt(1, QColor(self.bg_color))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, self.radius, self.radius)
        # Text
        painter.setPen(QColor(self.font_color))
        painter.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        painter.drawText(rect, Qt.AlignCenter, self.text())

class NeumorphicEntry(QLineEdit):
    def __init__(self, parent=None, radius=ENTRY_BORDER_RADIUS, bg_color=ENTRY_BG_COLOR, shadow_dark=NEUMORPH_SHADOW_DARK, shadow_light=NEUMORPH_SHADOW_LIGHT, font_family=FONT_FAMILY, font_size=ENTRY_FONT_SIZE, font_color=ENTRY_FONT_COLOR):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = bg_color
        self.shadow_dark = shadow_dark
        self.shadow_light = shadow_light
        self.font_family = font_family
        self.font_size = font_size
        self.font_color = font_color
        self.setFont(QFont(self.font_family, self.font_size))
        self.setStyleSheet(f"background: transparent; border: none; color: {self.font_color}; padding-left: 14px;")
        self.setMinimumHeight(44)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(8, 8, -8, -8)
        # Sunken effect: shadow top-left, highlight bottom-right
        for i, alpha in zip([8, 6, 4], [40, 60, 90]):
            shadow = QColor(self.shadow_dark)
            shadow.setAlpha(alpha)
            painter.setBrush(QBrush(shadow))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
        for i, alpha in zip([8, 6, 4], [30, 50, 80]):
            highlight = QColor(self.shadow_light)
            highlight.setAlpha(alpha)
            painter.setBrush(QBrush(highlight))
            painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
        # Main gradient background
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0, QColor(NEUMORPH_GRADIENT_START))
        grad.setColorAt(1, QColor(self.bg_color))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, self.radius, self.radius)
        # Call base class paint for text/cursor
        super().paintEvent(event)

class NeumorphicScrollArea(QScrollArea):
    def __init__(self, parent=None, radius=NEUMORPH_RADIUS, bg_color=NEUMORPH_BG_COLOR, shadow_dark=NEUMORPH_SHADOW_DARK, shadow_light=NEUMORPH_SHADOW_LIGHT):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = bg_color
        self.shadow_dark = shadow_dark
        self.shadow_light = shadow_light
        self.setStyleSheet("background: transparent; border: none;")
        self.setFrameShape(QScrollArea.NoFrame)

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(8, 8, -8, -8)
        # Multi-layered blurred shadow (bottom-right)
        for i, alpha in zip([8, 6, 4], [40, 60, 90]):
            shadow = QColor(self.shadow_dark)
            shadow.setAlpha(alpha)
            painter.setBrush(QBrush(shadow))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
        # Multi-layered highlight (top-left)
        for i, alpha in zip([8, 6, 4], [30, 50, 80]):
            highlight = QColor(self.shadow_light)
            highlight.setAlpha(alpha)
            painter.setBrush(QBrush(highlight))
            painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
        # Main gradient background
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0, QColor(NEUMORPH_GRADIENT_START))
        grad.setColorAt(1, QColor(self.bg_color))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, self.radius, self.radius)
        super().paintEvent(event)

class NeumorphicTextEdit(QTextEdit):
    def __init__(self, parent=None, radius=NOTES_BORDER_RADIUS, bg_color=NOTES_BG_COLOR, shadow_dark=NEUMORPH_SHADOW_DARK, shadow_light=NEUMORPH_SHADOW_LIGHT, font_family=FONT_FAMILY, font_size=NOTES_FONT_SIZE, font_color=NOTES_FONT_COLOR):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = bg_color
        self.shadow_dark = shadow_dark
        self.shadow_light = shadow_light
        self.font_family = font_family
        self.font_size = font_size
        self.font_color = font_color
        self.setFont(QFont(self.font_family, self.font_size))
        self.setStyleSheet(f"background: transparent; border: none; color: {self.font_color}; padding: 16px;")
        self.setMinimumHeight(100)

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(8, 8, -8, -8)
        # Multi-layered blurred shadow (bottom-right)
        for i, alpha in zip([8, 6, 4], [40, 60, 90]):
            shadow = QColor(self.shadow_dark)
            shadow.setAlpha(alpha)
            painter.setBrush(QBrush(shadow))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
        # Multi-layered highlight (top-left)
        for i, alpha in zip([8, 6, 4], [30, 50, 80]):
            highlight = QColor(self.shadow_light)
            highlight.setAlpha(alpha)
            painter.setBrush(QBrush(highlight))
            painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
        # Main gradient background
        grad = QLinearGradient(rect.topLeft(), rect.bottomRight())
        grad.setColorAt(0, QColor(NEUMORPH_GRADIENT_START))
        grad.setColorAt(1, QColor(self.bg_color))
        painter.setBrush(QBrush(grad))
        painter.drawRoundedRect(rect, self.radius, self.radius)
        super().paintEvent(event)

class LeftPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(820)
        self.setStyleSheet(f"background-color: {NEUMORPH_BG_COLOR};")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(28)

        # --- Top 2 Rows of Buttons ---
        row1 = QHBoxLayout()
        for label in ["Reset", "Save Problem", "Delete Problem"]:
            btn = self.create_neumorphic_button(label)
            btn.setMinimumWidth(CONTROL_BTN_WIDTH)
            row1.addWidget(btn)
        main_layout.addLayout(row1)

        # Reduce the space between row1 and row2 by 20%
        # If the default spacing is 28 (from main_layout.setSpacing(28)), use 22
        main_layout.addSpacing(-6)  # 28 * 0.2 = 5.6, so reduce by about 6px

        row2 = QHBoxLayout()
        for label in ["Query", "Next Match", "Previous Match"]:
            btn = self.create_neumorphic_button(label)
            btn.setMinimumWidth(CONTROL_BTN_WIDTH)
            if label == "Query":
                self.query_button = btn
            row2.addWidget(btn)
        main_layout.addLayout(row2)

        # --- Inputs Row ---
        input_row = QHBoxLayout()
        self.problem_id_entry = self.create_neumorphic_entry()
        self.search_text_entry = self.create_neumorphic_entry()
        self.answer_entry = self.create_neumorphic_entry()
        
        # Set fixed widths for each entry field
        self.problem_id_entry.setFixedWidth(120)  # Short width for Problem ID
        self.search_text_entry.setFixedWidth(280)  # Medium width for Search Text
        self.answer_entry.setFixedWidth(320)  # Longer width for Answer
        
        # Create labels and entries with their respective widths
        labels = ["Prob ID", "Search Text", "Answer"]
        entries = [self.problem_id_entry, self.search_text_entry, self.answer_entry]
        
        for label, entry in zip(labels, entries):
            col = QVBoxLayout()
            col.setSpacing(0)  # Remove spacing between label and entry
            lbl = QLabel(label)
            lbl.setFont(QFont(FONT_FAMILY, ENTRY_LABEL_FONT_SIZE, QFont.Bold))
            lbl.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding-bottom: 4px;")
            col.addWidget(lbl)
            col.addWidget(entry)
            input_row.addLayout(col)
        main_layout.addLayout(input_row)

        # --- SAT Problem Types ---
        sat_label = QLabel("SAT Problem Types")
        sat_label.setFont(QFont(FONT_FAMILY, SECTION_LABEL_FONT_SIZE, QFont.Bold))
        sat_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding-top: 10px;")
        main_layout.addWidget(sat_label)
        sat_types = QHBoxLayout()
        self.sat_type_panel = SatTypePanelQt()
        for t, cb in self.sat_type_panel.checkboxes.items():
            cb.setFont(QFont(FONT_FAMILY, SAT_TYPE_FONT_SIZE, QFont.Bold))
            cb.setStyleSheet(f"""
                QCheckBox {{
                    background: transparent;
                    color: {SAT_TYPE_FONT_COLOR};
                    padding: 8px 18px;
                    border-radius: 12px;
                }}
                QCheckBox::indicator {{ width: 22px; height: 22px; }}
            """)
            sat_types.addWidget(cb)
        main_layout.addLayout(sat_types)

        # --- Math Domains ---
        domains_label = QLabel("Math Domains")
        domains_label.setFont(QFont(FONT_FAMILY, SECTION_LABEL_FONT_SIZE, QFont.Bold))
        domains_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding-top: 10px;")
        main_layout.addWidget(domains_label)

        # Scrollable domain grid with neumorphic background
        domain_scroll = NeumorphicScrollArea()
        domain_scroll.setWidgetResizable(True)
        domain_content = QWidget()
        domain_layout = QGridLayout(domain_content)
        domain_layout.setSpacing(18)
        self.category_panel = CategoryPanelQt()
        for idx, cat in enumerate(self.category_panel.categories):
            btn = self.create_neumorphic_button(cat["name"], font_size=DOMAIN_BTN_FONT_SIZE)
            btn.setCheckable(True)
            btn.setMinimumWidth(220)
            btn.setMinimumHeight(48)
            btn.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
            btn.clicked.connect(lambda checked, cid=cat["category_id"]: self.category_panel.toggle_category(cid))
            domain_layout.addWidget(btn, idx // 2, idx % 2)
            self.category_panel.buttons[cat["category_id"]] = btn
        domain_content.setLayout(domain_layout)
        domain_scroll.setWidget(domain_content)
        main_layout.addWidget(domain_scroll)

        # --- Notes ---
        notes_label = QLabel("Notes")
        notes_label.setFont(QFont(FONT_FAMILY, SECTION_LABEL_FONT_SIZE, QFont.Bold))
        notes_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding-top: 10px;")
        main_layout.addWidget(notes_label)
        self.notes_text = NeumorphicTextEdit()
        main_layout.addWidget(self.notes_text)

    def create_neumorphic_button(self, text, parent=None, font_size=BUTTON_FONT_SIZE):
        return NeumorphicButton(
            text,
            parent=parent,
            radius=BUTTON_BORDER_RADIUS,
            bg_color=BUTTON_BG_COLOR,
            shadow_dark=QColor(NEUMORPH_SHADOW_DARK),
            shadow_light=QColor(NEUMORPH_SHADOW_LIGHT),
            font_family=FONT_FAMILY,
            font_size=font_size,
            font_color=BUTTON_FONT_COLOR
        )

    def create_neumorphic_entry(self):
        return NeumorphicEntry(
            radius=ENTRY_BORDER_RADIUS,
            bg_color=ENTRY_BG_COLOR,
            shadow_dark=QColor(NEUMORPH_SHADOW_DARK),
            shadow_light=QColor(NEUMORPH_SHADOW_LIGHT),
            font_family=FONT_FAMILY,
            font_size=ENTRY_FONT_SIZE,
            font_color=ENTRY_FONT_COLOR
        )

    def get_problem_id(self):
        return self.problem_id_entry.text()

    def set_problem_id(self, value):
        self.problem_id_entry.setText(value)

    def get_answer(self):
        return self.answer_entry.text()

    def set_answer(self, value):
        self.answer_entry.setText(value)

    def get_search_text(self):
        return self.search_text_entry.text()

    def set_search_text(self, value):
        self.search_text_entry.setText(value)

    def get_notes(self):
        return self.notes_text.toPlainText()

    def set_notes(self, text):
        self.notes_text.setPlainText(text)

    def on_query_clicked(self):
        text = self.get_search_text()
        QMessageBox.information(self, "Query", f"Search text: {text}") 