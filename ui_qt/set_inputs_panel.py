from PyQt5.QtWidgets import QWidget, QVBoxLayout, QCheckBox, QLabel
from db.problem_set_db import ProblemSetDB

class SetInputsPanelQt(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        self.checkboxes = {}
        self.refresh_sets()

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
        if not sets:
            label = QLabel("No sets defined.")
            self.layout.addWidget(label)
            return
        for set_id, name, *_ in sets:
            cb = QCheckBox(name)
            self.layout.addWidget(cb)
            self.checkboxes[set_id] = cb

    def get_selected_set_ids(self):
        return [set_id for set_id, cb in self.checkboxes.items() if cb.isChecked()]

    def set_selected_set_ids(self, set_ids):
        for set_id, cb in self.checkboxes.items():
            cb.setChecked(set_id in set_ids) 