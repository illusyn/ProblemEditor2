from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QMessageBox, QLabel, QListWidget, QListWidgetItem
from db.problem_set_db import ProblemSetDB
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import BUTTON_FONT_SIZE, BUTTON_MIN_HEIGHT, BUTTON_MIN_WIDTH, FONT_FAMILY, SECTION_LABEL_FONT_SIZE, NEUMORPH_TEXT_COLOR
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

class SetEditorPanelQt(QWidget):
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
        self.name_edit.setPlaceholderText("New set name")
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

        # --- Right column: scrollable set selector ---
        self.selector_scroll = QScrollArea()
        self.selector_scroll.setWidgetResizable(True)
        self.selector_widget = QWidget()
        self.selector_layout = QVBoxLayout(self.selector_widget)
        self.selector_widget.setLayout(self.selector_layout)
        # QListWidget for set selection
        self.set_list = QListWidget()
        self.set_list.setSelectionMode(QListWidget.SingleSelection)
        self.selector_layout.addWidget(self.set_list)
        self.selector_scroll.setWidget(self.selector_widget)
        main_layout.addWidget(self.selector_scroll, stretch=1)
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
        self.set_list.clear()
        db = ProblemSetDB()
        sets = db.get_all_sets()
        db.close()
        if not sets:
            item = QListWidgetItem("No sets defined.")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.set_list.addItem(item)
            return
        for set_id, name, *_ in sets:
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, set_id)
            self.set_list.addItem(item)

    def get_selected_set_id(self):
        selected_items = self.set_list.selectedItems()
        if selected_items:
            return selected_items[0].data(Qt.UserRole)
        return None

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
        if not selected_problems or not selected_set_id:
            QMessageBox.warning(self, "Add to Set", "Please select a problem and a set.")
            return
        from db.problem_set_db import ProblemSetDB
        db = ProblemSetDB()
        added = 0
        already = 0
        for prob in selected_problems:
            pid = prob.get('problem_id')
            result = db.add_problem_to_set(selected_set_id, pid)
            if result:
                added += 1
            else:
                already += 1
        QMessageBox.information(self, "Add to Set", f"Added {added} problem(s) to set. Already present: {already}.")
        db.close() 