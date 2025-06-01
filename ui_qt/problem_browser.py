from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QHBoxLayout, QCheckBox, QInputDialog, QMessageBox, QDialog, QLabel, QDialogButtonBox, QFormLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from db.math_db import MathProblemDB
from ui_qt.neumorphic_components import NeumorphicEntry, NeumorphicButton
from ui_qt.style_config import FONT_FAMILY, SECTION_LABEL_FONT_SIZE, NEUMORPH_TEXT_COLOR, LABEL_FONT_SIZE
from PyQt5.QtGui import QFont
from ui_qt.category_panel import CategoryPanelQt

class ProblemBrowser(QWidget):
    def __init__(self, db_path=None, parent=None):
        super().__init__(parent)
        self.db = MathProblemDB(db_path)
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout(self)
        # --- Left Side: Problem Set Fields Panel + Category Panel ---
        left_side = QVBoxLayout()
        # Problem Set Panel
        set_panel = QGroupBox("Problem Set")
        font = QFont(FONT_FAMILY, SECTION_LABEL_FONT_SIZE, QFont.Bold)
        set_panel.setFont(font)
        set_panel.setStyleSheet(f"QGroupBox {{ color: {NEUMORPH_TEXT_COLOR}; }}")
        set_form = QFormLayout()
        set_form.setContentsMargins(8, 8, 8, 8)
        set_form.setSpacing(6)
        label_font = QFont(FONT_FAMILY, LABEL_FONT_SIZE, QFont.Bold)
        set_name_label = QLabel("Set Name:")
        set_name_label.setFont(label_font)
        self.set_name_edit = NeumorphicEntry(self)
        set_form.addRow(set_name_label, self.set_name_edit)
        desc_label = QLabel("Description:")
        desc_label.setFont(label_font)
        self.set_desc_edit = NeumorphicEntry(self)
        set_form.addRow(desc_label, self.set_desc_edit)
        self.set_ordered_cb = QCheckBox("Ordered", self)
        self.set_ordered_cb.setFont(label_font)
        set_form.addRow(self.set_ordered_cb)
        # Query Problem Set
        self.query_set_edit = NeumorphicEntry(self)
        self.query_set_edit.setPlaceholderText("Enter set name or ID...")
        self.query_set_btn = NeumorphicButton("Query Problem Set", self)
        self.query_set_btn.clicked.connect(self.query_problem_set)
        query_row = QHBoxLayout()
        query_row.addWidget(self.query_set_edit)
        query_row.addWidget(self.query_set_btn)
        query_row.setSpacing(4)
        query_row.setContentsMargins(0, 0, 0, 0)
        query_row_widget = QWidget()
        query_row_widget.setLayout(query_row)
        set_form.addRow(query_row_widget)
        set_panel.setLayout(set_form)
        left_side.addWidget(set_panel)
        left_side.addSpacing(16)  # Add margin below Problem Set panel
        # Category Panel
        self.category_panel = CategoryPanelQt()
        # self.category_panel.setMaximumHeight(220)  # Remove or comment out to allow expansion
        left_side.addWidget(self.category_panel)
        left_side.addStretch()
        main_layout.addLayout(left_side, stretch=1)
        # --- Problem Table and Controls ---
        right_layout = QVBoxLayout()
        # Create Problem Set Button
        top_row = QHBoxLayout()
        self.create_set_btn = NeumorphicButton("Create Problem Set", self)
        self.create_set_btn.clicked.connect(self.show_create_set_dialog)
        top_row.addWidget(self.create_set_btn)
        top_row.addStretch()
        right_layout.addLayout(top_row)
        # Search bar
        search_layout = QHBoxLayout()
        self.search_bar = NeumorphicEntry(self)
        self.search_bar.setPlaceholderText("Filter by content...")
        self.search_bar.textChanged.connect(self.update_filter)
        search_layout.addWidget(self.search_bar)
        self.refresh_btn = NeumorphicButton("Refresh", self)
        self.refresh_btn.clicked.connect(self.load_problems)
        search_layout.addWidget(self.refresh_btn)
        right_layout.addLayout(search_layout)
        # Table (smaller)
        self.table = QTableWidget(self)
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Content", "Earmark", "Categories"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.MultiSelection)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setMaximumHeight(300)
        right_layout.addWidget(self.table)
        # Batch action button
        self.add_to_set_btn = NeumorphicButton("Add Selected to Set", self)
        right_layout.addWidget(self.add_to_set_btn)
        main_layout.addLayout(right_layout, stretch=2)
        self.setLayout(main_layout)
        self.load_problems()
        # Connect category panel selection to filtering
        for btn in self.category_panel.buttons.values():
            btn.clicked.connect(self.update_filter)

    def load_problems(self):
        self.all_problems = self.db.get_problems_list(limit=1000000)[1]
        for p in self.all_problems:
            p['id'] = p['problem_id']
        self.displayed_problems = self.all_problems
        self.populate_table(self.displayed_problems)

    def update_filter(self, text=None, *args, **kwargs):
        # text: from search bar, or None/bool if called from category panel
        if not isinstance(text, str):
            text = self.search_bar.text()
        text = text.strip().lower()
        selected_cats = {cat["name"] for cat in self.category_panel.get_selected_categories()}
        if not text and not selected_cats:
            self.displayed_problems = self.all_problems
        else:
            filtered = []
            for p in self.all_problems:
                content = p.get("content", "").lower()
                categories = {c["name"] for c in p.get("categories", [])}
                # Text filter
                if text and text not in content and text not in ", ".join(categories):
                    continue
                # Category filter (AND logic)
                if selected_cats and not selected_cats.issubset(categories):
                    continue
                filtered.append(p)
            self.displayed_problems = filtered
        self.populate_table(self.displayed_problems)

    def populate_table(self, problems):
        self.table.setRowCount(len(problems))
        for row, p in enumerate(problems):
            # ID
            id_item = QTableWidgetItem(str(p.get("id", "")))
            id_item.setFlags(id_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, id_item)
            # Content snippet
            content = p.get("content", "")
            snippet = content[:80] + ("..." if len(content) > 80 else "")
            content_item = QTableWidgetItem(snippet)
            content_item.setFlags(content_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, content_item)
            # Earmark (checkbox, read-only)
            earmark = bool(p.get("earmark", 0))
            earmark_widget = QCheckBox()
            earmark_widget.setChecked(earmark)
            earmark_widget.setEnabled(False)
            self.table.setCellWidget(row, 2, earmark_widget)
            # Categories
            categories = ", ".join([c["name"] for c in p.get("categories", [])])
            cat_item = QTableWidgetItem(categories)
            cat_item.setFlags(cat_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 3, cat_item)

    def get_selected_problem_ids(self):
        selected = self.table.selectionModel().selectedRows()
        ids = []
        for idx in selected:
            id_item = self.table.item(idx.row(), 0)
            if id_item:
                ids.append(int(id_item.text()))
        return ids

    def show_create_set_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Create Problem Set")
        form = QFormLayout(dialog)
        name_edit = NeumorphicEntry(dialog)
        desc_edit = NeumorphicEntry(dialog)
        ordered_cb = QCheckBox("Ordered", dialog)
        form.addRow(QLabel("Set Name:"), name_edit)
        form.addRow(QLabel("Description:"), desc_edit)
        form.addRow(ordered_cb)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, dialog)
        form.addWidget(buttons)
        dialog.setLayout(form)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        if dialog.exec_() == QDialog.Accepted:
            name = name_edit.text().strip()
            desc = desc_edit.text().strip()
            is_ordered = 1 if ordered_cb.isChecked() else 0
            if not name:
                QMessageBox.warning(self, "Create Problem Set", "Set name is required.")
                return
            try:
                self.db.create_problem_set(name, desc, is_ordered)
                QMessageBox.information(self, "Create Problem Set", f"Problem set '{name}' created.")
            except Exception as e:
                QMessageBox.critical(self, "Create Problem Set", f"Failed to create set: {e}")

    def query_problem_set(self):
        key = self.query_set_edit.text().strip()
        if not key:
            QMessageBox.warning(self, "Query Problem Set", "Enter a set name or ID.")
            return
        try:
            if key.isdigit():
                set_row = self.db.get_problem_set_by_id(int(key))
            else:
                set_row = self.db.get_problem_set_by_name(key)
            if not set_row:
                QMessageBox.information(self, "Query Problem Set", f"No set found for '{key}'.")
                return
            self.set_name_edit.setText(set_row[1])
            self.set_desc_edit.setText(set_row[2] or "")
            self.set_ordered_cb.setChecked(bool(set_row[3]))
            # Optionally: filter table to show only problems in this set
            problem_ids = [row[0] for row in self.db.get_problems_in_set(set_row[0])]
            problems = []
            for pid in problem_ids:
                success, prob = self.db.get_problem(pid, with_images=False, with_categories=True)
                if success:
                    problems.append(prob)
            self.populate_table(problems)
        except Exception as e:
            QMessageBox.critical(self, "Query Problem Set", f"Failed to query set: {e}") 