"""
Simplified left panel for the Simplified Math Editor (PyQt5).

This refactored version moves ALL query inputs into the QueryInputsPanel,
leaving only the control buttons in the left panel.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QSizePolicy
)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from ui_qt.query_inputs_panel import QueryInputsPanel
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import (
    FONT_FAMILY, CONTROL_BTN_FONT_SIZE, WINDOW_BG_COLOR, 
    BUTTON_BORDER_RADIUS, BUTTON_BG_COLOR, BUTTON_FONT_COLOR, CONTROL_BTN_WIDTH, 
    PADDING, SPACING, BUTTON_TEXT_PADDING
)
from ui_qt.query_panel import QueryPanel

class LeftPanel(QWidget):
    def __init__(self, parent=None, laptop_mode=False):
        super().__init__(parent)
        print(f"[DEBUG] LeftPanel: Initializing with laptop_mode={laptop_mode}")
        
        # Set panel width based on mode
        if laptop_mode:
            self.setFixedWidth(600)
        else:
            self.setFixedWidth(780)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        
        self.setStyleSheet(f"background-color: {WINDOW_BG_COLOR};")
        
        # Store laptop mode for potential future use
        self.laptop_mode = laptop_mode
        
        # Ensure UI is initialized and buttons are created
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components"""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        main_layout.setSpacing(0)  # Minimize gap between top row and query controls

        # --- Top Row: Problem Browser, Save Problem, Preview ---
        self._create_top_row(main_layout)
        main_layout.addSpacing(4)  # Reduce space between top row and query controls
        # --- QueryPanel (contains query controls and inputs) ---
        self.query_panel = QueryPanel(laptop_mode=self.laptop_mode)
        main_layout.addWidget(self.query_panel)
        main_layout.addStretch(1)
        # Wire up problem_display_panel for set panel add-to-set button
        parent_widget = self.parent()
        if parent_widget is not None and hasattr(parent_widget, 'problem_display_panel'):
            self.query_panel.problem_display_panel = parent_widget.problem_display_panel

    def _create_top_row(self, main_layout):
        """Create the top row with Problem Browser 2, Save Problem, and Preview buttons"""
        top_row = QHBoxLayout()
        self.problem_browser2_button = self.create_neumorphic_button("Problem Browser")
        self.save_problem_button = self.create_neumorphic_button("Save Problem")
        self.preview_button = self.create_neumorphic_button("Preview")
        
        # Override default minimum width and size buttons to content with padding
        buttons = [self.problem_browser2_button, self.save_problem_button, self.preview_button]
        for btn in buttons:
            btn.setMinimumWidth(0)  # Remove minimum width constraint
            # Calculate appropriate width based on text + padding
            fm = btn.fontMetrics()
            text_width = fm.horizontalAdvance(btn.text()) if hasattr(fm, 'horizontalAdvance') else fm.width(btn.text())
            btn.setFixedWidth(text_width + (BUTTON_TEXT_PADDING * 2))  # Padding on each side
        
        top_row.addWidget(self.problem_browser2_button)
        top_row.addStretch(1)
        top_row.addWidget(self.save_problem_button)
        top_row.addWidget(self.preview_button)
        main_layout.addLayout(top_row)

    def create_neumorphic_button(self, text, parent=None):
        """Create a neumorphic button with standard styling"""
        print(f"-------------CONTROL_BTN_FONT_SIZE={CONTROL_BTN_FONT_SIZE}")
        return NeumorphicButton(
            text,
            parent=parent,
            font_size=CONTROL_BTN_FONT_SIZE
        )

    # --- Proxy methods to QueryPanel ---
    def get_problem_id(self):
        return self.query_panel.get_problem_id()

    def set_problem_id(self, value):
        self.query_panel.set_problem_id(value)

    def get_answer(self):
        return self.query_panel.get_answer()

    def set_answer(self, value):
        self.query_panel.set_answer(value)

    def get_search_text(self):
        return self.query_panel.get_search_text()

    def set_search_text(self, value):
        self.query_panel.set_search_text(value)

    def get_notes(self):
        return self.query_panel.get_notes()

    def set_notes(self, text):
        self.query_panel.set_notes(text)

    def get_earmark(self):
        return self.query_panel.get_earmark()

    def set_earmark(self, value):
        self.query_panel.set_earmark(value)

    def get_selected_type_ids(self):
        return self.query_panel.get_selected_type_ids()

    def set_selected_type_ids(self, type_ids):
        self.query_panel.set_selected_type_ids(type_ids)

    def get_selected_categories(self):
        return self.query_panel.get_selected_categories()

    @property
    def category_panel(self):
        return self.query_panel.category_panel

    @property
    def problem_type_panel(self):
        return self.query_panel.problem_type_panel

    @property 
    def earmark_checkbox(self):
        return self.query_panel.earmark_checkbox

    @property
    def notes_text(self):
        return self.query_panel.notes_text
    
    @property
    def problem_id_entry(self):
        return self.query_panel.problem_id_entry
    
    @property
    def search_text_entry(self):
        return self.query_panel.search_text_entry
    
    @property
    def answer_entry(self):
        return self.query_panel.answer_entry

    def reset_fields(self):
        self.query_panel.reset_fields()

    def build_full_query_criteria(self):
        return self.query_panel.build_full_query_criteria()

    def apply_full_query_criteria(self, criteria):
        self.query_panel.apply_full_query_criteria(criteria)

    def validate_inputs(self):
        return self.query_panel.validate_inputs()

    def has_any_input(self):
        return self.query_panel.has_any_input()

    def get_search_mode(self):
        return self.query_panel.get_search_mode()

    def clear_all_inputs(self):
        self.reset_fields()

    def get_input_summary(self):
        return self.query_panel.get_input_summary()

    # --- Legacy compatibility methods ---
    def on_query_clicked(self):
        """Legacy method for query button click handling"""
        from PyQt5.QtWidgets import QMessageBox
        text = self.get_search_text()
        QMessageBox.information(self, "Query", f"Search text: {text}")