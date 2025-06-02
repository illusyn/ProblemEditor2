from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QListWidget, QPushButton, QLineEdit, QTextEdit, QCheckBox, QLabel, QGroupBox, QMessageBox, QInputDialog, QListWidgetItem, QSizePolicy,
    QAbstractItemView
)
from PyQt5.QtCore import Qt
from db.problem_set_db import ProblemSetDB

class ProblemSetPanel(QWidget):
    def __init__(self, parent=None, get_selected_problem_ids_callback=None):
        super().__init__(parent)
        self.setWindowTitle("Problem Set Manager")
        self.db = ProblemSetDB()
        self.get_selected_problem_ids_callback = get_selected_problem_ids_callback
        self._ignore_selection = False  # Guard variable to prevent recursive selection events
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # --- Top buttons ---
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Set")
        self.rename_btn = QPushButton("Rename")
        self.delete_btn = QPushButton("Delete")
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.rename_btn)
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        # --- Main content: sets list and details ---
        content_layout = QHBoxLayout()
        # Left: List of sets
        self.set_list = QListWidget()
        self.set_list.setMinimumWidth(200)
        self.set_list.setMaximumHeight(self.set_list.sizeHintForRow(0) * 3 + 6)  # 3 lines tall
        self.set_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.set_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.set_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        content_layout.addWidget(self.set_list, stretch=1)

        # Right: Set details (no QGroupBox, no label)
        details_layout = QVBoxLayout()
        details_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit()
        details_layout.addWidget(self.name_edit)
        details_layout.addWidget(QLabel("Description:"))
        self.desc_edit = QLineEdit()  # Single-line
        details_layout.addWidget(self.desc_edit)
        details_layout.addStretch(1)
        content_layout.addLayout(details_layout, stretch=2)

        main_layout.addLayout(content_layout, stretch=1)

        # --- Signals (UI only, no DB logic yet) ---
        self.add_btn.clicked.connect(self.on_add_set)
        self.rename_btn.clicked.connect(self.on_rename_set)
        self.delete_btn.clicked.connect(self.on_delete_set)
        self.set_list.currentRowChanged.connect(self.on_set_selected)
        self.name_edit.editingFinished.connect(self.on_save_details)
        self.desc_edit.editingFinished.connect(self.on_save_details)

        # --- Add Selected Problems to Set Button ---
        self.add_problems_btn = QPushButton("Add Selected Problems to Set")
        self.add_problems_btn.clicked.connect(self.on_add_problems_to_set)
        main_layout.addWidget(self.add_problems_btn)

        # Limit the maximum height of the panel
        self.setMaximumHeight(300)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        # Debug prints for size hints
        print("[DEBUG] ProblemSetPanel minimumSizeHint:", self.minimumSizeHint())
        print("[DEBUG] ProblemSetPanel sizeHint:", self.sizeHint())
        print("[DEBUG] set_list minimumSizeHint:", self.set_list.minimumSizeHint())
        print("[DEBUG] set_list sizeHint:", self.set_list.sizeHint())
        print("[DEBUG] desc_edit minimumSizeHint:", self.desc_edit.minimumSizeHint())
        print("[DEBUG] desc_edit sizeHint:", self.desc_edit.sizeHint())

        self.load_sets()

    def load_sets(self):
        self.set_list.clear()
        for set_id, name, description, ordered in self.db.get_all_sets():
            item = QListWidgetItem(name)
            item.setData(Qt.UserRole, set_id)
            item.setToolTip(description or "")
            self.set_list.addItem(item)

    def on_add_set(self):
        print("[DEBUG] on_add_set: called")
        try:
            name = self.name_edit.text().strip()
            print(f"[DEBUG] on_add_set: name={name!r}")
            if not name:
                QMessageBox.warning(self, "Add Set", "Please enter a set name in the Name field.")
                return
            set_id = self.db.add_set(name)
            print(f"[DEBUG] on_add_set: set_id={set_id}")
            self.load_sets()
            print("[DEBUG] on_add_set: after load_sets")
            print(f"[DEBUG] on_add_set: entering selection loop, set_id={set_id}, list count={self.set_list.count()}")
            self._ignore_selection = True
            try:
                for i in range(self.set_list.count()):
                    item = self.set_list.item(i)
                    print(f"[DEBUG] on_add_set: checking item {i}, data={item.data(Qt.UserRole)}")
                    if item.data(Qt.UserRole) == set_id:
                        self.set_list.setCurrentRow(i)
                        print(f"[DEBUG] on_add_set: selected row {i} for set_id={set_id}")
                        break
            finally:
                self._ignore_selection = False
            print("[DEBUG] on_add_set: finished")
        except Exception as e:
            print(f"[ERROR] Exception in on_add_set: {e}")

    def on_rename_set(self):
        row = self.set_list.currentRow()
        if row >= 0:
            item = self.set_list.item(row)
            set_id = item.data(Qt.UserRole)
            new_name = self.name_edit.text().strip()
            if not new_name:
                QMessageBox.warning(self, "Rename Set", "Please enter a new name in the Name field.")
                return
            self.db.rename_set(set_id, new_name)
            self.load_sets()
            # Reselect
            self._ignore_selection = True
            try:
                for i in range(self.set_list.count()):
                    if self.set_list.item(i).data(Qt.UserRole) == set_id:
                        self.set_list.setCurrentRow(i)
                        break
            finally:
                self._ignore_selection = False

    def on_delete_set(self):
        row = self.set_list.currentRow()
        if row >= 0:
            item = self.set_list.item(row)
            set_id = item.data(Qt.UserRole)
            reply = QMessageBox.question(self, "Delete Set", "Are you sure you want to delete this set?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.db.delete_set(set_id)
                self.load_sets()
                self.name_edit.clear()
                self.desc_edit.clear()

    def on_set_selected(self, row):
        if self._ignore_selection:
            print("[DEBUG] on_set_selected: ignoring due to guard")
            return
        print(f"[DEBUG] on_set_selected: row={row}")
        if row >= 0:
            item = self.set_list.item(row)
            print(f"[DEBUG] on_set_selected: item={item}")
            set_id = item.data(Qt.UserRole)
            print(f"[DEBUG] on_set_selected: set_id={set_id}")
            # Fetch details from DB
            sets = [s for s in self.db.get_all_sets() if s[0] == set_id]
            print(f"[DEBUG] on_set_selected: sets={sets}")
            if sets:
                _, name, description, _ = sets[0]
                print(f"[DEBUG] on_set_selected: name={name}, description={description}")
                self.name_edit.setText(name)
                self.desc_edit.setText(description or "")
        else:
            print("[DEBUG] on_set_selected: row < 0, clearing fields")
            self.name_edit.clear()
            self.desc_edit.clear()

    def on_save_details(self):
        row = self.set_list.currentRow()
        if row >= 0:
            item = self.set_list.item(row)
            set_id = item.data(Qt.UserRole)
            name = self.name_edit.text()
            description = self.desc_edit.text()
            self.db.update_set_details(set_id, name, description, False)
            self.load_sets()
            # Reselect
            self._ignore_selection = True
            try:
                for i in range(self.set_list.count()):
                    if self.set_list.item(i).data(Qt.UserRole) == set_id:
                        self.set_list.setCurrentRow(i)
                        break
            finally:
                self._ignore_selection = False

    def on_add_problems_to_set(self):
        row = self.set_list.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Add to Set", "Please select a set first.")
            return
        item = self.set_list.item(row)
        set_id = item.data(Qt.UserRole)
        # Get selected problems from callback
        if not callable(self.get_selected_problem_ids_callback):
            QMessageBox.warning(self, "Add to Set", "Cannot access selected problems (no callback provided).")
            return
        problem_ids = self.get_selected_problem_ids_callback()
        if not problem_ids:
            QMessageBox.information(self, "Add to Set", "No problems selected.")
            return
        added = 0
        already = 0
        for pid in problem_ids:
            success = self.db.add_problem_to_set(set_id, pid)
            if success:
                added += 1
            else:
                already += 1
        QMessageBox.information(self, "Add to Set", f"Added {added} problems to set. {already} were already present.")

    def closeEvent(self, event):
        self.db.close()
        super().closeEvent(event) 