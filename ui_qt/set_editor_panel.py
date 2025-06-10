from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox, QLabel, QTableWidget, QTableWidgetItem, QAbstractItemView, QStyledItemDelegate, QStyle, QGridLayout, QFrame
from db.problem_set_db import ProblemSetDB
from ui_qt.neumorphic_components import NeumorphicButton, NeumorphicEntry, NeumorphicTextEdit
from ui_qt.style_config import BUTTON_MIN_HEIGHT, BUTTON_MIN_WIDTH, FONT_FAMILY, SECTION_LABEL_FONT_SIZE, NEUMORPH_TEXT_COLOR, NEUMORPH_BG_COLOR, NEUMORPH_SHADOW_DARK, NEUMORPH_SHADOW_LIGHT, CATEGORY_BTN_SELECTED_COLOR, NEUMORPH_RADIUS, SET_EDITOR_CONTROL_BUTTON_FONT_SIZE, SET_EDITOR_BUTTON_FONT_SIZE, SET_EDITOR_LABEL_FONT_SIZE, SET_EDITOR_HEAD_FONT_SIZE
from PyQt5.QtCore import Qt, pyqtSignal, QRect
from PyQt5.QtGui import QFont, QColor, QBrush, QPen, QPainter
from ui_qt.category_panel import NeumorphicToolButton
from ui_qt.set_selector_grid import SetSelectorGridQt

class NeumorphicTileDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        rect = option.rect
        painter.save()

        bg_color = QColor(NEUMORPH_BG_COLOR)
        shadow_dark = QColor(NEUMORPH_SHADOW_DARK)
        shadow_light = QColor(NEUMORPH_SHADOW_LIGHT)
        selected_color = QColor(CATEGORY_BTN_SELECTED_COLOR)
        radius = NEUMORPH_RADIUS

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        # Draw base background
        painter.setBrush(QBrush(bg_color))
        painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), radius, radius)

        # Neumorphic shadow (bottom-right)
        shadow = QColor(shadow_dark)
        shadow.setAlpha(60)
        painter.setBrush(QBrush(shadow))
        painter.drawRoundedRect(rect.adjusted(8, 8, -8, -8), radius, radius)

        # Neumorphic highlight (top-left)
        highlight = QColor(shadow_light)
        highlight.setAlpha(50)
        painter.setBrush(QBrush(highlight))
        painter.drawRoundedRect(rect.adjusted(-2, -2, 2, 2), radius, radius)

        # If selected, overlay the selected color
        if option.state & QStyle.State_Selected:
            painter.setBrush(QBrush(selected_color))
            painter.drawRoundedRect(rect.adjusted(4, 4, -4, -4), radius, radius)

        # Draw text
        painter.setPen(QColor(NEUMORPH_TEXT_COLOR))
        font = QFont(FONT_FAMILY, SET_EDITOR_BUTTON_FONT_SIZE, QFont.Bold)
        painter.setFont(font)
        text = index.data(Qt.DisplayRole)
        painter.drawText(rect, Qt.AlignCenter, text)

        painter.restore()

