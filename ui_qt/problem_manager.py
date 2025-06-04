from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QMessageBox
from PyQt5.QtCore import pyqtSignal, Qt
from ui_qt.query_panel import QueryPanel
from ui_qt.problem_display_panel import ProblemDisplayPanel
from ui_qt.set_panel import SetPanelQt
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import CONTROL_BTN_WIDTH

class ProblemManager(QWidget):
    return_to_editor = pyqtSignal()

    def __init__(self, parent=None, laptop_mode=False):
        super().__init__(parent)
        print("[DEBUG] ProblemManager __init__ called:", self)
        main_layout = QVBoxLayout(self)
        # Main content layout
        content_layout = QHBoxLayout()
        # --- Left side: Return button above query panel ---
        left_vbox = QVBoxLayout()
        self.return_btn = NeumorphicButton("Return to Editor", self)
        self.return_btn.setMinimumWidth(CONTROL_BTN_WIDTH)
        self.return_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.return_btn.clicked.connect(self.return_to_editor)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.return_btn)
        btn_row.addStretch(1)
        left_vbox.addLayout(btn_row)
        self.query_panel = QueryPanel(laptop_mode=laptop_mode, show_preview_and_nav_buttons=False)
        left_vbox.addWidget(self.query_panel)
        # Add SetPanelQt for set selection in Problem Manager
        self.set_panel = SetPanelQt(self)
        left_vbox.addWidget(self.set_panel)
        content_layout.addLayout(left_vbox, stretch=2)  # 40%
        # --- Right side: Problem display + Add-to-Set button ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.problem_display_panel = ProblemDisplayPanel()
        right_layout.addWidget(self.problem_display_panel)
        self.add_to_set_btn = QPushButton("Add Selected Problems to Set(s)")
        self.add_to_set_btn.clicked.connect(self.on_add_to_set_clicked)
        right_layout.addWidget(self.add_to_set_btn)
        content_layout.addWidget(right_panel, stretch=3)
        main_layout.addLayout(content_layout)
        self.query_panel.query_clicked.connect(self.on_query)
        # Connect query results to display panel
        self.query_panel.query_executed.connect(self.problem_display_panel.set_problems)
        # Connect reset to clear the grid
        self.query_panel.reset_clicked.connect(lambda: self.problem_display_panel.set_problems([]))

        # --- Centralized selection state ---
        self.selected_problem_ids = set()
        self.selected_set_ids = set()
        print(f"-------------------->set():{set()}")
        self.problem_display_panel.selection_changed.connect(self.on_problems_selected)
        # If SetPanelQt emits a selection_changed signal, connect it here if needed

    def get_selected_problem_ids(self):
        return [p.get('problem_id') for p in self.problem_display_panel.get_selected_problems()]

    def debug_print_size_hints(self):
        print("[DEBUG] ProblemManager minimumSizeHint:", self.minimumSizeHint())
        print("[DEBUG] ProblemManager sizeHint:", self.sizeHint())
        print("[DEBUG] QueryPanel minimumSizeHint:", self.query_panel.minimumSizeHint())
        print("[DEBUG] QueryPanel sizeHint:", self.query_panel.sizeHint())
        print("[DEBUG] ProblemDisplayPanel minimumSizeHint:", self.problem_display_panel.minimumSizeHint())
        print("[DEBUG] ProblemDisplayPanel sizeHint:", self.problem_display_panel.sizeHint())
        if hasattr(self.query_panel, 'problem_set_panel'):
            print("[DEBUG] ProblemSetPanel minimumSizeHint:", self.query_panel.problem_set_panel.minimumSizeHint())
            print("[DEBUG] ProblemSetPanel sizeHint:", self.query_panel.problem_set_panel.sizeHint())

    def on_query(self):
        criteria = self.query_panel.query_inputs_panel.build_query_criteria()
        selected_set_ids = self.query_panel.query_inputs_panel.get_selected_set_ids()
        selected_set_id = selected_set_ids[0] if selected_set_ids else None
        from db.math_db import MathProblemDB
        db = MathProblemDB()
        # If a set is selected, get only problems in that set; else get all
        if selected_set_id:
            problems = db.list_problems_in_set(selected_set_id)
            # list_problems_in_set may return an error string if it fails
            if not isinstance(problems, list):
                print("[ERROR] list_problems_in_set failed:", problems)
                problems = []
        else:
            success, problems = db.get_problems_list(limit=10000)
            if not success:
                print("[ERROR] get_problems_list failed:", problems)
                problems = []
        db.close()

        # Filter by Problem ID
        problem_id = criteria.get('problem_id', '').strip()
        if problem_id:
            problems = [p for p in problems if str(p.get('problem_id', '')) == problem_id]

        # Filter by Earmark
        earmark = criteria.get('earmark', False)
        if earmark:
            problems = [p for p in problems if p.get('earmark', 0)]

        # Filter by Problem Types
        selected_type_ids = criteria.get('selected_type_ids', [])
        if selected_type_ids:
            problems = [p for p in problems if any(t['type_id'] in selected_type_ids for t in p.get('types', []))]

        # Filter by Categories
        selected_categories = criteria.get('selected_categories', [])
        if selected_categories:
            selected_cat_names = {cat['name'] for cat in selected_categories}
            problems = [p for p in problems if selected_cat_names.issubset({c['name'] for c in p.get('categories', [])})]

        self.problem_display_panel.set_problems(problems)

    def on_add_to_set_clicked(self):
        selected_problems = self.problem_display_panel.get_selected_problems()
        selected_sets = self.set_panel.get_selected_set_ids() if hasattr(self.set_panel, 'get_selected_set_ids') else []
        print("[DEBUG] on_add_to_set_clicked: selected_sets:", selected_sets)
        if not selected_problems or not selected_sets:
            QMessageBox.warning(self, "Add to Set", "Please select problems and sets.")
            return
        from db.problem_set_db import ProblemSetDB
        db = ProblemSetDB()
        added = 0
        already = 0
        for prob in selected_problems:
            pid = prob.get('problem_id')
            for set_id in selected_sets:
                result = db.add_problem_to_set(set_id, pid)
                if result:
                    added += 1
                else:
                    already += 1
        QMessageBox.information(self, "Add to Set", f"Added {added} problems to {len(selected_sets)} set(s). Already present: {already}.")

    def on_problems_selected(self, ids):
        print("[DEBUG] on_problems_selected:", ids)
        self.selected_problem_ids = set(ids)

    def on_sets_selected(self, ids):
        print("[DEBUG] on_sets_selected:", ids)
        self.selected_set_ids = set(ids)
        