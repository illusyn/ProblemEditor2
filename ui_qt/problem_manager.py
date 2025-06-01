from PyQt5.QtWidgets import QWidget, QHBoxLayout
from ui_qt.query_panel import QueryPanel
from ui_qt.problem_display_panel import ProblemDisplayPanel
from ui_qt.problem_set_panel import ProblemSetPanel

class ProblemManager(QWidget):
    def __init__(self, parent=None, laptop_mode=False):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.query_panel = QueryPanel(laptop_mode=laptop_mode)
        self.problem_display_panel = ProblemDisplayPanel()
        layout.addWidget(self.query_panel, stretch=2)  # 40%
        layout.addWidget(self.problem_display_panel, stretch=3)  # 60%
        self.query_panel.query_clicked.connect(self.on_query)
        # Add ProblemSetPanel only in ProblemManager
        self.problem_set_panel = ProblemSetPanel(self, get_selected_problem_ids_callback=self.get_selected_problem_ids)
        self.query_panel.layout().addWidget(self.problem_set_panel)
        # Connect query results to display panel
        self.query_panel.query_executed.connect(self.problem_display_panel.set_problems)
        # Connect reset to clear the grid
        self.query_panel.reset_clicked.connect(lambda: self.problem_display_panel.set_problems([]))

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
        selected_set_id = self.query_panel.query_inputs_panel.get_selected_set_id()
        print(f"[DEBUG] selected_set_id={selected_set_id} (type={type(selected_set_id)})")
        from db.math_db import MathProblemDB
        db = MathProblemDB()
        # If a set is selected, get only problems in that set; else get all
        if selected_set_id:
            problems = db.list_problems_in_set(selected_set_id)
            print(f"[DEBUG] Problems returned from list_problems_in_set: {len(problems)}")
        else:
            problems = db.get_problems_list(limit=10000)[1]
            print(f"[DEBUG] Problems returned from get_problems_list: {len(problems)}")
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
        print(f"[DEBUG] ProblemManager on_query called. Displaying {len(problems)} problems.") 