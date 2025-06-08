# problem_manager.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QMessageBox, QLabel, QTextEdit
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from ui_qt.query_panel import QueryPanel
from ui_qt.problem_display_panel import ProblemDisplayPanel
from ui_qt.set_editor_panel import SetEditorPanelQt
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import CONTROL_BTN_WIDTH, FONT_FAMILY, SECTION_LABEL_FONT_SIZE

class ProblemManager(QWidget):
    return_to_editor = pyqtSignal()

    def __init__(self, parent=None, laptop_mode=False):
        super().__init__(parent)
        print("[DEBUG] ProblemManager __init__ called:", self)
        main_layout = QVBoxLayout(self)
        # Main content layout
        content_layout = QHBoxLayout()
        # --- Left side: Return button above query panel ---
        left_panel_widget = QWidget()
        left_vbox = QVBoxLayout(left_panel_widget)
        left_panel_widget.setStyleSheet('background: transparent;')
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
        left_vbox.addWidget(self.query_panel, stretch=1)
        # Remove SetEditorPanelQt and Add-to-Set button from here
        # Add-to-Set logic will be handled in SetEditorPanelQt
        # If using a QWidget for the left panel, set its background to transparent for debugging
        # If not, set the background of the parent widget of left_vbox to transparent
        # Example (if left_panel_widget exists):
        # left_panel_widget.setStyleSheet('background: transparent;')
        content_layout.addWidget(left_panel_widget, stretch=2)  # 40%
        # --- Right side: Problem display only ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        self.problem_display_panel = ProblemDisplayPanel()
        right_layout.addWidget(self.problem_display_panel)
        content_layout.addWidget(right_panel, stretch=3)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
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

    def on_problems_selected(self, ids):
        print("[DEBUG] on_problems_selected:", ids)
        self.selected_problem_ids = set(ids)

    def on_sets_selected(self, ids):
        print("[DEBUG] on_sets_selected:", ids)
        self.selected_set_ids = set(ids)
        