class SetEditorPanelQt(QWidget):
    add_selected_problems_to_set = pyqtSignal(list, object)  # selected_problems, selected_set_id
    def __init__(self, parent=None):
        super().__init__(parent)
        # --- Directly use main layout for all contents (no QFrame border) ---
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)
        # Title label
        title_label = QLabel("Set Editor")
        title_label.setFont(QFont(FONT_FAMILY, SET_EDITOR_HEAD_FONT_SIZE, QFont.Bold))
        title_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        title_label.setAlignment(Qt.AlignHCenter)
        main_layout.addWidget(title_label, alignment=Qt.AlignHCenter)
        # Main content layout
        main_layout.addLayout(main_layout)

        # --- Top row: set name entry and buttons ---
        top_row = QHBoxLayout()
        name_label = QLabel("Set Name")
        name_label.setFont(QFont(FONT_FAMILY, SET_EDITOR_LABEL_FONT_SIZE, QFont.Bold))
        name_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        top_row.addWidget(name_label)
        self.name_edit = NeumorphicEntry()
        self.name_edit.setFixedWidth(256)
        entry_font = self.name_edit.font()
        entry_font.setPointSize(SET_EDITOR_LABEL_FONT_SIZE)
        self.name_edit.setFont(entry_font)
        top_row.addWidget(self.name_edit)
        self.create_btn = NeumorphicButton("Create Set")
        self.create_btn.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.create_btn.setMaximumHeight(BUTTON_MIN_HEIGHT)
        self.create_btn.setMinimumWidth(140)
        self.create_btn.setMaximumWidth(180)
        font = self.create_btn.font()
        font.setPointSize(SET_EDITOR_CONTROL_BUTTON_FONT_SIZE)
        self.create_btn.setFont(font)
        self.create_btn.clicked.connect(self.create_set)
        top_row.addWidget(self.create_btn)
        self.add_to_set_btn = NeumorphicButton("Add Problems to Set")
        self.add_to_set_btn.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.add_to_set_btn.setMaximumHeight(BUTTON_MIN_HEIGHT)
        self.add_to_set_btn.setMinimumWidth(180)
        self.add_to_set_btn.setMaximumWidth(220)
        font = self.add_to_set_btn.font()
        font.setPointSize(SET_EDITOR_CONTROL_BUTTON_FONT_SIZE)
        self.add_to_set_btn.setFont(font)
        self.add_to_set_btn.clicked.connect(self.on_add_selected_problem_to_set)
        top_row.addWidget(self.add_to_set_btn)
        self.delete_btn = NeumorphicButton("Delete Selected Set")
        self.delete_btn.setMinimumHeight(BUTTON_MIN_HEIGHT)
        self.delete_btn.setMaximumHeight(BUTTON_MIN_HEIGHT)
        self.delete_btn.setMinimumWidth(180)
        self.delete_btn.setMaximumWidth(220)
        font = self.delete_btn.font()
        font.setPointSize(SET_EDITOR_CONTROL_BUTTON_FONT_SIZE)
        self.delete_btn.setFont(font)
        self.delete_btn.clicked.connect(self.delete_selected_set)
        top_row.addWidget(self.delete_btn)
        top_row.addStretch(1)
        main_layout.addLayout(top_row)

        # --- Set grid: full width below top row ---
        self.set_selector_grid = SetSelectorGridQt()
        # Set height for 5 rows to match the main set selector
        self.set_selector_grid.setMinimumHeight(250)
        main_layout.addWidget(self.set_selector_grid, stretch=1)
        # Initialize selected_set_id
        self.selected_set_id = None
        
        # Wire up selection logic
        def on_set_selected(set_id, is_selected):
            if is_selected:
                self.selected_set_id = set_id
                print(f"[DEBUG] Set selected: {set_id}")
            else:
                # If deselecting the currently selected set, clear selection
                if self.selected_set_id == set_id:
                    self.selected_set_id = None
                    print(f"[DEBUG] Set deselected: {set_id}")
        self.set_selector_grid.set_selected.connect(on_set_selected)

    def create_set(self):
        name = self.name_edit.text().strip()
        if not name:
            warning_box = QMessageBox(self)
            warning_box.setWindowTitle("Create Set")
            warning_box.setText("Set name cannot be empty.")
            warning_box.setIcon(QMessageBox.Warning)
            warning_box.setStyleSheet("""
                QMessageBox { 
                    background-color: #f0f0f3; 
                    color: #031282; 
                    font-size: 14px;
                }
                QLabel { 
                    color: #031282; 
                    font-size: 14px;
                    padding: 10px;
                }
                QPushButton { 
                    color: #031282; 
                    background-color: #e0e0e0; 
                    border: 1px solid #cccccc;
                    padding: 5px 15px;
                    font-size: 12px;
                    min-width: 60px;
                }
            """)
            warning_box.exec_()
            return
        db = ProblemSetDB()
        try:
            db.cur.execute("INSERT INTO problem_sets (name) VALUES (?)", (name,))
            db.conn.commit()
            self.name_edit.clear()
            self.refresh_sets()
        except Exception as e:
            error_box = QMessageBox(self)
            error_box.setWindowTitle("Create Set")
            error_box.setText(f"Could not create set: {e}")
            error_box.setIcon(QMessageBox.Critical)
            error_box.setStyleSheet("""
                QMessageBox { 
                    background-color: #f0f0f3; 
                    color: #031282; 
                    font-size: 14px;
                }
                QLabel { 
                    color: #031282; 
                    font-size: 14px;
                    padding: 10px;
                }
                QPushButton { 
                    color: #031282; 
                    background-color: #e0e0e0; 
                    border: 1px solid #cccccc;
                    padding: 5px 15px;
                    font-size: 12px;
                    min-width: 60px;
                }
            """)
            error_box.exec_()
        db.close()

    def refresh_sets(self):
        self.set_selector_grid.refresh_sets()

    def delete_selected_set(self):
        selected_id = self.get_selected_set_id()
        if not selected_id:
            warning_box = QMessageBox(self)
            warning_box.setWindowTitle("Delete Set")
            warning_box.setText("No set selected for deletion.")
            warning_box.setIcon(QMessageBox.Warning)
            warning_box.setStyleSheet("""
                QMessageBox { 
                    background-color: #f0f0f3; 
                    color: #031282; 
                    font-size: 14px;
                }
                QLabel { 
                    color: #031282; 
                    font-size: 14px;
                    padding: 10px;
                }
                QPushButton { 
                    color: #031282; 
                    background-color: #e0e0e0; 
                    border: 1px solid #cccccc;
                    padding: 5px 15px;
                    font-size: 12px;
                    min-width: 60px;
                }
            """)
            warning_box.exec_()
            return
        
        print(f"[DEBUG] Selected set ID for deletion: {selected_id}")
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Delete Set")
        msg_box.setText("Are you sure you want to delete the selected set? This cannot be undone.")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setStyleSheet("""
            QMessageBox { 
                background-color: #f0f0f3; 
                color: #031282; 
                font-size: 14px;
            }
            QLabel { 
                color: #031282; 
                font-size: 14px;
                padding: 10px;
            }
            QPushButton { 
                color: #031282; 
                background-color: #e0e0e0; 
                border: 1px solid #cccccc;
                padding: 5px 15px;
                font-size: 12px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #d0d0d3;
            }
            QPushButton:pressed {
                background-color: #c0c0c3;
            }
        """)
        reply = msg_box.exec_()
        if reply != QMessageBox.Yes:
            return
        
        try:
            db = ProblemSetDB()
            print(f"[DEBUG] About to delete set_id: {selected_id}")
            db.delete_set(selected_id)
            db.close()
            print(f"[DEBUG] Successfully deleted set_id: {selected_id}")
            
            # Clear the selection after deletion
            self.set_selector_grid.clear_selection()
            self.selected_set_id = None
            
            # Refresh the grid
            self.refresh_sets()
        except Exception as e:
            print(f"[DEBUG] Error deleting set: {e}")
            error_box = QMessageBox(self)
            error_box.setWindowTitle("Delete Set")
            error_box.setText(f"Error deleting set: {str(e)}")
            error_box.setIcon(QMessageBox.Critical)
            error_box.setStyleSheet("""
                QMessageBox { 
                    background-color: #f0f0f3; 
                    color: #031282; 
                    font-size: 14px;
                }
                QLabel { 
                    color: #031282; 
                    font-size: 14px;
                    padding: 10px;
                }
                QPushButton { 
                    color: #031282; 
                    background-color: #e0e0e0; 
                    border: 1px solid #cccccc;
                    padding: 5px 15px;
                    font-size: 12px;
                    min-width: 60px;
                }
            """)
            error_box.exec_()
            if 'db' in locals():
                db.close()

    def on_add_selected_problem_to_set(self):
        parent = self.parent()
        if parent and hasattr(parent, 'problem_display_panel'):
            selected_problems = parent.problem_display_panel.get_selected_problems()
        else:
            selected_problems = []
        selected_set_id = self.get_selected_set_id()
        print("[DEBUG] on_add_selected_problem_to_set: selected_set_id:", selected_set_id)
        self.add_selected_problems_to_set.emit(selected_problems, selected_set_id)

    def get_selected_set_id(self):
        # Use the tracked selected_set_id, but also check the grid for consistency
        grid_selected = self.set_selector_grid.get_selected_sets()
        
        print(f"[DEBUG] get_selected_set_id: tracked={self.selected_set_id}, grid_selected={grid_selected}")
        
        if self.selected_set_id is not None and self.selected_set_id in grid_selected:
            return self.selected_set_id
        elif grid_selected:
            # Update our tracking if grid has selection but we don't
            self.selected_set_id = grid_selected[0]
            return self.selected_set_id
        else:
            return None 