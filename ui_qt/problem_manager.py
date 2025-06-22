# problem_manager.py

from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QSpacerItem, QSizePolicy, QMessageBox, QLabel, QTextEdit, QDialog
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont
from ui_qt.query_panel import QueryPanel
from ui_qt.problem_display_panel import ProblemDisplayPanel
from ui_qt.set_editor_panel import SetEditorPanelQt
from ui_qt.neumorphic_components import NeumorphicButton
from ui_qt.style_config import CONTROL_BTN_WIDTH, FONT_FAMILY, SECTION_LABEL_FONT_SIZE, CONTROL_BTN_FONT_SIZE, BUTTON_FONT_SIZE, BUTTON_TEXT_PADDING, SPACING
from ui_qt.export_selected_dialog import ExportSelectedDialog
from ui_qt.export_set_dialog import ExportSetDialog
from ui_qt.display_config_dialog import DisplayConfigDialog

def show_styled_message(parent, title, message, msg_type="info"):
    """Show a styled message box"""
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if msg_type == "info":
        msg_box.setIcon(QMessageBox.Information)
    elif msg_type == "warning":
        msg_box.setIcon(QMessageBox.Warning)
    elif msg_type == "error":
        msg_box.setIcon(QMessageBox.Critical)
    
    # Apply styling to ensure readability
    msg_box.setStyleSheet("""
        QMessageBox {
            background-color: #f0f0f3;
            color: #2b2d42;
        }
        QMessageBox QLabel {
            color: #2b2d42;
            font-family: 'Segoe UI';
            font-size: 12pt;
        }
        QMessageBox QPushButton {
            background-color: #e0e0e3;
            color: #2b2d42;
            border: 1px solid #b0b0b3;
            border-radius: 4px;
            padding: 5px 15px;
            font-family: 'Segoe UI';
            font-size: 11pt;
            min-width: 60px;
        }
        QMessageBox QPushButton:hover {
            background-color: #d0d0d3;
        }
    """)
    
    msg_box.exec_()

