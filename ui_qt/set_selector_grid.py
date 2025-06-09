"""
Set selector grid for the Simplified Math Editor (PyQt5).

This module provides a grid of buttons for selecting problem sets,
with neumorphic styling and proper signal handling.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGridLayout, 
                             QScrollArea, QSizePolicy)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import (
    FONT_FAMILY, BUTTON_FONT_SIZE, NEUMORPH_TEXT_COLOR, 
    BUTTON_MIN_WIDTH, BUTTON_MIN_HEIGHT, DOMAIN_GRID_SPACING
)
from db.problem_set_db import ProblemSetDB

class SetSelectorGridQt(QWidget):
    """Grid of buttons for selecting problem sets"""
    
    set_selected = pyqtSignal(int, bool)  # set_id, is_selected
    
    def __init__(self):
        super().__init__()
        self.selected_sets = set()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create container widget for grid
        container = QWidget()
        self.grid_layout = QGridLayout(container)
        self.grid_layout.setSpacing(10)
        
        # Load sets from database
        db = ProblemSetDB()
        sets = db.get_all_sets()
        db.close()
        
        # Create buttons for each set
        row = 0
        col = 0
        max_cols = 2  # Number of columns in the grid
        
        for set_data in sets:
            set_id, set_name, description, is_ordered = set_data
            
            # Create neumorphic button
            btn = NeumorphicButton(set_name)
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, sid=set_id: self.toggle_set(sid, checked))
            
            # Add to grid
            self.grid_layout.addWidget(btn, row, col)
            
            # Update grid position
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        # Add stretch to push buttons to the top
        self.grid_layout.setRowStretch(row + 1, 1)
        
        # Set the container as the scroll area's widget
        scroll.setWidget(container)
        
        # Add scroll area to main layout
        layout.addWidget(scroll)
    
    def toggle_set(self, set_id, is_selected):
        """Toggle selection of a set"""
        if is_selected:
            self.selected_sets.add(set_id)
        else:
            self.selected_sets.discard(set_id)
        self.set_selected.emit(set_id, is_selected)
    
    def get_selected_sets(self):
        """Get list of selected set IDs"""
        return list(self.selected_sets)
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_sets.clear()
        # Uncheck all buttons
        for i in range(self.grid_layout.count()):
            widget = self.grid_layout.itemAt(i).widget()
            if isinstance(widget, NeumorphicButton):
                widget.setChecked(False) 