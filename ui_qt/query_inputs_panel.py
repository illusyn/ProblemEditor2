# query_inputs_panel.py
"""
Query inputs panel for the Simplified Math Editor (PyQt5).

This module contains ALL query-related input components:
- Basic inputs: Problem ID, Search Text, Answer
- Advanced inputs: Problem types, earmark, categories, notes
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QTextEdit, 
    QLineEdit, QPushButton, QCheckBox, QScrollArea, QSizePolicy, QGroupBox, QComboBox
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

class NeumorphicButton(QPushButton):
    def __init__(self, text, parent=None, radius=NEUMORPH_RADIUS, bg_color=NEUMORPH_BG_COLOR, 
                 shadow_dark=NEUMORPH_SHADOW_DARK, shadow_light=NEUMORPH_SHADOW_LIGHT, 
                 font_family=FONT_FAMILY, font_size=BUTTON_FONT_SIZE, font_color=BUTTON_FONT_COLOR):
        super().__init__(text, parent)
        self.radius = radius
        self.bg_color = bg_color
        self.shadow_dark = shadow_dark
        self.shadow_light = shadow_light
        self.font_family = font_family
        self.font_size = font_size
        self.font_color = font_color
        self.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        self.setStyleSheet("background: transparent; border: none;")
        self.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.setMinimumWidth(BUTTON_MIN_WIDTH)

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect().adjusted(SHADOW_RECT_ADJUST, SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST)
            # Multi-layered blurred shadow (bottom-right)
            for i, alpha in zip(SHADOW_OFFSETS, [40, 60, 90]):
                shadow = QColor(self.shadow_dark)
                shadow.setAlpha(alpha)
                painter.setBrush(QBrush(shadow))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
            # Multi-layered highlight (top-left)
            for i, alpha in zip(SHADOW_OFFSETS, [30, 50, 80]):
                highlight = QColor(self.shadow_light)
                highlight.setAlpha(alpha)
                painter.setBrush(QBrush(highlight))
                painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
            # Solid background (highlight if checked)
            if self.isCheckable() and self.isChecked():
                painter.setBrush(QBrush(QColor(CATEGORY_BTN_SELECTED_COLOR)))
            else:
                painter.setBrush(QBrush(QColor(self.bg_color)))
            painter.drawRoundedRect(rect, self.radius, self.radius)
            # Text
            painter.setPen(QColor(self.font_color))
            painter.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
            painter.drawText(rect, Qt.AlignCenter, self.text())
        finally:
            painter.end()

class NeumorphicEntry(QLineEdit):
    def __init__(self, parent=None, radius=ENTRY_BORDER_RADIUS, bg_color=ENTRY_BG_COLOR, 
                 shadow_dark=NEUMORPH_SHADOW_DARK, shadow_light=NEUMORPH_SHADOW_LIGHT, 
                 font_family=FONT_FAMILY, font_size=ENTRY_FONT_SIZE, font_color=ENTRY_FONT_COLOR):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = bg_color
        self.shadow_dark = shadow_dark
        self.shadow_light = shadow_light
        self.font_family = font_family
        self.font_size = font_size
        self.font_color = font_color
        self.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        self.setStyleSheet(f"background: transparent; border: none; color: {self.font_color}; padding-left: {ENTRY_PADDING_LEFT}px;")
        self.setMinimumHeight(ENTRY_MIN_HEIGHT)

    def paintEvent(self, event):
        painter = QPainter(self)
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect().adjusted(SHADOW_RECT_ADJUST, SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST)
            # Sunken effect: shadow top-left, highlight bottom-right
            for i, alpha in zip(SHADOW_OFFSETS, [40, 60, 90]):
                shadow = QColor(self.shadow_dark)
                shadow.setAlpha(alpha)
                painter.setBrush(QBrush(shadow))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
            for i, alpha in zip(SHADOW_OFFSETS, [30, 50, 80]):
                highlight = QColor(self.shadow_light)
                highlight.setAlpha(alpha)
                painter.setBrush(QBrush(highlight))
                painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
            # Solid background (no gradient)
            painter.setBrush(QBrush(QColor(self.bg_color)))
            painter.drawRoundedRect(rect, self.radius, self.radius)
            # Call base class paint for text/cursor
            super().paintEvent(event)
        finally:
            painter.end()

class NeumorphicTextEdit(QTextEdit):
    def __init__(self, parent=None, radius=NOTES_BORDER_RADIUS, bg_color=NOTES_BG_COLOR, 
                 shadow_dark=NEUMORPH_SHADOW_DARK, shadow_light=NEUMORPH_SHADOW_LIGHT, 
                 font_family=FONT_FAMILY, font_size=NOTES_FONT_SIZE, font_color=NOTES_FONT_COLOR):
        super().__init__(parent)
        self.radius = radius
        self.bg_color = bg_color
        self.shadow_dark = shadow_dark
        self.shadow_light = shadow_light
        self.font_family = font_family
        self.font_size = font_size
        self.font_color = font_color
        self.setFont(QFont(self.font_family, self.font_size, QFont.Bold))
        self.setStyleSheet(f"background: transparent; border: none; color: {self.font_color}; padding: {TEXTEDIT_PADDING}px;")
        self.setFixedHeight(NOTES_FIXED_HEIGHT)  # Use centralized height

    def paintEvent(self, event):
        painter = QPainter(self.viewport())
        try:
            painter.setRenderHint(QPainter.Antialiasing)
            rect = self.rect().adjusted(SHADOW_RECT_ADJUST, SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST, -SHADOW_RECT_ADJUST)
            # Multi-layered blurred shadow (bottom-right)
            for i, alpha in zip(SHADOW_OFFSETS, [40, 60, 90]):
                shadow = QColor(self.shadow_dark)
                shadow.setAlpha(alpha)
                painter.setBrush(QBrush(shadow))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(rect.translated(i, i), self.radius, self.radius)
            # Multi-layered highlight (top-left)
            for i, alpha in zip(SHADOW_OFFSETS, [30, 50, 80]):
                highlight = QColor(self.shadow_light)
                highlight.setAlpha(alpha)
                painter.setBrush(QBrush(highlight))
                painter.drawRoundedRect(rect.translated(-i, -i), self.radius, self.radius)
            # Solid background (no gradient)
            painter.setBrush(QBrush(QColor(self.bg_color)))
            painter.drawRoundedRect(rect, self.radius, self.radius)
            super().paintEvent(event)
        finally:
            painter.end()

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
        layout.addStretch()
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
        # --- Wrap all contents in a QGroupBox ---
        from PyQt5.QtWidgets import QGroupBox, QVBoxLayout
        self.outer_groupbox = QGroupBox("")
        outer_layout = QVBoxLayout(self.outer_groupbox)
        outer_layout.setContentsMargins(8, 8, 8, 8)
        outer_layout.setSpacing(SPACING)
        self.init_ui(outer_layout)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.outer_groupbox)
    
    def init_ui(self, main_layout=None):
        """Initialize the UI components"""
        if main_layout is None:
            main_layout = QVBoxLayout(self)
            main_layout.setContentsMargins(0, 0, 0, 0)  # No extra margins
            main_layout.setSpacing(SPACING)
        
        # --- Basic Inputs Row (Problem ID, Search Text, Answer) ---
        self._create_basic_inputs(main_layout)
        
        # Add spacing before advanced inputs
        main_layout.addSpacing(4)
        
        # --- Earmark checkbox and Problem type buttons on the same row ---
        earmark_and_types_row = QHBoxLayout()
        earmark_and_types_row.setSpacing(16)
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
        earmark_and_types_row.addSpacing(12)
        earmark_and_types_row.addWidget(self.problem_type_panel)
        earmark_and_types_row.addStretch(20)
        main_layout.addLayout(earmark_and_types_row)
        
        main_layout.addSpacing(40)  # Add space after problem type buttons
        
        # Remove or reduce spacing before Math Domains
        main_layout.addSpacing(-40)  # Minimal spacing
        
        # --- Math Domains Section ---
        domains_label = QLabel("Math Domains")
        domains_label.setFont(QFont(FONT_FAMILY, SECTION_LABEL_FONT_SIZE, QFont.Bold))
        domains_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding-top: 0px; padding-bottom: 0px; margin-top: 0px; margin-bottom: 0px; background: {WINDOW_BG_COLOR};")
        domains_label.setMaximumHeight(16)
        domains_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(domains_label)
        
        self.category_panel = CategoryPanelQt()
        self.category_groupbox = QGroupBox("")
        self.category_groupbox.setMinimumHeight(440)
        category_layout = QVBoxLayout(self.category_groupbox)
        category_layout.setContentsMargins(0, 0, 0, 0)
        category_layout.setSpacing(0)
        category_layout.addWidget(self.category_panel)
        self.category_groupbox.setLayout(category_layout)
        main_layout.addWidget(self.category_groupbox)
        
        # --- Sets Panel (for filtering) ---
        self.set_panel = SetInputsPanelQt()
        main_layout.addWidget(self.set_panel)
    
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
            col.addSpacing(8)  # More space between label and entry
            
            # Set entry height and add to column
            entry.setMinimumHeight(36)  # Entry field height
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
        return self.set_panel.get_selected_set_ids()

    def set_selected_set_ids(self, set_ids):
        self.set_panel.set_selected_set_ids(set_ids)