# query_inputs_panel.py
"""
Query inputs panel for the Simplified Math Editor (PyQt5).

This module contains ALL query-related input components:
- Basic inputs: Problem ID, Search Text, Answer
- Advanced inputs: Problem types, earmark, categories, notes
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QTextEdit, 
    QLineEdit, QPushButton, QCheckBox, QScrollArea, QSizePolicy, QGroupBox, QComboBox, QFrame, QStackedWidget
)
from PyQt5.QtGui import QFont, QColor, QPainter, QBrush, QLinearGradient
from PyQt5.QtCore import Qt
from ui_qt.category_panel import CategoryPanelQt
from ui_qt.style_config import (
    FONT_FAMILY, FONT_WEIGHT, LABEL_FONT_SIZE, SECTION_LABEL_FONT_SIZE, 
    BUTTON_FONT_SIZE, CONTROL_BTN_FONT_SIZE, ENTRY_FONT_SIZE, NOTES_FONT_SIZE, 
    NEUMORPH_TEXT_COLOR, WINDOW_BG_COLOR, NEUMORPH_BG_COLOR, NEUMORPH_SHADOW_DARK, 
    NEUMORPH_SHADOW_LIGHT, NEUMORPH_GRADIENT_START, NEUMORPH_GRADIENT_END, 
    NEUMORPH_RADIUS, BUTTON_BORDER_RADIUS, BUTTON_BG_COLOR, BUTTON_FONT_COLOR, 
    ENTRY_BORDER_RADIUS, ENTRY_BG_COLOR, ENTRY_FONT_COLOR, NOTES_BG_COLOR, 
    NOTES_FONT_COLOR, NOTES_BORDER_RADIUS, CONTROL_BTN_WIDTH, PROB_ID_ENTRY_WIDTH, 
    SEARCH_TEXT_ENTRY_WIDTH, ANSWER_ENTRY_WIDTH, SEARCH_TEXT_LABEL_PADDING, 
    ANSWER_LABEL_PADDING, DEFAULT_LABEL_PADDING, ROW_SPACING_REDUCTION, 
    NOTES_FIXED_HEIGHT, PADDING, SPACING, LEFT_PANEL_WIDTH, DOMAIN_GRID_SPACING, 
    DOMAIN_BTN_WIDTH, DOMAIN_BTN_HEIGHT, SECTION_LABEL_PADDING_TOP, BUTTON_MIN_WIDTH, 
    BUTTON_MIN_HEIGHT, ENTRY_MIN_HEIGHT, ENTRY_PADDING_LEFT, TEXTEDIT_PADDING, 
    SHADOW_RECT_ADJUST, SHADOW_OFFSETS, EDITOR_BG_COLOR, CATEGORY_BTN_SELECTED_COLOR
)
from db.problem_set_db import ProblemSetDB
from ui_qt.set_inputs_panel import SetInputsPanelQt
from ui_qt.set_editor_panel import SetEditorPanelQt
from ui_qt.neumorphic_components import NeumorphicButton, NeumorphicEntry, NeumorphicTextEdit
from ui_qt.set_selector_grid import SetSelectorGridQt

class ProblemTypePanelQt(QWidget):
    def __init__(self, parent=None, types=None):
        super().__init__(parent)
        # types should be a list of dicts: {"type_id": int, "name": str}
        if types is None:
            # fallback for legacy usage
            types = [
                {"type_id": 1, "name": "Intro"},
                {"type_id": 2, "name": "Efficiency"},
                {"type_id": 3, "name": "SAT-Problem"}
            ]
        self.types = types
        self.selected = set()  # set of type_id
        self.buttons = {}  # type_id: button
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        for t in self.types:
            btn = NeumorphicButton(t["name"], font_size=BUTTON_FONT_SIZE)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, tid=t["type_id"]: self.toggle_type(tid))
            layout.addWidget(btn)
            self.buttons[t["type_id"]] = btn
        # layout.addStretch()
        self.setLayout(layout)

    def toggle_type(self, type_id):
        btn = self.buttons[type_id]
        if btn.isChecked():
            self.selected.add(type_id)
        else:
            self.selected.discard(type_id)

    def get_selected_type_ids(self):
        return list(self.selected)

    def set_selected_type_ids(self, type_ids):
        for tid, btn in self.buttons.items():
            btn.setChecked(tid in type_ids)
            if tid in type_ids:
                self.selected.add(tid)
            else:
                self.selected.discard(tid)

class QueryInputsPanel(QWidget):
    """
    Panel containing ALL query-related input components:
    - Basic inputs: Problem ID, Search Text, Answer
    - Advanced inputs: Problem types, earmark, categories, notes
    """
    
    def __init__(self, parent=None, laptop_mode=False):
        super().__init__(parent)
        self.setStyleSheet('background: transparent;')
        self.laptop_mode = laptop_mode
        self._selected_set_id = None
        # --- Wrap all contents in a QFrame with border ---
        self.outer_frame = QFrame()
        self.outer_frame.setFrameShape(QFrame.StyledPanel)
        self.outer_frame.setStyleSheet('QFrame { border: 2px solid #888; border-radius: 12px; background: transparent; }')
        self.outer_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        outer_layout = QVBoxLayout(self.outer_frame)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(SPACING)
        self.init_ui(outer_layout)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.outer_frame)
    
    def init_ui(self, main_layout=None):
        """Initialize the UI components"""
        if main_layout is None:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)  # No extra margins
            main_layout.setSpacing(SPACING)
        
        # --- Group box for basic inputs and earmark/problem type row ---
        self.query_inputs_groupbox = QGroupBox("")
        groupbox_layout = QVBoxLayout(self.query_inputs_groupbox)
        groupbox_layout.setContentsMargins(0, 0, 0, 0)
        groupbox_layout.setSpacing(0)
        
        # --- Basic Inputs Row (Problem ID, Search Text, Answer) ---
        self._create_basic_inputs(groupbox_layout)
        
        # --- Earmark checkbox and Problem type buttons on the same row ---
        earmark_and_types_row = QHBoxLayout()
        earmark_and_types_row.setSpacing(8)
        earmark_and_types_row.setContentsMargins(0, 0, 0, 0)
        self.earmark_checkbox = QCheckBox("Earmark")
        self.earmark_checkbox.setFont(QFont(FONT_FAMILY, LABEL_FONT_SIZE, QFont.Bold))
        self.earmark_checkbox.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; margin-left: 10px;")
        earmark_and_types_row.addWidget(self.earmark_checkbox)
        from db.math_db import MathProblemDB
        db = MathProblemDB()
        types = db.cur.execute("SELECT type_id, name FROM problem_types ORDER BY name").fetchall()
        db.close()
        type_dicts = [{"type_id": row[0], "name": row[1]} for row in types]
        self.problem_type_panel = ProblemTypePanelQt(types=type_dicts)
        self.problem_type_panel.setContentsMargins(0, 0, 0, 0)
        self.problem_type_panel.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        earmark_and_types_row.addSpacing(1)
        earmark_and_types_row.addWidget(self.problem_type_panel)
        earmark_and_types_row.addStretch(2)
        groupbox_layout.addLayout(earmark_and_types_row)
        
        main_layout.addWidget(self.query_inputs_groupbox)
        main_layout.addSpacing(2)
        
        # --- Math Domains Section ---
        self.domains_groupbox = QGroupBox("")
        domains_groupbox_layout = QVBoxLayout(self.domains_groupbox)
        domains_groupbox_layout.setContentsMargins(0, 0, 0, 0)
        domains_groupbox_layout.setSpacing(0)
        domains_label = QLabel("Math Domains")
        domains_label.setFont(QFont(FONT_FAMILY, SECTION_LABEL_FONT_SIZE, QFont.Bold))
        domains_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding-top: 4px; padding-bottom: 4px; margin-top: 0px; margin-bottom: 0px; background: {WINDOW_BG_COLOR};")
        domains_label.setMinimumHeight(30)
        domains_label.setAlignment(Qt.AlignCenter)
        domains_groupbox_layout.addWidget(domains_label)
        self.category_panel = CategoryPanelQt()
        self.category_groupbox = QGroupBox("")
        self.category_groupbox.setMinimumHeight(300)
        category_layout = QVBoxLayout(self.category_groupbox)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(0)
        self.category_frame = QFrame()
        self.category_frame.setFrameShape(QFrame.StyledPanel)
        self.category_frame.setStyleSheet('QFrame { border: 2px solid #888; border-radius: 12px; background: transparent; }')
        frame_layout = QVBoxLayout(self.category_frame)
        frame_layout.setContentsMargins(0, 0, 0, 0)
        frame_layout.setSpacing(0)
        frame_layout.addWidget(self.category_panel)
        self.category_frame.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Maximum)
        category_layout.addWidget(self.category_frame)
        self.category_groupbox.setLayout(category_layout)
        domains_groupbox_layout.addWidget(self.category_groupbox)
        main_layout.addWidget(self.domains_groupbox)
        
        # --- Set Selector and Set Editor Section (QStackedWidget) ---
        self.set_selector_groupbox = QGroupBox("")
        set_selector_layout = QVBoxLayout(self.set_selector_groupbox)
        set_selector_layout.setContentsMargins(0, 0, 0, 0)
        set_selector_layout.setSpacing(0)
        set_selector_label = QLabel("Problem Sets")
        set_selector_label.setFont(QFont(FONT_FAMILY, SECTION_LABEL_FONT_SIZE, QFont.Bold))
        set_selector_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding-top: 4px; padding-bottom: 4px; margin-top: 0px; margin-bottom: 0px; background: {WINDOW_BG_COLOR};")
        set_selector_label.setMinimumHeight(30)
        set_selector_label.setAlignment(Qt.AlignCenter)
        set_selector_layout.addWidget(set_selector_label)
        self.set_selector_grid = SetSelectorGridQt()
        self.set_selector_grid.setMinimumHeight(150)
        set_selector_layout.addWidget(self.set_selector_grid)
        self.set_selector_groupbox.setLayout(set_selector_layout)

        # Set Editor Panel
        self.set_editor_panel = SetEditorPanelQt()

        # QStackedWidget to hold both
        self.set_stack = QStackedWidget()
        self.set_stack.addWidget(self.set_selector_groupbox)  # index 0
        self.set_stack.addWidget(self.set_editor_panel)       # index 1

        # Toggle button
        self.toggle_set_editor_btn = QPushButton("Open Set Editor")
        self.toggle_set_editor_btn.clicked.connect(self.toggle_set_editor_view)
        main_layout.addWidget(self.toggle_set_editor_btn)
        main_layout.addWidget(self.set_stack)

        self.set_selector_grid.set_selected.connect(self.on_set_selected)
    
    def _create_basic_inputs(self, main_layout):
        """Create the basic input fields (Problem ID, Search Text, Answer)"""
        input_row = QHBoxLayout()
        
        # Create input fields
        self.problem_id_entry = self._create_neumorphic_entry()
        self.search_text_entry = self._create_neumorphic_entry()
        self.answer_entry = self._create_neumorphic_entry()
        
        # Set field widths
        self.problem_id_entry.setFixedWidth(PROB_ID_ENTRY_WIDTH)
        self.search_text_entry.setFixedWidth(SEARCH_TEXT_ENTRY_WIDTH)
        self.answer_entry.setFixedWidth(ANSWER_ENTRY_WIDTH)
        
        # Create labeled columns
        labels = ["Prob ID", "Search Text", "Answer"]
        entries = [self.problem_id_entry, self.search_text_entry, self.answer_entry]
        
        for label, entry in zip(labels, entries):
            col = QVBoxLayout()
            col.setSpacing(0)
            col.setContentsMargins(0, 0, 0, 0)
            
            # Create label
            lbl = QLabel(label)
            lbl.setFont(QFont(FONT_FAMILY, LABEL_FONT_SIZE, QFont.Bold))
            lbl.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding: 0px; margin: 0px; background: {WINDOW_BG_COLOR};")
            lbl.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
            lbl.setMinimumHeight(LABEL_FONT_SIZE + 4)  # Ensure label is always visible
            
            col.addWidget(lbl, alignment=Qt.AlignLeft)
            col.addSpacing(1)  #@@ # More space between label and entry
            
            # Set entry height and add to column
            entry.setMinimumHeight(36)  # Entry field height KEEP
            col.addWidget(entry)
            input_row.addLayout(col)  # <-- Add each column to the row
        
        main_layout.addLayout(input_row)
    
    def _create_neumorphic_entry(self):
        """Create a neumorphic entry field with standard styling"""
        return NeumorphicEntry(
            radius=ENTRY_BORDER_RADIUS,
            bg_color=ENTRY_BG_COLOR,
            shadow_dark=NEUMORPH_SHADOW_DARK,
            shadow_light=NEUMORPH_SHADOW_LIGHT,
            font_family=FONT_FAMILY,
            font_size=ENTRY_FONT_SIZE,
            font_color=ENTRY_FONT_COLOR
        )
    
    def get_problem_id(self):
        return self.problem_id_entry.text()
    
    def set_problem_id(self, value):
        self.problem_id_entry.setText(str(value))
    
    def get_answer(self):
        return self.answer_entry.text()
    
    def set_answer(self, value):
        self.answer_entry.setText(str(value))
    
    def get_search_text(self):
        return self.search_text_entry.text()
    
    def set_search_text(self, value):
        self.search_text_entry.setText(str(value))
    
    def get_earmark(self):
        return self.earmark_checkbox.isChecked()
    
    def set_earmark(self, value):
        self.earmark_checkbox.setChecked(value)
    
    def get_selected_type_ids(self):
        return self.problem_type_panel.get_selected_type_ids()
    
    def set_selected_type_ids(self, type_ids):
        self.problem_type_panel.set_selected_type_ids(type_ids)
    
    def get_selected_categories(self):
        return self.category_panel.get_selected_categories()
    
    def clear_category_selection(self):
        self.category_panel.clear_selection()
    
    def reset_all_inputs(self):
        """Reset all input fields to their default state"""
        self.problem_id_entry.setText("")
        self.search_text_entry.setText("")
        self.answer_entry.setText("")
        self.earmark_checkbox.setChecked(False)
        self.problem_type_panel.set_selected_type_ids([])
        self.clear_category_selection()
        self.set_selector_grid.clear_selection()
        if hasattr(self, 'notes_edit'):
            self.notes_edit.setText("")
    
    def build_query_criteria(self):
        """Build query criteria from current input values"""
        criteria = {}
        if self.get_problem_id():
            criteria['problem_id'] = self.get_problem_id()
        if self.get_search_text():
            criteria['search_text'] = self.get_search_text()
        if self.get_answer():
            criteria['answer'] = self.get_answer()
        if self.get_earmark():
            criteria['earmark'] = True
        type_ids = self.get_selected_type_ids()
        if type_ids:
            criteria['type_ids'] = type_ids
        categories = self.get_selected_categories()
        if categories:
            criteria['categories'] = categories
        set_ids = self.get_selected_sets()
        if set_ids:
            criteria['set_ids'] = set_ids
        return criteria
    
    def apply_query_criteria(self, criteria):
        """Apply query criteria to input fields"""
        self.reset_all_inputs()
        if 'problem_id' in criteria:
            self.set_problem_id(criteria['problem_id'])
        if 'search_text' in criteria:
            self.set_search_text(criteria['search_text'])
        if 'answer' in criteria:
            self.set_answer(criteria['answer'])
        if 'earmark' in criteria:
            self.set_earmark(criteria['earmark'])
        if 'type_ids' in criteria:
            self.set_selected_type_ids(criteria['type_ids'])
        if 'categories' in criteria:
            for category in criteria['categories']:
                self.category_panel.select_category(category)
        if 'set_ids' in criteria:
            self.set_selected_sets(criteria['set_ids'])
    
    def validate_inputs(self):
        """Validate input values"""
        errors = []
        problem_id = self.get_problem_id()
        if problem_id:
            try:
                int(problem_id)
            except ValueError:
                errors.append("Problem ID must be a number")
        return errors
    
    def has_any_input(self):
        """Check if any input field has a value"""
        return (
            bool(self.get_problem_id()) or
            bool(self.get_search_text()) or
            bool(self.get_answer()) or
            self.get_earmark() or
            bool(self.get_selected_type_ids()) or
            bool(self.get_selected_categories()) or
            bool(self.get_selected_sets())
        )
    
    def get_search_mode(self):
        """Get the current search mode based on inputs"""
        if self.get_problem_id():
            return 'id'
        elif self.get_search_text():
            return 'text'
        elif self.get_answer():
            return 'answer'
        elif self.get_earmark():
            return 'earmark'
        elif self.get_selected_type_ids():
            return 'type'
        elif self.get_selected_categories():
            return 'category'
        elif self.get_selected_sets():
            return 'set'
        return None
    
    def get_selected_sets(self):
        """Get the list of selected set IDs"""
        return self.set_selector_grid.get_selected_sets()

    def get_selected_set_ids(self):
        """Alias for get_selected_sets() for backward compatibility"""
        return self.get_selected_sets()

    def set_selected_sets(self, set_ids):
        """Set which sets are selected"""
        # If you want to implement this, add a set_selected_sets method to SetSelectorGridQt
        pass
    
    def set_notes(self, text):
        """Set the notes text"""
        pass  # No notes field in this panel
    
    def get_notes(self):
        """Get the notes text"""
        return ""  # No notes field in this panel
    
    def on_set_selected(self, set_id):
        """Handle set selection"""
        self._selected_set_id = set_id

    def toggle_set_editor_view(self):
        if self.set_stack.currentIndex() == 0:
            self.set_stack.setCurrentIndex(1)
            self.toggle_set_editor_btn.setText("Back to Set Selector")
        else:
            self.set_stack.setCurrentIndex(0)
            self.toggle_set_editor_btn.setText("Open Set Editor")