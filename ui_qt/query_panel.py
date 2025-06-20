# query_panel.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QSizePolicy
from PyQt5.QtCore import pyqtSignal
from ui_qt.query_inputs_panel import QueryInputsPanel
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import CONTROL_BTN_FONT_SIZE, CONTROL_BTN_WIDTH, SPACING, PADDING, WINDOW_BG_COLOR, BUTTON_TEXT_PADDING
from ui_qt.edit_selected_problems_panel import EditSelectedProblemsPanel
from db.math_db import MathProblemDB

class QueryPanel(QWidget):
    query_executed = pyqtSignal(list)  # Emits a list of problems
    reset_clicked = pyqtSignal()       # Emits when reset is clicked
    query_clicked = pyqtSignal()       # Emits when Query button is clicked
    apply_attributes_to_selected = pyqtSignal(dict)  # Emits attributes to apply
    clear_attributes_from_selected = pyqtSignal(dict)  # Emits attributes to clear
    def __init__(self, parent=None, laptop_mode=False, show_preview_and_nav_buttons=True, return_button=None):
        super().__init__(parent)
        self.laptop_mode = laptop_mode
        self.show_preview_and_nav_buttons = show_preview_and_nav_buttons
        self.return_button = return_button
        self.setStyleSheet(f"background-color: {WINDOW_BG_COLOR};")
        self.setSizePolicy(self.sizePolicy().horizontalPolicy(), QSizePolicy.Minimum)
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

        # --- Edit Selected Problems Panel ---
        self.edit_selected_panel = EditSelectedProblemsPanel(query_inputs_panel=self.query_inputs_panel)
        layout.addWidget(self.edit_selected_panel)

        # Debug prints for child size hints
        print("[DEBUG] QueryInputsPanel minimumSizeHint:", self.query_inputs_panel.minimumSizeHint())
        print("[DEBUG] QueryInputsPanel sizeHint:", self.query_inputs_panel.sizeHint())

        # Set a maximum height for QueryPanel to prevent huge minimum size
        # self.setMaximumHeight(900)

        # Connect query button to emit signal (placeholder logic)
        self.query_button.clicked.connect(self.query_clicked.emit)
        self.reset_button.clicked.connect(self._on_reset_clicked)
        
        # Connect edit panel signals
        self.edit_selected_panel.apply_attributes.connect(self.apply_attributes_to_selected.emit)
        self.edit_selected_panel.clear_attributes.connect(self.clear_attributes_from_selected.emit)

    def _create_query_controls(self, main_layout):
        query_grid = QGridLayout()
        query_grid.setSpacing(8)

        self.reset_button = self.create_neumorphic_button("Reset")
        self.query_button = self.create_neumorphic_button("Query")

        buttons = []
        # Add return button if provided
        if self.return_button:
            buttons.append(self.return_button)
        
        buttons += [self.reset_button, self.query_button]
        # Only add Preview button if not in main editor context
        if self.show_preview_and_nav_buttons:
            self.next_match_button = self.create_neumorphic_button("Next Match")
            self.prev_match_button = self.create_neumorphic_button("Previous Match")
            buttons += [self.next_match_button, self.prev_match_button]
        
        # Override the default minimum width and let buttons size to content with padding
        for btn in buttons:
            btn.setMinimumWidth(0)  # Remove minimum width constraint
            # Calculate appropriate width based on text + padding
            fm = btn.fontMetrics()
            text_width = fm.horizontalAdvance(btn.text()) if hasattr(fm, 'horizontalAdvance') else fm.width(btn.text())
            btn.setFixedWidth(text_width + (BUTTON_TEXT_PADDING * 2))  # Padding on each side
        # Put all buttons on one row
        for i, btn in enumerate(buttons):
            query_grid.addWidget(btn, 0, i)
        main_layout.addLayout(query_grid)

    def create_neumorphic_button(self, text, parent=None):
        print(f"Creating button '{text}' with CONTROL_BTN_FONT_SIZE: {CONTROL_BTN_FONT_SIZE}")
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
        earmark_ids = criteria.get('earmark_ids', [])
        filtered = all_problems

        if problem_id:
            filtered = [p for p in filtered if str(p.get('problem_id', '')) == problem_id]
        if earmark_ids:
            # Filter by new earmarks structure
            filtered = [p for p in filtered if any(e['earmark_id'] in earmark_ids for e in p.get('earmarks', []))]
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
    def get_selected_earmark_ids(self):
        return self.query_inputs_panel.get_selected_earmark_ids()
    def set_selected_earmark_ids(self, earmark_ids):
        self.query_inputs_panel.set_selected_earmark_ids(earmark_ids)
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