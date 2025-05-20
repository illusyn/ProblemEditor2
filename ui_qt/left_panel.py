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
from ui_qt.style_config import (FONT_FAMILY, FONT_WEIGHT, LABEL_FONT_SIZE, SECTION_LABEL_FONT_SIZE, BUTTON_FONT_SIZE, CONTROL_BTN_FONT_SIZE, ENTRY_FONT_SIZE, NOTES_FONT_SIZE, NEUMORPH_TEXT_COLOR, WINDOW_BG_COLOR, NEUMORPH_BG_COLOR, NEUMORPH_SHADOW_DARK, NEUMORPH_SHADOW_LIGHT, NEUMORPH_GRADIENT_START, NEUMORPH_GRADIENT_END, NEUMORPH_RADIUS, BUTTON_BORDER_RADIUS, BUTTON_BG_COLOR, BUTTON_FONT_COLOR, ENTRY_BORDER_RADIUS, ENTRY_BG_COLOR, ENTRY_FONT_COLOR, NOTES_BG_COLOR, NOTES_FONT_COLOR, NOTES_BORDER_RADIUS, SAT_TYPE_FONT_COLOR, SAT_TYPE_FONT_SIZE, DOMAIN_BTN_FONT_SIZE, CONTROL_BTN_WIDTH, ENTRY_LABEL_FONT_SIZE, PROB_ID_ENTRY_WIDTH, SEARCH_TEXT_ENTRY_WIDTH, ANSWER_ENTRY_WIDTH, SEARCH_TEXT_LABEL_PADDING, ANSWER_LABEL_PADDING, DEFAULT_LABEL_PADDING, ROW_SPACING_REDUCTION, NOTES_FIXED_HEIGHT, PADDING, SPACING, LEFT_PANEL_WIDTH, DOMAIN_GRID_SPACING, DOMAIN_BTN_WIDTH, DOMAIN_BTN_HEIGHT, SECTION_LABEL_PADDING_TOP, BUTTON_MIN_WIDTH, BUTTON_MIN_HEIGHT, ENTRY_MIN_HEIGHT, ENTRY_PADDING_LEFT, TEXTEDIT_PADDING, SHADOW_RECT_ADJUST, SHADOW_OFFSETS, EDITOR_BG_COLOR)

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
        self.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(SHADOW_RECT_ADJUST, SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST)
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
        self.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        self.setStyleSheet(f"background: transparent; border: none; color: {self.font_color}; padding-left: {ENTRY_PADDING_LEFT}px;")
        self.setMinimumHeight(ENTRY_MIN_HEIGHT)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(SHADOW_RECT_ADJUST, SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST)
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
        rect = self.rect().adjusted(SHADOW_RECT_ADJUST, SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST)
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
        self.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        self.setStyleSheet(f"background: transparent; border: none; color: {self.font_color}; padding: {TEXTEDIT_PADDING}px;")
        self.setFixedHeight(NOTES_FIXED_HEIGHT)  # Use centralized height

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect().adjusted(SHADOW_RECT_ADJUST, SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST)
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

