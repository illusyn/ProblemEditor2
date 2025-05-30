from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout
from ui_qt.query_inputs_panel import QueryInputsPanel
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import CONTROL_BTN_FONT_SIZE, CONTROL_BTN_WIDTH, SPACING, PADDING, WINDOW_BG_COLOR

class QueryPanel(QWidget):
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
    def get_selected_types(self):
        return self.query_inputs_panel.get_selected_types()
    def set_selected_types(self, type_names):
        self.query_inputs_panel.set_selected_types(type_names)
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