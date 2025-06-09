from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QStyledItemDelegate, QStyle, QGridLayout, QFrame
from db.problem_set_db import ProblemSetDB
from ui_qt.neumorphic_components import NeumorphicButton, NeumorphicEntry, NeumorphicTextEdit
from ui_qt.style_config import BUTTON_MIN_HEIGHT, BUTTON_MIN_WIDTH, FONT_FAMILY, SECTION_LABEL_FONT_SIZE, NEUMORPH_TEXT_COLOR, NEUMORPH_BG_COLOR, NEUMORPH_SHADOW_DARK, NEUMORPH_SHADOW_LIGHT, CATEGORY_BTN_SELECTED_COLOR, NEUMORPH_RADIUS, SET_EDITOR_CONTROL_BUTTON_FONT_SIZE, SET_EDITOR_BUTTON_FONT_SIZE, SET_EDITOR_LABEL_FONT_SIZE, SET_EDITOR_HEAD_FONT_SIZE
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QColor, QBrush, QPen, QPainter
from ui_qt.category_panel import NeumorphicToolButton
from ui_qt.set_selector_grid import SetSelectorGridQt

class NeumorphicTileDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        rect = option.rect
        painter.save()

        bg_color = QColor(NEUMORPH_BG_COLOR)
        shadow_dark = QColor(NEUMORPH_SHADOW_DARK)
        shadow_light = QColor(NEUMORPH_SHADOW_LIGHT)
        selected_color = QColor(CATEGORY_BTN_SELECTED_COLOR)
        radius = NEUMORPH_RADIUS

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        # Draw base background
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), radius, radius)

        # Neumorphic shadow (bottom-right)
        shadow = QColor(shadow_dark)
        shadow.setAlpha(60)
        painter.setBrush(QBrush(shadow))
        painter.drawRoundedRect(rect.adjusted(8, 8, -8, -8), radius, radius)

        # Neumorphic highlight (top-left)
        highlight = QColor(shadow_light)
        highlight.setAlpha(50)
        painter.setBrush(QBrush(highlight))
        painter.drawRoundedRect(rect.adjusted(-2, -2, 2, 2), radius, radius)

        # If selected, overlay the selected color
        if option.state & QStyle.State_Selected:
            painter.setBrush(QBrush(selected_color))
            painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), radius, radius)

        # Draw text
        painter.setPen(QColor(NEUMORPH_TEXT_COLOR))
        font = QFont(FONT_FAMILY, SET_EDITOR_BUTTON_FONT_SIZE, QFont.Bold)
        painter.setFont(font)
        text = index.data(Qt.DisplayRole)
        painter.drawText(rect, Qt.AlignCenter, text)

        painter.restore()

class SetEditorPanelQt(QWidget):
    add_selected_problems_to_set = pyqtSignal(list, object)  # selected_problems, selected_set_id
    def __init__(self, parent=None):
        super().__init__(parent)
        # --- Directly use main layout for all contents (no QFrame border) ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)
        # Title label
        title_label = QLabel("Set Editor")
        title_label.setFont(QFont(FONT_FAMILY, SET_EDITOR_HEAD_FONT_SIZE, QFont.Bold))
        title_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        title_label.setAlignment(Qt.AlignHCenter)
        main_layout.addWidget(title_label, alignment=Qt.AlignHCenter)
        # Main content layout
        main_layout.addLayout(main_layout)

        # --- Top row: set name entry and buttons ---
        top_row = QHBoxLayout()
        name_label = QLabel("Set Name")
        name_label.setFont(QFont(FONT_FAMILY, SET_EDITOR_LABEL_FONT_SIZE, QFont.Bold))
        name_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        top_row.addWidget(name_label)
        self.name_edit = NeumorphicEntry()
        self.name_edit.setFixedWidth(256)
        entry_font = self.name_edit.font()
        entry_font.setPointSize(SET_EDITOR_LABEL_FONT_SIZE)
        self.name_edit.setFont(entry_font)
        top_row.addWidget(self.name_edit)
        self.create_btn = NeumorphicButton("Create Set")
        self.create_btn.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.create_btn.setMaximumHeight(BUTTON_MIN_HEIGHT)
        self.create_btn.setMinimumWidth(140)
        self.create_btn.setMaximumWidth(180)
        font = self.create_btn.font()
        font.setPointSize(SET_EDITOR_CONTROL_BUTTON_FONT_SIZE)
        self.create_btn.setFont(font)
        self.create_btn.clicked.connect(self.create_set)
        top_row.addWidget(self.create_btn)
        self.add_to_set_btn = NeumorphicButton("Add Problems to Set")
        self.add_to_set_btn.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.add_to_set_btn.setMaximumHeight(BUTTON_MIN_HEIGHT)
        self.add_to_set_btn.setMinimumWidth(180)
        self.add_to_set_btn.setMaximumWidth(220)
        font = self.add_to_set_btn.font()
        font.setPointSize(SET_EDITOR_CONTROL_BUTTON_FONT_SIZE)
        self.add_to_set_btn.setFont(font)
        self.add_to_set_btn.clicked.connect(self.on_add_selected_problem_to_set)
        top_row.addWidget(self.add_to_set_btn)
        self.delete_btn = NeumorphicButton("Delete Selected Set")
        self.delete_btn.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.delete_btn.setMaximumHeight(BUTTON_MIN_HEIGHT)
        self.delete_btn.setMinimumWidth(180)
        self.delete_btn.setMaximumWidth(220)
        font = self.delete_btn.font()
        font.setPointSize(SET_EDITOR_CONTROL_BUTTON_FONT_SIZE)
        self.delete_btn.setFont(font)
        self.delete_btn.clicked.connect(self.delete_selected_set)
        top_row.addWidget(self.delete_btn)
        top_row.addStretch(1)
        main_layout.addLayout(top_row)

        # --- Set grid: full width below top row ---
        self.set_selector_grid = SetSelectorGridQt()
        main_layout.addWidget(self.set_selector_grid, stretch=1)
        # Wire up selection logic
        def on_set_selected(set_id):
            self.selected_set_id = set_id
        self.set_selector_grid.set_selected.connect(on_set_selected)

    def create_set(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Create Set", "Set name cannot be empty.")
            return
        db = ProblemSetDB()
        try:
            db.cur.execute("INSERT INTO problem_sets (name) VALUES (?)", (name,))
            db.conn.commit()
            self.name_edit.clear()
            self.refresh_sets()
        except Exception as e:
            QMessageBox.warning(self, "Create Set", f"Could not create set: {e}")
        db.close()

    def refresh_sets(self):
        self.set_selector_grid.refresh_sets()

    def delete_selected_set(self):
        selected_id = self.get_selected_set_id()
        if not selected_id:
            QMessageBox.warning(self, "Delete Set", "No set selected for deletion.")
            return
        reply = QMessageBox.question(
            self, "Delete Set",
            f"Are you sure you want to delete the selected set? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        db = ProblemSetDB()
        db.delete_set(selected_id)
        db.close()
        self.refresh_sets()

    def on_add_selected_problem_to_set(self):
        parent = self.parent()
        if parent and hasattr(parent, 'problem_display_panel'):
            selected_problems = parent.problem_display_panel.get_selected_problems()
        else:
            selected_problems = []
        selected_set_id = self.get_selected_set_id()
        print("[DEBUG] on_add_selected_problem_to_set: selected_set_id:", selected_set_id)
        self.add_selected_problems_to_set.emit(selected_problems, selected_set_id)

    def get_selected_set_id(self):
        return self.set_selector_grid.get_selected_set_id() 