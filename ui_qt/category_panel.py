"""
Category panel for the Simplified Math Editor (PyQt5).
"""

from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton
from PyQt5.QtCore import Qt
from db.problem_database import ProblemDatabase

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
        layout.setSpacing(8)
        for idx, cat in enumerate(self.categories):
            btn = QPushButton(cat["name"])
            btn.setCheckable(True)
            btn.setMinimumWidth(120)
            btn.setMinimumHeight(32)
            btn.clicked.connect(lambda checked, cid=cat["category_id"]: self.toggle_category(cid))
            layout.addWidget(btn, idx // 2, idx % 2)
            self.buttons[cat["category_id"]] = btn

    def toggle_category(self, category_id):
        btn = self.buttons[category_id]
        if btn.isChecked():
            self.selected.add(category_id)
            btn.setStyleSheet("background-color: #cce5ff;")
        else:
            self.selected.discard(category_id)
            btn.setStyleSheet("")

    def get_selected_categories(self):
        # Return list of selected category dicts
        return [cat for cat in self.categories if cat["category_id"] in self.selected] 