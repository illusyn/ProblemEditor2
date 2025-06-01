from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from PyQt5.QtCore import pyqtSignal
from ui_qt.query_inputs_panel import QueryInputsPanel
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import CONTROL_BTN_FONT_SIZE, CONTROL_BTN_WIDTH, SPACING, PADDING, WINDOW_BG_COLOR
from db.math_db import MathProblemDB
from ui_qt.problem_set_panel import ProblemSetPanel

class QueryPanel(QWidget):
    query_executed = pyqtSignal(list)  # Emits a list of problems
    reset_clicked = pyqtSignal()       # Emits when reset is clicked
    query_clicked = pyqtSignal()       # Emits when Query button is clicked
    def __init__(self, parent=None, laptop_mode=False):
        super().__init__(parent)
        self.laptop_mode = laptop_mode
        self.setStyleSheet(f"background-color: {WINDOW_BG_COLOR};")
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        layout.setSpacing(SPACING)

        # --- Query Controls: 2-row layout ---
        self._create_query_controls(layout)

        # --- Query Inputs Panel (contains ALL input fields) ---
        self.query_inputs_panel = QueryInputsPanel(laptop_mode=self.laptop_mode)
        layout.addWidget(self.query_inputs_panel)

        # Debug prints for child size hints
        print("[DEBUG] QueryInputsPanel minimumSizeHint:", self.query_inputs_panel.minimumSizeHint())
        print("[DEBUG] QueryInputsPanel sizeHint:", self.query_inputs_panel.sizeHint())

        # Set a maximum height for QueryPanel to prevent huge minimum size
        # self.setMaximumHeight(900)

        # Connect query button to emit signal (placeholder logic)
        self.query_button.clicked.connect(self.query_clicked.emit)
        self.reset_button.clicked.connect(self._on_reset_clicked)

    def _create_query_controls(self, main_layout):
        query_grid = QGridLayout()
        query_grid.setSpacing(8)

        self.browse_all_button = self.create_neumorphic_button("Browse All")
        self.browse_all_button.setMinimumWidth(CONTROL_BTN_WIDTH)

        self.reset_button = self.create_neumorphic_button("Reset")
        self.reset_button.setMinimumWidth(CONTROL_BTN_WIDTH)

        self.preview_button = self.create_neumorphic_button("Preview")
        self.preview_button.setMinimumWidth(CONTROL_BTN_WIDTH)

        self.query_button = self.create_neumorphic_button("Query")
        self.query_button.setMinimumWidth(CONTROL_BTN_WIDTH)

        self.next_match_button = self.create_neumorphic_button("Next Match")
        self.next_match_button.setMinimumWidth(CONTROL_BTN_WIDTH)

        self.prev_match_button = self.create_neumorphic_button("Previous Match")
        self.prev_match_button.setMinimumWidth(CONTROL_BTN_WIDTH)

        buttons = [
            self.browse_all_button, self.reset_button, self.preview_button,
            self.query_button, self.next_match_button, self.prev_match_button
        ]
        for i, btn in enumerate(buttons):
            query_grid.addWidget(btn, i // 3, i % 3)
        main_layout.addLayout(query_grid)

    def create_neumorphic_button(self, text, parent=None):
        return NeumorphicButton(
            text,
            parent=parent,
            font_size=CONTROL_BTN_FONT_SIZE
        )

    def _on_query_clicked(self):
        db = MathProblemDB()
        criteria = self.query_inputs_panel.build_query_criteria()
        # Get selected category ID if any
        selected_categories = self.query_inputs_panel.get_selected_categories()
        category_id = None
        if selected_categories:
            # Use the first selected category (single selection)
            category_id = selected_categories[0]['category_id']
        all_problems = db.get_problems_list(category_id=category_id, limit=1000)[1]
        db.close()
        problem_id = criteria.get('problem_id', '').strip()
        earmark = criteria.get('earmark', False)
        filtered = all_problems

        if problem_id:
            filtered = [p for p in filtered if str(p.get('problem_id', '')) == problem_id]
        if earmark:
            filtered = [p for p in filtered if p.get('earmark', 0)]
        selected_type_ids = self.query_inputs_panel.get_selected_type_ids()
        if selected_type_ids:
            filtered = [p for p in filtered if any(t['type_id'] in selected_type_ids for t in p.get('types', []))]
        self.query_executed.emit(filtered)

    def _on_reset_clicked(self):
        self.query_inputs_panel.reset_all_inputs()
        self.reset_clicked.emit()

    # Proxy methods to QueryInputsPanel for external access
    def get_problem_id(self):
        return self.query_inputs_panel.get_problem_id()
    def set_problem_id(self, value):
        self.query_inputs_panel.set_problem_id(value)
    def get_answer(self):
        return self.query_inputs_panel.get_answer()
    def set_answer(self, value):
        self.query_inputs_panel.set_answer(value)
    def get_search_text(self):
        return self.query_inputs_panel.get_search_text()
    def set_search_text(self, value):
        self.query_inputs_panel.set_search_text(value)
    def get_notes(self):
        return self.query_inputs_panel.get_notes()
    def set_notes(self, text):
        self.query_inputs_panel.set_notes(text)
    def get_earmark(self):
        return self.query_inputs_panel.get_earmark()
    def set_earmark(self, value):
        self.query_inputs_panel.set_earmark(value)
    def get_selected_type_ids(self):
        return self.query_inputs_panel.get_selected_type_ids()
    def set_selected_type_ids(self, type_ids):
        self.query_inputs_panel.set_selected_type_ids(type_ids)
    def get_selected_categories(self):
        return self.query_inputs_panel.get_selected_categories()
    def reset_fields(self):
        self.query_inputs_panel.reset_all_inputs()
    def build_full_query_criteria(self):
        return self.query_inputs_panel.build_query_criteria()
    def apply_full_query_criteria(self, criteria):
        self.query_inputs_panel.apply_query_criteria(criteria)
    def validate_inputs(self):
        return self.query_inputs_panel.validate_inputs()
    def has_any_input(self):
        return self.query_inputs_panel.has_any_input()
    def get_search_mode(self):
        return self.query_inputs_panel.get_search_mode()
    def clear_all_inputs(self):
        self.reset_fields()
    def get_input_summary(self):
        return self.query_inputs_panel.get_input_summary()
    @property
    def category_panel(self):
        return self.query_inputs_panel.category_panel
    @property
    def problem_type_panel(self):
        return self.query_inputs_panel.problem_type_panel
    @property
    def earmark_checkbox(self):
        return self.query_inputs_panel.earmark_checkbox
    @property
    def notes_text(self):
        return self.query_inputs_panel.notes_text
    @property
    def problem_id_entry(self):
        return self.query_inputs_panel.problem_id_entry
    @property
    def search_text_entry(self):
        return self.query_inputs_panel.search_text_entry
    @property
    def answer_entry(self):
        return self.query_inputs_panel.answer_entry 