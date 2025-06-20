# edit_selected_problems_panel.py
"""
Edit Selected Problems panel for the Simplified Math Editor (PyQt5).

This panel allows bulk editing of attributes for selected problems:
- Earmark
- Problem types
- Categories
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import (
    FONT_FAMILY, LABEL_FONT_SIZE, SECTION_LABEL_FONT_SIZE,
    NEUMORPH_TEXT_COLOR, WINDOW_BG_COLOR, CONTROL_BTN_FONT_SIZE,
    BUTTON_TEXT_PADDING, PADDING, SPACING
)


class EditSelectedProblemsPanel(QWidget):
    """Panel for bulk editing attributes of selected problems"""
    
    # Signals
    apply_attributes = pyqtSignal(dict)  # Emits dict of attributes to apply
    clear_attributes = pyqtSignal(dict)  # Emits dict of attributes to clear
    
    def __init__(self, parent=None, query_inputs_panel=None):
        super().__init__(parent)
        self.setStyleSheet('background: transparent;')
        self.query_inputs_panel = query_inputs_panel
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(SPACING)
        
        # Section title
        title_label = QLabel("Edit Selected Problems")
        title_font = QFont(FONT_FAMILY)
        title_font.setPointSizeF(SECTION_LABEL_FONT_SIZE)
        title_font.setWeight(QFont.Bold)
        title_label.setFont(title_font)
        title_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR}; padding-top: 4px; padding-bottom: 4px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Frame for content
        content_frame = QFrame()
        content_frame.setFrameShape(QFrame.StyledPanel)
        content_frame.setStyleSheet('QFrame { border: 1px solid #888; border-radius: 8px; background: transparent; }')
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        content_layout.setSpacing(SPACING)
        
        # Info label
        info_label = QLabel("Use the attribute selections above (Earmarks, Problem Types, Categories) to edit selected problems")
        info_font = QFont(FONT_FAMILY)
        info_font.setPointSizeF(LABEL_FONT_SIZE - 1)
        info_label.setFont(info_font)
        info_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        info_label.setWordWrap(True)
        content_layout.addWidget(info_label)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(SPACING)
        
        self.clear_button = NeumorphicButton("Clear Attribute(s)", font_size=CONTROL_BTN_FONT_SIZE)
        self.apply_button = NeumorphicButton("Apply Attribute(s)", font_size=CONTROL_BTN_FONT_SIZE)
        
        # Set button widths based on text
        for btn in [self.clear_button, self.apply_button]:
            fm = btn.fontMetrics()
            text_width = fm.horizontalAdvance(btn.text()) if hasattr(fm, 'horizontalAdvance') else fm.width(btn.text())
            btn.setFixedWidth(text_width + (BUTTON_TEXT_PADDING * 2))
        
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.apply_button)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_frame)
        
        # Connect signals
        self.clear_button.clicked.connect(self._on_clear_clicked)
        self.apply_button.clicked.connect(self._on_apply_clicked)
    
    def _get_selected_attributes(self):
        """Get currently selected attributes from the query inputs panel"""
        if not self.query_inputs_panel:
            return {}
            
        attributes = {}
        
        # Get selected earmarks
        earmark_ids = self.query_inputs_panel.get_selected_earmark_ids()
        if earmark_ids:
            attributes['earmark_ids'] = earmark_ids
        
        # Get selected problem types
        type_ids = self.query_inputs_panel.get_selected_type_ids()
        if type_ids:
            attributes['type_ids'] = type_ids
        
        # Get selected categories
        categories = self.query_inputs_panel.get_selected_categories()
        if categories:
            attributes['categories'] = categories
        
        return attributes
    
    def _on_clear_clicked(self):
        """Handle clear button click"""
        attributes = self._get_selected_attributes()
        if attributes:
            self.clear_attributes.emit(attributes)
    
    def _on_apply_clicked(self):
        """Handle apply button click"""
        attributes = self._get_selected_attributes()
        if attributes:
            self.apply_attributes.emit(attributes)