class ProblemManager(QWidget):
    return_to_editor = pyqtSignal()

    def __init__(self, parent=None, laptop_mode=False):
        super().__init__(parent)
        print("[DEBUG] ProblemManager __init__ called:", self)
        main_layout = QVBoxLayout(self)
        # Main content layout
        content_layout = QHBoxLayout()
        # --- Left side: query panel ---
        left_panel_widget = QWidget()
        left_vbox = QVBoxLayout(left_panel_widget)
        left_panel_widget.setStyleSheet('background: transparent;')
        # Create return button but don't add it here - we'll pass it to QueryPanel
        self.return_btn = NeumorphicButton("Return to Editor", self)
        self.return_btn.clicked.connect(self.return_to_editor)
        self.query_panel = QueryPanel(laptop_mode=laptop_mode, show_preview_and_nav_buttons=False, return_button=self.return_btn)
        left_vbox.addWidget(self.query_panel, stretch=1)
        # Remove SetEditorPanelQt and Add-to-Set button from here
        # Add-to-Set logic will be handled in SetEditorPanelQt
        # If using a QWidget for the left panel, set its background to transparent for debugging
        # If not, set the background of the parent widget of left_vbox to transparent
        # Example (if left_panel_widget exists):
        # left_panel_widget.setStyleSheet('background: transparent;')
        content_layout.addWidget(left_panel_widget, stretch=2)  # 40%
        # --- Right side: Problem display with export buttons ---
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(SPACING)
        
        # Export buttons row
        export_buttons_layout = QHBoxLayout()
        export_buttons_layout.setSpacing(SPACING)
        
        self.export_selected_btn = NeumorphicButton("Export Selected to LaTeX", font_size=BUTTON_FONT_SIZE)
        self.export_set_btn = NeumorphicButton("Export Set to LaTeX", font_size=BUTTON_FONT_SIZE)
        self.display_config_btn = NeumorphicButton("Display Configuration", font_size=BUTTON_FONT_SIZE)
        
        # Set button widths based on text
        for btn in [self.export_selected_btn, self.export_set_btn, self.display_config_btn]:
            fm = btn.fontMetrics()
            text_width = fm.horizontalAdvance(btn.text()) if hasattr(fm, 'horizontalAdvance') else fm.width(btn.text())
            btn.setFixedWidth(text_width + (BUTTON_TEXT_PADDING * 2))
        
        export_buttons_layout.addWidget(self.export_selected_btn)
        export_buttons_layout.addWidget(self.export_set_btn)
        export_buttons_layout.addStretch()
        export_buttons_layout.addWidget(self.display_config_btn)
        
        right_layout.addLayout(export_buttons_layout)
        
        # Problem display panel
        self.problem_display_panel = ProblemDisplayPanel()
        right_layout.addWidget(self.problem_display_panel)
        content_layout.addWidget(right_panel, stretch=3)
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
        self.query_panel.query_clicked.connect(self.on_query)
        # Connect query results to display panel
        self.query_panel.query_executed.connect(self.problem_display_panel.set_problems)
        # Connect reset to clear the grid
        self.query_panel.reset_clicked.connect(lambda: self.problem_display_panel.set_problems([]))
        # Connect edit panel signals
        self.query_panel.apply_attributes_to_selected.connect(self.on_apply_attributes)
        self.query_panel.clear_attributes_from_selected.connect(self.on_clear_attributes)
        # --- Centralized selection state ---
        self.selected_problem_ids = set()
        self.selected_set_ids = set()
        print(f"-------------------->set():{set()}")
        self.problem_display_panel.selection_changed.connect(self.on_problems_selected)
        
        # Connect export buttons
        self.export_selected_btn.clicked.connect(self.show_export_selected_dialog)
        self.export_set_btn.clicked.connect(self.show_export_set_dialog)
        self.display_config_btn.clicked.connect(self.show_display_config_dialog)

    def get_selected_problem_ids(self):
        return [p.get('problem_id') for p in self.problem_display_panel.get_selected_problems()]

    def debug_print_size_hints(self):
        print("[DEBUG] ProblemManager minimumSizeHint:", self.minimumSizeHint())
        print("[DEBUG] ProblemManager sizeHint:", self.sizeHint())
        print("[DEBUG] QueryPanel minimumSizeHint:", self.query_panel.minimumSizeHint())
        print("[DEBUG] QueryPanel sizeHint:", self.query_panel.sizeHint())
        print("[DEBUG] ProblemDisplayPanel minimumSizeHint:", self.problem_display_panel.minimumSizeHint())
        print("[DEBUG] ProblemDisplayPanel sizeHint:", self.problem_display_panel.sizeHint())
        if hasattr(self.query_panel, 'problem_set_panel'):
            print("[DEBUG] ProblemSetPanel minimumSizeHint:", self.query_panel.problem_set_panel.minimumSizeHint())
            print("[DEBUG] ProblemSetPanel sizeHint:", self.query_panel.problem_set_panel.sizeHint())

    def on_query(self):
        criteria = self.query_panel.query_inputs_panel.build_query_criteria()
        print(f"[DEBUG] Query criteria: {criteria}")
        selected_set_ids = self.query_panel.query_inputs_panel.get_selected_set_ids()
        selected_set_id = selected_set_ids[0] if selected_set_ids else None
        from db.math_db import MathProblemDB
        db = MathProblemDB()
        # If a set is selected, get only problems in that set; else get all
        if selected_set_id:
            problems = db.list_problems_in_set(selected_set_id)
            # list_problems_in_set may return an error string if it fails
            if not isinstance(problems, list):
                print("[ERROR] list_problems_in_set failed:", problems)
                problems = []
        else:
            success, problems = db.get_problems_list(limit=10000)
            if not success:
                print("[ERROR] get_problems_list failed:", problems)
                problems = []
        db.close()
        print(f"[DEBUG] Total problems before filtering: {len(problems)}")
        # Filter by Problem ID
        problem_id = criteria.get('problem_id', '').strip()
        if problem_id:
            problems = [p for p in problems if str(p.get('problem_id', '')) == problem_id]
        # Filter by Earmarks
        earmark_ids = criteria.get('earmark_ids', [])
        if earmark_ids:
            problems = [p for p in problems if any(e['earmark_id'] in earmark_ids for e in p.get('earmarks', []))]
        # Filter by Problem Types
        selected_type_ids = criteria.get('type_ids', [])
        if selected_type_ids:
            print(f"[DEBUG] Filtering by type_ids: {selected_type_ids}")
            problems = [p for p in problems if any(t['type_id'] in selected_type_ids for t in p.get('types', []))]
            print(f"[DEBUG] Problems after type filtering: {len(problems)}")
        # Filter by Categories
        selected_categories = criteria.get('categories', [])
        if selected_categories:
            selected_cat_names = {cat['name'] for cat in selected_categories}
            problems = [p for p in problems if selected_cat_names.issubset({c['name'] for c in p.get('categories', [])})]
        self.problem_display_panel.set_problems(problems)
        # Also update query panel's export panel with the results
        self.query_panel.set_query_results(problems)

    def on_problems_selected(self, ids):
        print("[DEBUG] on_problems_selected:", ids)
        self.selected_problem_ids = set(ids)

    def on_sets_selected(self, ids):
        print("[DEBUG] on_sets_selected:", ids)
        self.selected_set_ids = set(ids)
    
    def on_apply_attributes(self, attributes):
        """Apply attributes to selected problems"""
        selected_ids = self.get_selected_problem_ids()
        if not selected_ids:
            show_styled_message(self, "No Selection", "Please select problems to apply attributes to.", "warning")
            return
        
        from db.math_db import MathProblemDB
        db = MathProblemDB()
        
        success_count = 0
        for problem_id in selected_ids:
            try:
                # Apply earmarks if specified
                if 'earmark_ids' in attributes:
                    for earmark_id in attributes['earmark_ids']:
                        db.cur.execute("""
                            INSERT OR IGNORE INTO problem_earmarks (problem_id, earmark_id)
                            VALUES (?, ?)
                        """, (problem_id, earmark_id))
                
                # Apply problem types if specified
                if 'type_ids' in attributes:
                    # First, add any new types
                    for type_id in attributes['type_ids']:
                        db.cur.execute("""
                            INSERT OR IGNORE INTO problem_problem_types (problem_id, type_id)
                            VALUES (?, ?)
                        """, (problem_id, type_id))
                
                # Apply categories if specified
                if 'categories' in attributes:
                    # First, add any new categories
                    for category in attributes['categories']:
                        db.cur.execute("""
                            INSERT OR IGNORE INTO problem_math_categories (problem_id, category_id)
                            VALUES (?, ?)
                        """, (problem_id, category['category_id']))
                
                success_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to apply attributes to problem {problem_id}: {e}")
        
        db.conn.commit()
        db.close()
        
        show_styled_message(self, "Success", f"Attributes applied to {success_count} problems.", "info")
        # Refresh only the selected problems in the current display
        self._refresh_selected_problems(selected_ids)
    
    def on_clear_attributes(self, attributes):
        """Clear attributes from selected problems"""
        selected_ids = self.get_selected_problem_ids()
        if not selected_ids:
            show_styled_message(self, "No Selection", "Please select problems to clear attributes from.", "warning")
            return
        
        from db.math_db import MathProblemDB
        db = MathProblemDB()
        
        success_count = 0
        for problem_id in selected_ids:
            try:
                # Clear earmarks if specified
                if 'earmark_ids' in attributes:
                    for earmark_id in attributes['earmark_ids']:
                        db.cur.execute("""
                            DELETE FROM problem_earmarks 
                            WHERE problem_id = ? AND earmark_id = ?
                        """, (problem_id, earmark_id))
                
                # Clear problem types if specified
                if 'type_ids' in attributes:
                    for type_id in attributes['type_ids']:
                        db.cur.execute("""
                            DELETE FROM problem_problem_types 
                            WHERE problem_id = ? AND type_id = ?
                        """, (problem_id, type_id))
                
                # Clear categories if specified
                if 'categories' in attributes:
                    for category in attributes['categories']:
                        db.cur.execute("""
                            DELETE FROM problem_math_categories 
                            WHERE problem_id = ? AND category_id = ?
                        """, (problem_id, category['category_id']))
                
                success_count += 1
            except Exception as e:
                print(f"[ERROR] Failed to clear attributes from problem {problem_id}: {e}")
        
        db.conn.commit()
        db.close()
        
        show_styled_message(self, "Success", f"Attributes cleared from {success_count} problems.", "info")
        # Refresh only the selected problems in the current display
        self._refresh_selected_problems(selected_ids)
    
    def on_export_completed(self, output_path):
        """Handle export completion"""
        # The export panel already shows a success message, so we don't need another one here
        pass
    
    def show_export_selected_dialog(self):
        """Show the export selected problems dialog"""
        # Get the problems from the last query (stored in query panel)
        current_problems = self.query_panel.selected_problems
        
        if not current_problems:
            show_styled_message(self, "No Problems", "No problems available to export. Please run a query first.", "warning")
            return
        
        # Create and show the dialog
        dialog = ExportSelectedDialog(self, current_problems)
        dialog.export_completed.connect(self.on_export_completed)
        dialog.exec_()
    
    def show_export_set_dialog(self):
        """Show the export set dialog"""
        # Get selected sets from the query inputs panel
        selected_sets = self.query_panel.query_inputs_panel.get_selected_set_ids()
        
        if not selected_sets:
            show_styled_message(self, "No Set Selected", "Please select exactly one set to export.", "warning")
            return
        
        if len(selected_sets) > 1:
            show_styled_message(self, "Multiple Sets Selected", "Please select exactly one set to export.", "warning")
            return
        
        # Get the selected set's details
        set_id = selected_sets[0]
        
        # Get set name from the database
        from db.problem_set_db import ProblemSetDB
        set_db = ProblemSetDB()
        sets = set_db.get_all_sets()
        set_db.close()
        
        set_name = None
        for s in sets:
            # s is a tuple: (set_id, name, description, is_ordered)
            if s[0] == set_id:
                set_name = s[1]
                break
        
        if not set_name:
            show_styled_message(self, "Set Not Found", "Could not find the selected set.", "error")
            return
        
        # Create and show the dialog
        dialog = ExportSetDialog(self, set_id=set_id, set_name=set_name)
        dialog.export_completed.connect(self.on_export_completed)
        dialog.exec_()
    
    def _refresh_selected_problems(self, problem_ids):
        """Refresh only the selected problems in the current display"""
        if not problem_ids:
            return
            
        # Get fresh data for the selected problems
        from db.math_db import MathProblemDB
        db = MathProblemDB()
        
        # Get current problems list from query panel
        current_problems = self.query_panel.selected_problems
        if not current_problems:
            db.close()
            return
        
        # Create a map of problem_id to index for quick lookup
        problem_map = {p['problem_id']: i for i, p in enumerate(current_problems)}
        
        # Update each selected problem with fresh data
        for problem_id in problem_ids:
            if problem_id in problem_map:
                # Get fresh problem data with all attributes
                success, fresh_data = db.get_problem(problem_id, with_images=True, with_categories=True)
                if success and fresh_data:
                    # Also get earmarks and types
                    earmarks_success, earmarks = db.get_earmarks_for_problem(problem_id)
                    if earmarks_success:
                        fresh_data['earmarks'] = earmarks
                    
                    types_success, types = db.get_types_for_problem(problem_id)
                    if types_success:
                        fresh_data['types'] = types
                    # Update the problem in the list
                    idx = problem_map[problem_id]
                    current_problems[idx] = fresh_data
        
        db.close()
        
        # Update the display with the refreshed problems
        self.problem_display_panel.set_problems(current_problems)
        # Also update query panel's reference
        self.query_panel.set_query_results(current_problems)
    
    def show_display_config_dialog(self):
        """Show the display configuration dialog"""
        # Get current font size from display panel
        current_font_size = self.problem_display_panel.current_font_size
        
        # Create and show the dialog
        dialog = DisplayConfigDialog(current_font_size=current_font_size, parent=self)
        
        # Connect the config_changed signal to save the configuration
        dialog.config_changed.connect(self._on_display_config_save)
        
        # If OK is clicked, apply the configuration
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_config()
            self.problem_display_panel.set_config(config)
    
    def _on_display_config_save(self, config):
        """Handle saving the display configuration"""
        # Save to the problem display panel's config file
        if 'font_size' in config:
            self.problem_display_panel.save_font_size(config['font_size'])
        