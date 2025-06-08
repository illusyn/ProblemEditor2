from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QScrollArea
from PyQt5.QtCore import pyqtSignal
from db.problem_set_db import ProblemSetDB
from ui_qt.category_panel import NeumorphicToolButton
from ui_qt.style_config import SET_EDITOR_BUTTON_FONT_SIZE

class SetSelectorGridQt(QWidget):
    set_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.set_buttons = {}
        self.selected_set_id = None
        # Create the grid widget and layout
        self.grid_widget = QWidget()
        self.layout = QGridLayout(self.grid_widget)
        self.layout.setSpacing(16)
        self.layout.setContentsMargins(0, 0, 0, 0)
        # Create the scroll area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.grid_widget)
        self.scroll_area.setStyleSheet('border: none;')
        # Main layout
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.scroll_area, 0, 0)
        self.refresh_sets()

    def refresh_sets(self):
        # Remove old buttons
        for btn in getattr(self, 'set_buttons', {}).values():
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.set_buttons = {}
        db = ProblemSetDB()
        sets = db.get_all_sets()
        db.close()
        if not sets:
            label = QLabel("No sets defined.")
            self.layout.addWidget(label, 0, 0)
            return
        cols = 3
        for idx, (set_id, name, *_) in enumerate(sets):
            row = idx // cols
            col = idx % cols
            btn = NeumorphicToolButton(name, font_size=SET_EDITOR_BUTTON_FONT_SIZE)
            btn.setMinimumWidth(290)
            btn.setMaximumWidth(290)
            btn.setCheckable(True)
            btn.setChecked(self.selected_set_id == set_id)
            btn.clicked.connect(lambda checked, sid=set_id: self.on_set_selected(sid, checked))
            self.layout.addWidget(btn, row, col)
            self.set_buttons[set_id] = btn

    def on_set_selected(self, set_id, checked):
        if checked:
            # Uncheck all others
            for sid, btn in self.set_buttons.items():
                if sid != set_id:
                    btn.setChecked(False)
            self.selected_set_id = set_id
            self.set_selected.emit(set_id)
        else:
            self.selected_set_id = None

    def get_selected_set_id(self):
        return self.selected_set_id 