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