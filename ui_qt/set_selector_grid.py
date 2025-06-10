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
        self.button_to_set_id = {}  # Map button to set_id for easier access
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
            
            # Store mapping
            self.button_to_set_id[btn] = set_id
            
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
        """Toggle selection of a set (single selection only)"""
        print(f"[DEBUG] toggle_set called: set_id={set_id}, is_selected={is_selected}")
        
        if is_selected:
            # Clear any existing selection first (single selection mode)
            cleared_sets = []
            for btn, btn_set_id in self.button_to_set_id.items():
                if btn_set_id != set_id and btn.isChecked():
                    btn.setChecked(False)
                    self.selected_sets.discard(btn_set_id)
                    cleared_sets.append(btn_set_id)
            
            if cleared_sets:
                print(f"[DEBUG] Cleared previous selections: {cleared_sets}")
            
            # Add the new selection
            self.selected_sets.clear()  # Ensure only one selection
            self.selected_sets.add(set_id)
            print(f"[DEBUG] Added selection: {set_id}")
        else:
            self.selected_sets.discard(set_id)
            print(f"[DEBUG] Removed selection: {set_id}")
        
        print(f"[DEBUG] Current selected_sets: {list(self.selected_sets)}")
        self.set_selected.emit(set_id, is_selected)
    
    def get_selected_sets(self):
        """Get list of selected set IDs"""
        return list(self.selected_sets)
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_sets.clear()
        # Uncheck all buttons
        for btn in self.button_to_set_id.keys():
            btn.setChecked(False)
    
    def refresh_sets(self):
        print("[DEBUG] refresh_sets() called")
        
        # Remove all widgets from the grid layout
        widget_count = self.grid_layout.count()
        print(f"[DEBUG] Removing {widget_count} widgets from grid")
        
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
        
        # Clear mappings and selections
        self.selected_sets.clear()
        self.button_to_set_id.clear()
        
        # Load sets from database
        db = ProblemSetDB()
        sets = db.get_all_sets()
        db.close()
        
        print(f"[DEBUG] Loaded {len(sets)} sets from database: {[s[1] for s in sets]}")
        
        row = 0
        col = 0
        max_cols = 2
        
        for set_data in sets:
            set_id, set_name, description, is_ordered = set_data
            print(f"[DEBUG] Creating button for set: {set_name} (ID: {set_id})")
            
            btn = NeumorphicButton(set_name)
            btn.setCheckable(True)
            btn.setMinimumHeight(40)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(lambda checked, sid=set_id: self.toggle_set(sid, checked))
            
            # Store mapping
            self.button_to_set_id[btn] = set_id
            
            self.grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        
        self.grid_layout.setRowStretch(row + 1, 1)
        print(f"[DEBUG] refresh_sets() completed, grid now has {len(self.button_to_set_id)} buttons") 