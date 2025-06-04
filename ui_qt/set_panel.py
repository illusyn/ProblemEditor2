from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel, QLineEdit, QPushButton, QMessageBox
from db.problem_set_db import ProblemSetDB

class SetPanelQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        print("[DEBUG] SetPanelQt created:", self)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.checkboxes = {}
        print("[DEBUG] SetPanelQt about to call refresh_sets()")
        self.refresh_sets()
        print("[DEBUG] SetPanelQt finished calling refresh_sets()")

        # --- Add Set Creation UI ---
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("New set name")
        self.create_btn = QPushButton("Create Set")
        self.create_btn.clicked.connect(self.create_set)
        self.layout.addWidget(self.name_edit)
        self.layout.addWidget(self.create_btn)

        # --- Add Delete Set Button ---
        self.delete_btn = QPushButton("Delete Selected Set(s)")
        self.delete_btn.clicked.connect(self.delete_selected_sets)
        self.layout.addWidget(self.delete_btn)

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
        # Remove old checkboxes
        for cb in self.checkboxes.values():
            self.layout.removeWidget(cb)
            cb.deleteLater()
        self.checkboxes.clear()
        # Fetch sets
        db = ProblemSetDB()
        sets = db.get_all_sets()
        db.close()
        print("[DEBUG] refresh_sets: sets from DB:", sets)
        if not sets:
            label = QLabel("No sets defined.")
            self.layout.addWidget(label)
            return
        for set_id, name, *_ in sets:
            cb = QCheckBox(name)
            print(f"[DEBUG] Creating checkbox for set_id={set_id}, name={name}")
            self.layout.addWidget(cb)
            self.checkboxes[set_id] = cb

    def get_selected_set_ids(self):
        selected = [set_id for set_id, cb in self.checkboxes.items() if cb.isChecked()]
        print("==============>[DEBUG] SetPanelQt.get_selected_set_ids called on:", self, "Selected:", selected)
        return selected

    def set_selected_set_ids(self, set_ids):
        for set_id, cb in self.checkboxes.items():
            cb.setChecked(set_id in set_ids)

    def delete_selected_sets(self):
        selected_ids = self.get_selected_set_ids()
        if not selected_ids:
            QMessageBox.warning(self, "Delete Set", "No set selected for deletion.")
            return
        reply = QMessageBox.question(
            self, "Delete Set(s)",
            f"Are you sure you want to delete the selected set(s)? This cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        db = ProblemSetDB()
        for set_id in selected_ids:
            db.delete_set(set_id)
        db.close()
        self.refresh_sets()

    def set_get_selected_problem_ids_callback(self, callback):
        self._get_selected_problem_ids_callback = callback

    def add_selected_problems_to_sets(self):
        print("[DEBUG] add_selected_problems_to_sets called on:", self)
        if self._get_selected_problem_ids_callback is None:
            QMessageBox.warning(self, "Add to Set", "Cannot access selected problems (no callback set)")
            return
        problem_ids = self._get_selected_problem_ids_callback()
        if not problem_ids:
            QMessageBox.warning(self, "Add to Set", "No problems selected.")
            return
        set_ids = self.get_selected_set_ids()
        if not set_ids:
            QMessageBox.warning(self, "Add to Set", "No sets selected.")
            return
        # Add problems to sets
        db = ProblemSetDB()
        added = 0
        already = 0
        for set_id in set_ids:
            for pid in problem_ids:
                result = db.add_problem_to_set(set_id, pid)
                if result:
                    added += 1
                else:
                    already += 1
        QMessageBox.information(self, "Add to Set", f"Added {added} problems to {len(set_ids)} set(s). Already present: {already}.")
        db.close() 