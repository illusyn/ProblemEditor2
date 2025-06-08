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
        
        # Remove or reduce spacing before Math Domains
        # main_layout.addSpacing(-20)  # Back to previous value
        
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
        self.category_groupbox.setMinimumHeight(400)
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
        
        # --- Toggle Set Editor Button and QStackedWidget ---
        self.toggle_set_editor_btn = QPushButton("Open Set Editor")
        self.toggle_set_editor_btn.setFont(QFont(FONT_FAMILY, LABEL_FONT_SIZE, QFont.Bold))
        self.toggle_set_editor_btn.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; margin: 8px 0px 8px 0px;")
        main_layout.addWidget(self.toggle_set_editor_btn)

        self.set_stack = QStackedWidget()
        self.set_selector_grid = SetSelectorGridQt()
        self.set_stack.addWidget(self.set_selector_grid)  # Page 0: set selector for filtering
        self.set_editor_panel = SetEditorPanelQt()
        self.set_stack.addWidget(self.set_editor_panel)   # Page 1: set editor
        main_layout.addWidget(self.set_stack)

        # Toggle between set selector and set editor
        def toggle_set_editor():
            if self.set_stack.currentIndex() == 0:
                self.set_stack.setCurrentIndex(1)
                self.toggle_set_editor_btn.setText("Close Set Editor")
            else:
                self.set_stack.setCurrentIndex(0)
                self.toggle_set_editor_btn.setText("Open Set Editor")
        self.toggle_set_editor_btn.clicked.connect(toggle_set_editor)
        self.set_stack.setCurrentIndex(0)
    
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
            shadow_dark=QColor(NEUMORPH_SHADOW_DARK),
            shadow_light=QColor(NEUMORPH_SHADOW_LIGHT),
            font_family=FONT_FAMILY,
            font_size=ENTRY_FONT_SIZE,
            font_color=ENTRY_FONT_COLOR
        )
    
    # --- Basic input field methods ---
    def get_problem_id(self):
        """Get the problem ID input value"""
        return self.problem_id_entry.text()

    def set_problem_id(self, value):
        """Set the problem ID input value"""
        self.problem_id_entry.setText(value)

    def get_answer(self):
        """Get the answer input value"""
        return self.answer_entry.text()

    def set_answer(self, value):
        """Set the answer input value"""
        self.answer_entry.setText(value)

    def get_search_text(self):
        """Get the search text input value"""
        return self.search_text_entry.text()

    def set_search_text(self, value):
        """Set the search text input value"""
        self.search_text_entry.setText(value)
    
    # --- Earmark methods ---
    def get_earmark(self):
        """Get earmark checkbox state"""
        return self.earmark_checkbox.isChecked()

    def set_earmark(self, value):
        """Set earmark checkbox state"""
        self.earmark_checkbox.setChecked(bool(value))
    
    # --- Problem type methods ---
    def get_selected_type_ids(self):
        """Get list of selected problem type IDs"""
        return self.problem_type_panel.get_selected_type_ids()

    def set_selected_type_ids(self, type_ids):
        """Set selected problem type IDs"""
        self.problem_type_panel.set_selected_type_ids(type_ids)
    
    # --- Category methods ---
    def get_selected_categories(self):
        """Get list of selected category dictionaries"""
        return self.category_panel.get_selected_categories()
    
    def clear_category_selection(self):
        """Clear all category selections"""
        for btn in self.category_panel.buttons.values():
            btn.setChecked(False)
        self.category_panel.selected.clear()
    
    # --- Reset functionality ---
    def reset_all_inputs(self):
        """Reset all query inputs to default state"""
        # Reset basic inputs
        self.problem_id_entry.setText("")
        self.search_text_entry.setText("")
        self.answer_entry.setText("")
        
        # Reset earmark
        self.earmark_checkbox.setChecked(False)
        
        # Reset problem types
        for btn in self.problem_type_panel.buttons.values():
            btn.setChecked(False)
        self.problem_type_panel.selected.clear()
        
        # Reset categories
        self.clear_category_selection()
    
    # --- Query building methods ---
    def build_query_criteria(self):
        """
        Build a dictionary of query criteria from current input state
        
        Returns:
            dict: Query criteria with all inputs
        """
        return {
            # Basic inputs
            'problem_id': self.get_problem_id().strip(),
            'search_text': self.get_search_text().strip(),
            'answer': self.get_answer().strip(),
            # Advanced inputs
            'earmark': self.get_earmark(),
            'selected_type_ids': self.get_selected_type_ids(),
            'selected_categories': self.get_selected_categories(),
        }
    
    def apply_query_criteria(self, criteria):
        """
        Apply query criteria to set the input state
        
        Args:
            criteria (dict): Query criteria dictionary
        """
        # Apply basic inputs
        if 'problem_id' in criteria:
            self.set_problem_id(criteria['problem_id'])
        if 'search_text' in criteria:
            self.set_search_text(criteria['search_text'])
        if 'answer' in criteria:
            self.set_answer(criteria['answer'])
        
        # Apply advanced inputs
        if 'earmark' in criteria:
            self.set_earmark(criteria['earmark'])
        
        if 'selected_type_ids' in criteria:
            self.set_selected_type_ids(criteria['selected_type_ids'])
        
        if 'selected_categories' in criteria:
            # Set categories by name
            category_names = [cat['name'] if isinstance(cat, dict) else cat 
                            for cat in criteria['selected_categories']]
            for cat in self.category_panel.categories:
                btn = self.category_panel.buttons[cat["category_id"]]
                if cat["name"] in category_names:
                    btn.setChecked(True)
                    self.category_panel.selected.add(cat["category_id"])
                else:
                    btn.setChecked(False)
                    self.category_panel.selected.discard(cat["category_id"])
    
    # --- Validation methods ---
    def validate_inputs(self):
        """
        Validate current input state
        
        Returns:
            tuple: (is_valid, error_message)
        """
        criteria = self.build_query_criteria()
        
        # Check for problem ID format if provided
        if criteria['problem_id']:
            try:
                int(criteria['problem_id'])
            except ValueError:
                return False, "Problem ID must be a valid number"
        
        # Check if at least one search criterion is provided
        has_criteria = any([
            criteria['problem_id'],
            criteria['search_text'],
            criteria['earmark'],
            criteria['selected_type_ids'],
            criteria['selected_categories']
        ])
        
        if not has_criteria:
            return False, "Please provide at least one search criterion"
        
        return True, "Valid"
    
    def has_any_input(self):
        """Check if any input field has content"""
        criteria = self.build_query_criteria()
        return any([
            criteria['problem_id'],
            criteria['search_text'], 
            criteria['answer'],
            criteria['earmark'],
            criteria['selected_type_ids'],
            criteria['selected_categories'],
        ])
    
    def get_search_mode(self):
        """
        Determine the current search mode based on inputs
        
        Returns:
            str: 'direct_id', 'text_search', 'filtered_search', or 'browse_all'
        """
        criteria = self.build_query_criteria()
        
        if criteria['problem_id']:
            return 'direct_id'
        elif criteria['search_text']:
            return 'text_search'
        elif any([criteria['earmark'], criteria['selected_type_ids'], criteria['selected_categories']]):
            return 'filtered_search'
        else:
            return 'browse_all'

    # --- Set methods ---
    def get_selected_set_ids(self):
        return self.set_editor_panel.get_selected_set_id()

    def set_selected_set_ids(self, set_ids):
        self.set_editor_panel.set_selected_set_id(set_ids)

    def set_notes(self, text):
        """Set the notes input value"""
        # self.notes_text.setPlainText(text)
        pass

    def get_notes(self):
        """Get the notes input value"""
        # return self.notes_text.toPlainText()
        return ""

    # Connect set selector signal (for filtering)
    def on_set_selected(self, set_id):
        # TODO: implement filtering logic for selected set
        print(f"[DEBUG] Set selected for filtering: {set_id}")