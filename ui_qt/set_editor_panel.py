from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QStyledItemDelegate, QStyle, QGridLayout
from db.problem_set_db import ProblemSetDB
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import BUTTON_FONT_SIZE, BUTTON_MIN_HEIGHT, BUTTON_MIN_WIDTH, FONT_FAMILY, SECTION_LABEL_FONT_SIZE, NEUMORPH_TEXT_COLOR, NEUMORPH_BG_COLOR, NEUMORPH_SHADOW_DARK, NEUMORPH_SHADOW_LIGHT, CATEGORY_BTN_SELECTED_COLOR, NEUMORPH_RADIUS
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QColor, QBrush, QPen, QPainter
from ui_qt.category_panel import NeumorphicToolButton

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
        font = QFont(FONT_FAMILY, BUTTON_FONT_SIZE, QFont.Bold)
        painter.setFont(font)
        text = index.data(Qt.DisplayRole)
        painter.drawText(rect, Qt.AlignCenter, text)

        painter.restore()

class SetEditorPanelQt(QWidget):
    add_selected_problems_to_set = pyqtSignal(list, object)  # selected_problems, selected_set_id
    def __init__(self, parent=None):
        super().__init__(parent)
        # self.setStyleSheet("background: #ccffcc;")
        main_layout = QHBoxLayout(self)
        self.setLayout(main_layout)

        # --- Left column: label, entry, buttons ---
        left_col = QVBoxLayout()
        # Set Name label
        name_label = QLabel("Set Name")
        name_label.setFont(QFont(FONT_FAMILY, BUTTON_FONT_SIZE, QFont.Bold))
        name_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        left_col.addWidget(name_label, alignment=Qt.AlignHCenter)
        # Set Name entry
        self.name_edit = QLineEdit()
        # self.name_edit.setPlaceholderText("Enter set name")
        self.name_edit.setFixedWidth(256)
        entry_font = self.name_edit.font()
        entry_font.setPointSize(BUTTON_FONT_SIZE)
        self.name_edit.setFont(entry_font)
        left_col.addWidget(self.name_edit)
        # Button stack (vertical)
        self.create_btn = NeumorphicButton("Create Set")
        self.create_btn.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.create_btn.setMaximumHeight(BUTTON_MIN_HEIGHT)
        self.create_btn.setMinimumWidth(256)
        self.create_btn.setMaximumWidth(256)
        font = self.create_btn.font()
        font.setPointSize(BUTTON_FONT_SIZE)
        self.create_btn.setFont(font)
        self.create_btn.clicked.connect(self.create_set)
        left_col.addWidget(self.create_btn, alignment=Qt.AlignLeft)

        self.add_to_set_btn = NeumorphicButton("Add Problems to Set")
        self.add_to_set_btn.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.add_to_set_btn.setMaximumHeight(BUTTON_MIN_HEIGHT)
        self.add_to_set_btn.setMinimumWidth(256)
        self.add_to_set_btn.setMaximumWidth(256)
        font = self.add_to_set_btn.font()
        font.setPointSize(BUTTON_FONT_SIZE)
        self.add_to_set_btn.setFont(font)
        self.add_to_set_btn.clicked.connect(self.on_add_selected_problem_to_set)
        left_col.addWidget(self.add_to_set_btn, alignment=Qt.AlignLeft)

        self.delete_btn = NeumorphicButton("Delete Selected Set")
        self.delete_btn.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.delete_btn.setMaximumHeight(BUTTON_MIN_HEIGHT)
        self.delete_btn.setMinimumWidth(256)
        self.delete_btn.setMaximumWidth(256)
        font = self.delete_btn.font()
        font.setPointSize(BUTTON_FONT_SIZE)
        self.delete_btn.setFont(font)
        self.delete_btn.clicked.connect(self.delete_selected_set)
        left_col.addWidget(self.delete_btn, alignment=Qt.AlignLeft)
        left_col.addStretch(1)
        main_layout.addLayout(left_col)

        # --- Right column: scrollable neumorphic set selector ---
        self.set_grid_widget = QWidget()
        self.set_grid_layout = QGridLayout(self.set_grid_widget)
        self.set_grid_layout.setSpacing(16)
        self.set_grid_layout.setContentsMargins(0, 0, 0, 0)
        # Wrap grid in a scroll area
        self.set_scroll_area = QScrollArea()
        self.set_scroll_area.setWidgetResizable(True)
        self.set_scroll_area.setWidget(self.set_grid_widget)
        self.set_scroll_area.setStyleSheet('border: none;')
        # Calculate tile/button height (match category panel)
        tile_width = 215
        tile_height = BUTTON_MIN_HEIGHT if 'BUTTON_MIN_HEIGHT' in globals() else 56
        visible_rows = 3
        visible_cols = 3
        spacing = self.set_grid_layout.spacing()
        grid_height = visible_rows * tile_height + (visible_rows - 1) * spacing
        grid_width = visible_cols * tile_width + (visible_cols - 1) * spacing
        self.set_scroll_area.setFixedSize(grid_width + self.set_scroll_area.verticalScrollBar().sizeHint().width(), grid_height)
        main_layout.addWidget(self.set_scroll_area, stretch=1)
        self.set_buttons = {}  # set_id: button
        self.selected_set_id = None
        self.refresh_sets()

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
        # Remove old buttons
        for btn in getattr(self, 'set_buttons', {}).values():
            self.set_grid_layout.removeWidget(btn)
            btn.deleteLater()
        self.set_buttons = {}
        db = ProblemSetDB()
        sets = db.get_all_sets()
        db.close()
        if not sets:
            label = QLabel("No sets defined.")
            self.set_grid_layout.addWidget(label, 0, 0)
            return
        cols = 3
        for idx, (set_id, name, *_) in enumerate(sets):
            row = idx // cols
            col = idx % cols
            btn = NeumorphicToolButton(name, font_size=BUTTON_FONT_SIZE)
            btn.setMinimumWidth(215)
            btn.setMaximumWidth(215)
            btn.setCheckable(True)
            btn.setChecked(self.selected_set_id == set_id)
            btn.clicked.connect(lambda checked, sid=set_id: self.on_set_selected(sid, checked))
            self.set_grid_layout.addWidget(btn, row, col)
            self.set_buttons[set_id] = btn

    def on_set_selected(self, set_id, checked):
        if checked:
            # Uncheck all others
            for sid, btn in self.set_buttons.items():
                if sid != set_id:
                    btn.setChecked(False)
            self.selected_set_id = set_id
        else:
            self.selected_set_id = None

    def get_selected_set_id(self):
        return self.selected_set_id

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