class LeftPanel(QWidget):
    def __init__(self, parent=None, laptop_mode=False):
        super().__init__(parent)
        print(f"[DEBUG] LeftPanel: LABEL_FONT_SIZE={LABEL_FONT_SIZE}, BUTTON_FONT_SIZE={BUTTON_FONT_SIZE}, ENTRY_FONT_SIZE={ENTRY_FONT_SIZE}, NOTES_FONT_SIZE={NOTES_FONT_SIZE}")
        if laptop_mode:
            self.setFixedWidth(600)
        else:
            self.setFixedWidth(780)
        self.setStyleSheet(f"background-color: {WINDOW_BG_COLOR};")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        main_layout.setSpacing(SPACING)

        # --- Top 2 Rows of Buttons ---
        row1 = QHBoxLayout()
        for label in ["Reset", "Save Problem", "Preview"]:
            btn = self.create_neumorphic_button(label, font_size=CONTROL_BTN_FONT_SIZE)
            btn.setMinimumWidth(CONTROL_BTN_WIDTH)
            if label == "Save Problem":
                self.save_problem_button = btn
            elif label == "Reset":
                self.reset_button = btn
            elif label == "Preview":
                self.preview_button = btn
            row1.addWidget(btn)
        main_layout.addLayout(row1)

        # Reduce the space between row1 and row2
        main_layout.addSpacing(ROW_SPACING_REDUCTION)

        row2 = QHBoxLayout()
        for label in ["Query", "Next Match", "Previous Match"]:
            btn = self.create_neumorphic_button(label, font_size=CONTROL_BTN_FONT_SIZE)
            btn.setMinimumWidth(CONTROL_BTN_WIDTH)
            if label == "Query":
                self.query_button = btn
            elif label == "Next Match":
                self.next_match_button = btn
            elif label == "Previous Match":
                self.prev_match_button = btn
            row2.addWidget(btn)
        main_layout.addLayout(row2)

        # --- Inputs Row ---
        input_row = QHBoxLayout()
        self.problem_id_entry = self.create_neumorphic_entry()
        self.search_text_entry = self.create_neumorphic_entry()
        self.answer_entry = self.create_neumorphic_entry()
        
        # Set fixed widths for each entry field using centralized values
        self.problem_id_entry.setFixedWidth(PROB_ID_ENTRY_WIDTH)
        self.search_text_entry.setFixedWidth(SEARCH_TEXT_ENTRY_WIDTH)
        self.answer_entry.setFixedWidth(ANSWER_ENTRY_WIDTH)
        
        # Create labels and entries with their respective widths
        labels = ["Prob ID", "Search Text", "Answer"]
        entries = [self.problem_id_entry, self.search_text_entry, self.answer_entry]
        
        for label, entry in zip(labels, entries):
            col = QVBoxLayout()
            col.setSpacing(0)  # Remove spacing between label and entry
            lbl = QLabel(label)
            lbl.setFont(QFont(FONT_FAMILY, ENTRY_LABEL_FONT_SIZE, QFont.Bold))
            # Use centralized padding values
            if label == "Search Text":
                padding = SEARCH_TEXT_LABEL_PADDING
            elif label == "Answer":
                padding = ANSWER_LABEL_PADDING
            else:
                padding = DEFAULT_LABEL_PADDING
            lbl.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; {padding} background: {WINDOW_BG_COLOR};")
            lbl.setAlignment(Qt.AlignCenter)  # Center the label horizontally
            col.addWidget(lbl)
            col.addWidget(entry)
            input_row.addLayout(col)
        main_layout.addLayout(input_row)
        # Remove or minimize vertical space before SAT Problem Types
        main_layout.addSpacing(0)
        # --- SAT Problem Types ---
        sat_label = QLabel("SAT Problem Types")
        sat_label.setFont(QFont(FONT_FAMILY, SECTION_LABEL_FONT_SIZE, QFont.Bold))
        sat_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding-top: 0px; padding-bottom: 0px; margin-top: 0px; margin-bottom: 0px; background: {WINDOW_BG_COLOR};")
        sat_label.setMaximumHeight(18)
        sat_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(sat_label)
        sat_types = QHBoxLayout()
        sat_types.setSpacing(0)
        self.sat_type_panel = SatTypePanelQt()
        for t, cb in self.sat_type_panel.checkboxes.items():
            cb.setFont(QFont(FONT_FAMILY, SAT_TYPE_FONT_SIZE, QFont.Bold))
            cb.setStyleSheet(f"""
                QCheckBox {{
                    background: transparent;
                    color: {SAT_TYPE_FONT_COLOR};
                    padding: 2px 8px;
                    border-radius: 4px;
                    margin-top: 0px; margin-bottom: 0px;
                }}
                QCheckBox::indicator {{ width: 18px; height: 18px; }}
            """)
            cb.setMinimumHeight(28)
            cb.setMaximumHeight(40)
            sat_types.addWidget(cb)
        main_layout.addLayout(sat_types)

        # --- Math Domains ---
        if laptop_mode:
            main_layout.addSpacing(5)  # Minimal spacing for scaled mode
        else:
            main_layout.addSpacing(30)
        domains_label = QLabel("Math Domains")
        domains_label.setFont(QFont(FONT_FAMILY, SECTION_LABEL_FONT_SIZE, QFont.Bold))
        domains_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding-top: 0px; padding-bottom: 0px; margin-top: 0px; margin-bottom: 0px; background: {WINDOW_BG_COLOR};")
        domains_label.setMaximumHeight(18)
        domains_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(domains_label)

        # Use CategoryPanelQt directly
        self.category_panel = CategoryPanelQt()
        main_layout.addWidget(self.category_panel)

        # --- Notes ---
        self.notes_text = None
        if not laptop_mode:
            notes_label = QLabel("Notes")
            notes_label.setFont(QFont(FONT_FAMILY, SECTION_LABEL_FONT_SIZE, QFont.Bold))
            notes_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; {SECTION_LABEL_PADDING_TOP} background: {WINDOW_BG_COLOR};")
            main_layout.addWidget(notes_label)
            self.notes_text = NeumorphicTextEdit(bg_color=EDITOR_BG_COLOR)
            main_layout.addWidget(self.notes_text)

        # Connect Reset button to reset_fields method
        # self.reset_button.clicked.connect(self.reset_fields)

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
        if self.notes_text is not None:
            return self.notes_text.toPlainText()
        return ""

    def set_notes(self, text):
        if self.notes_text is not None:
            self.notes_text.setPlainText(text)

    def on_query_clicked(self):
        text = self.get_search_text()
        QMessageBox.information(self, "Query", f"Search text: {text}")

    def reset_fields(self):
        self.problem_id_entry.setText("")
        self.search_text_entry.setText("")
        self.answer_entry.setText("")
        if self.notes_text is not None:
            self.notes_text.setPlainText("")
        # Uncheck all SAT type checkboxes
        for cb in self.sat_type_panel.checkboxes.values():
            cb.setChecked(False)
        # Unselect all category buttons
        for btn in self.category_panel.buttons.values():
            btn.setChecked(False)
        self.category_panel.selected.clear() 