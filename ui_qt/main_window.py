"""
Main PyQt5 window for the Simplified Math Editor (migration skeleton).
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMenuBar, QAction, QFileDialog, QMessageBox, QPushButton, QVBoxLayout, QDialog, QToolBar, QStackedWidget
from ui_qt.left_panel import LeftPanel
from ui_qt.editor_panel import EditorPanel
from ui_qt.preview_panel import PreviewPanel
from db.math_db import MathProblemDB
from managers.file_manager_qt import FileManager
from managers.image_manager_qt import ImageManagerQt
from managers.image_manager_qt import ImageDetailsDialog
from ui_qt.image_dialog import ImageSizeAdjustDialog
import re
from pathlib import Path
import os
from converters.image_converter import ImageConverter
from ui_qt.style_config import active_palette, MultiShadowButton, WINDOW_BG_COLOR, FONT_FAMILY, BUTTON_FONT_SIZE, LABEL_FONT_SIZE, NOTES_FONT_SIZE
print(f"---------------WINDOW_BG_COLOR: {WINDOW_BG_COLOR}")
from PyQt5.QtGui import QFont
from ui_qt.problem_manager import ProblemManager
from ui_qt.problem_display_panel import ProblemDisplayPanel
from PyQt5.QtCore import Qt
from managers.config_manager import ConfigManager
from ui_qt.set_panel import SetPanelQt

def update_problem_image_map(problem_id, content, db):
    # Remove old mappings
    db.cur.execute("DELETE FROM problem_image_map WHERE problem_id = ?", (problem_id,))
    # Extract image names from content
    image_names = re.findall(r'\\includegraphics(?:\\[.*?\\])?\\{([^\\}]+)\\}', content)
    for image_name in image_names:
        db.cur.execute(
            "INSERT INTO problem_image_map (problem_id, image_name) VALUES (?, ?)",
            (problem_id, image_name)
        )

class MainWindow(QMainWindow):
    def __init__(self, laptop_mode=False):
        super().__init__()
        self.setWindowTitle("Simplified Math Editor (PyQt5)")
        self.setGeometry(100, 100, 1200, 800)
        self.config_manager = ConfigManager(config_file="default_config.json")

        # Initialize file manager
        self.file_manager = FileManager(self)

        # Initialize image manager (for Tkinter dialog compatibility)
        self.image_manager = ImageManagerQt(self)

        # Initialize image converter
        self.image_converter = ImageConverter()

        # Menu bar
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("File")

        new_action = QAction("New", self)
        new_action.triggered.connect(self.file_manager.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.file_manager.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.file_manager.save_file)
        file_menu.addAction(save_action)

        saveas_action = QAction("Save As...", self)
        saveas_action.triggered.connect(self.file_manager.save_as)
        file_menu.addAction(saveas_action)

        export_action = QAction("Export to PDF...", self)
        export_action.triggered.connect(self.file_manager.export_to_pdf)
        file_menu.addAction(export_action)

        self.setMenuBar(menubar)

        # Central widget and layout
        self.stacked_widget = QStackedWidget(self)
        self.setCentralWidget(self.stacked_widget)
        # --- Main Editor UI ---
        self.editor_container = QWidget(self)
        editor_layout = QHBoxLayout(self.editor_container)
        self.left_panel = LeftPanel(laptop_mode=laptop_mode)
        if not laptop_mode:
            self.left_panel.setFixedWidth(780)
        editor_layout.addWidget(self.left_panel)
        self.left_panel.query_panel.query_clicked.connect(self.on_query)
        self.left_panel.query_panel.next_match_button.clicked.connect(self.show_next_problem)
        self.left_panel.query_panel.prev_match_button.clicked.connect(self.show_previous_problem)
        self.left_panel.preview_button.clicked.connect(self.update_preview)
        self.left_panel.query_panel.reset_button.clicked.connect(self.reset_fields)
        self.left_panel.query_panel.browse_all_button.clicked.connect(self.browse_all_problems)
        # Add Problem Browser 2 screen
        self.problem_manager_screen = ProblemManager(laptop_mode=laptop_mode)
        self.stacked_widget.addWidget(self.problem_manager_screen)
        self.left_panel.problem_browser2_button.clicked.connect(self.show_problem_manager_screen)
        # Connect return_to_editor signal
        self.problem_manager_screen.return_to_editor.connect(self.show_editor_screen)
        self.problem_db = MathProblemDB()
        self.editor_panel = EditorPanel()
        editor_vlayout = QVBoxLayout()
        editor_vlayout.addWidget(self.editor_panel)
        nav_layout = QHBoxLayout()
        delete_btn = MultiShadowButton("Delete Problem", active_palette)
        delete_btn.setMinimumWidth(180)
        delete_btn.setMaximumWidth(180)
        delete_btn.setMinimumHeight(36)
        delete_btn.setMaximumHeight(36)
        delete_btn.setStyleSheet(delete_btn.styleSheet() + "font-size: 13px;")
        delete_btn.clicked.connect(self.delete_current_problem)
        delete_btn.setFont(QFont(FONT_FAMILY, BUTTON_FONT_SIZE, QFont.Bold))
        nav_layout.addWidget(delete_btn)
        editor_vlayout.addLayout(nav_layout)
        editor_panel_container = QWidget()
        editor_panel_container.setLayout(editor_vlayout)
        editor_layout.addWidget(editor_panel_container, stretch=2)
        self.preview_panel = PreviewPanel(config_manager=self.config_manager)
        editor_layout.addWidget(self.preview_panel, stretch=3)
        self.preview_panel.set_main_window(self)
        self.current_results = []
        self.current_result_index = -1
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        self.stacked_widget.addWidget(self.editor_container)
        # Show editor by default
        self.stacked_widget.setCurrentWidget(self.editor_container)
        self.menuBar().setVisible(True)

    def update_preview(self):
        """Update the preview with current editor content, ensuring all images are available for LaTeX."""
        text = self.editor_panel.text_edit.toPlainText()
        # --- Ensure all images referenced in LaTeX are present in temp/images ---
        image_pattern = r'\\includegraphics(?:\[.*?\])?\{([^{}]+)\}'
        image_filenames = set(re.findall(image_pattern, text))
        image_dir = os.path.join(os.getcwd(), "temp", "images")
        os.makedirs(image_dir, exist_ok=True)
        for filename in image_filenames:
            image_path = os.path.join(image_dir, filename)
            if not os.path.exists(image_path):
                # Try to export from database
                success, result = self.image_manager.image_db.export_to_file(filename, image_path)
                if not success:
                    QMessageBox.critical(self, "Image Error", f"Could not extract image '{filename}' from database: {result}")
                    self.status_bar.showMessage(f"Image missing: {filename}")
                    return  # Abort preview if any image is missing
        # --- Proceed with preview ---
        self.preview_panel.update_preview(text)
        self.status_bar.showMessage("Preview updated")

    def on_query(self):
        selected_set_ids = self.left_panel.query_panel.query_inputs_panel.get_selected_set_ids()
        selected_set_id = selected_set_ids[0] if selected_set_ids else None
        problem_id = self.left_panel.get_problem_id().strip()
        earmark_filter = self.left_panel.get_earmark()
        if selected_set_id:
            problems = self.problem_db.list_problems_in_set(selected_set_id)
        else:
            problems = self.problem_db.get_problems_list(limit=1000000)[1]
        if problem_id:
            for p in problems:
                if str(p.get("problem_id", "")) == problem_id:
                    self.current_results = [p]
                    self.current_result_index = 0
                    self.load_problem_into_ui(p)
                    return
            QMessageBox.information(self, "Query", f"No problem found with ID {problem_id}")
            self.current_results = []
            self.current_result_index = -1
            return
        search_text = self.left_panel.get_search_text().strip().lower()
        selected_cats = {cat["name"] for cat in self.left_panel.category_panel.get_selected_categories()}
        results = []
        for p in problems:
            if search_text and search_text not in (p.get('content','').lower()) and search_text not in (p.get('title','').lower()):
                continue
            problem_cat_names = {c["name"] for c in p.get('categories', [])}
            if selected_cats and not selected_cats.issubset(problem_cat_names):
                continue
            if earmark_filter and not p.get('earmark', 0):
                continue
            results.append(p)
        if not results:
            self.current_results = []
            self.current_result_index = -1
        else:
            self.current_results = results
            self.current_result_index = 0
            self.load_problem_into_ui(self.current_results[0])

    def load_problem_into_ui(self, problem):
        self.editor_panel.text_edit.setPlainText(problem.get("content", ""))
        self.left_panel.set_problem_id(str(problem.get("problem_id", "")))
        self.left_panel.set_answer(problem.get("answer", ""))
        self.left_panel.set_notes(problem.get("notes", ""))
        selected_cat_names = {c["name"] for c in problem.get("categories", [])}
        for cat in self.left_panel.category_panel.categories:
            btn = self.left_panel.category_panel.buttons[cat["category_id"]]
            if cat["name"] in selected_cat_names:
                btn.setChecked(True)
                btn.setStyleSheet("background-color: #cce5ff;")
                self.left_panel.category_panel.selected.add(cat["category_id"])
            else:
                btn.setChecked(False)
                btn.setStyleSheet("")
                self.left_panel.category_panel.selected.discard(cat["category_id"])
        # Load problem types
        problem_id = problem.get("id", None)
        if problem_id:
            db = MathProblemDB(self.problem_db.db_path)
            success, types = db.get_types_for_problem(problem_id)
            if success:
                self.left_panel.set_selected_type_ids([t["type_id"] for t in types])
            else:
                self.left_panel.set_selected_type_ids([])
            db.close()
        else:
            self.left_panel.set_selected_type_ids([])
        self.left_panel.set_earmark(problem.get("earmark", 0))
        self.update_preview()

    def show_next_problem(self):
        if not self.current_results:
            return
        self.current_result_index = (self.current_result_index + 1) % len(self.current_results)
        self.load_problem_into_ui(self.current_results[self.current_result_index])

    def show_previous_problem(self):
        if not self.current_results:
            return
        self.current_result_index = (self.current_result_index - 1) % len(self.current_results)
        self.load_problem_into_ui(self.current_results[self.current_result_index])

    def showEvent(self, event):
        super().showEvent(event)
        # Find the actual SetPanelQt instance in the UI
        set_panels = self.findChildren(SetPanelQt)
        if set_panels:
            self.set_panel = set_panels[0]
            print("[DEBUG] Using SetPanelQt instance for all logic:", self.set_panel)
        # Remove callback setting on SetPanelQt
        # If needed, connect the new signal here:
        if set_panels:
            set_panel = set_panels[0]
            set_panel.request_selected_problem_ids.connect(self.on_add_selected_problems_to_sets)
        self.showMaximized()

    def adjust_image_size(self):
        """Show dialog to adjust image size (PyQt5 version)"""
        try:
            # Get current editor content
            content = self.editor_panel.text_edit.toPlainText()
            # Find the image at cursor position
            cursor = self.editor_panel.text_edit.textCursor()
            position = cursor.position()
            image_pattern = r'\\includegraphics(?:\[.*?\])?\{([^{}]+)\}'
            matches = list(re.finditer(image_pattern, content))
            if not matches:
                QMessageBox.information(self, "No Image", "No image found at cursor position.")
                return
            # Find the closest image to cursor
            closest_match = min(matches, key=lambda m: abs(m.start() - position))
            image_filename = closest_match.group(1)
            width, left, top, bottom, align = self.parse_latex_settings(content, image_filename)
            # Prepare image_info dict
            image_info = {
                'filename': image_filename,
                'width': int(width * 800),  # assuming 800px as base width for 1.0
                'height': int(width * 600), # estimate, or fetch actual if available
                'original_width': int(width * 800),
                'original_height': int(width * 600),
                'caption': '',
                'label': f'fig:{Path(image_filename).stem}',
                'latex_width': width,
            }
            # Extract current LaTeX height (in cm) from LaTeX code if possible
            height_cm = 6.0
            adjustbox_pattern = r'\\adjustbox\{([^}]*)\}.*?\\includegraphics.*?\{' + re.escape(image_filename) + r'\}'
            match = re.search(adjustbox_pattern, content)
            if match:
                opts = match.group(1)
                height_match = re.search(r'height=([0-9.]+)cm', opts)
                if height_match:
                    try:
                        height_cm = float(height_match.group(1))
                    except Exception:
                        height_cm = 6.0
            # Construct full image path
            image_dir = os.path.join(os.getcwd(), "temp", "images")
            image_path = os.path.join(image_dir, image_filename)
            if not os.path.exists(image_path):
                image_path = image_filename
            # Define the apply callback
            def apply_callback(height_cm):
                margin_vals = dialog.get_margin_values()
                new_content = self._update_latex_image_margins_and_height(
                    content, image_filename, height_cm,
                    margin_left=margin_vals['left'],
                    margin_bottom=margin_vals['bottom'],
                    margin_top=margin_vals['top']
                )
                self.editor_panel.text_edit.setPlainText(new_content)
                self.update_preview()

            # Show adjustment dialog, passing margin values
            dialog = ImageSizeAdjustDialog(
                self,
                image_path=image_path,
                current_height_cm=height_cm,
                apply_callback=apply_callback,
                margin_top=top,
                margin_left=left,
                margin_bottom=bottom
            )
            if dialog.exec_() == QDialog.Accepted:
                height_cm = dialog.get_result()
                if height_cm:
                    margin_vals = dialog.get_margin_values()
                    new_content = self._update_latex_image_margins_and_height(
                        content, image_filename, height_cm,
                        margin_left=margin_vals['left'],
                        margin_bottom=margin_vals['bottom'],
                        margin_top=margin_vals['top']
                    )
                    self.editor_panel.text_edit.setPlainText(new_content)
                    self.update_preview()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to adjust image: {str(e)}")
    
    def parse_latex_settings(self, content, filename):
        """Parse LaTeX code to extract width, margin, and alignment for an image"""
        pattern = r'\\adjustbox\{([^}]*)\}\{\\includegraphics\[.*?\]\{' + re.escape(filename) + r'\}\}'
        match = re.search(pattern, content)
        width = 0.8
        left = top = bottom = 0.0
        align = 'left'
        if match:
            opts = match.group(1)
            # Parse width
            width_match = re.search(r'width=([0-9.]+)\\textwidth', opts)
            if width_match:
                try:
                    width = float(width_match.group(1))
                except Exception:
                    width = 0.8
            # Parse margin
            margin_match = re.search(r'margin=([^,}]+)', opts)
            if margin_match:
                margin_str = margin_match.group(1)
                parts = margin_str.split()
                if len(parts) == 4:
                    try:
                        left = float(parts[0].replace('cm', ''))
                        bottom = float(parts[1].replace('cm', ''))
                        # right = float(parts[2].replace('cm', ''))  # ignored
                        top = float(parts[3].replace('cm', ''))
                    except Exception:
                        left = top = bottom = 0.0
            # Parse align
            for a in ['left', 'center', 'right']:
                if a in opts:
                    align = a
                    break
        return width, left, top, bottom, align 

    def _update_latex_image_margins_and_height(self, content, image_filename, height_cm, margin_left, margin_bottom, margin_top):
        """
        Update the height=...cm and margin=... in the adjustbox that directly wraps the includegraphics for the given image.
        """
        import re
        # Pattern to match the adjustbox that wraps the includegraphics for the image
        pattern = (
            r'(\\adjustbox\{[^}]*?)height=[0-9.]+cm([^}]*)margin=([^,}}]+)([^}]*)\}(\{\\includegraphics[^\{]*\{' +
            re.escape(image_filename) + r'\}[^}]*\})'
        )
        def repl(match):
            before = match.group(1)
            between = match.group(2)
            old_margin = match.group(3)
            after_margin = match.group(4)
            rest = match.group(5)
            new_margin = f"{margin_left:.2f}cm {margin_bottom:.2f}cm 0cm {margin_top:.2f}cm"
            return f'{before}height={height_cm:.2f}cm{between}margin={new_margin}{after_margin}}}{rest}'
        new_content, n = re.subn(pattern, repl, content, count=1)
        return new_content if n else content

    def delete_current_problem(self):
        problem_id = self.left_panel.get_problem_id().strip()
        if not problem_id:
            QMessageBox.warning(self, "Delete Problem", "No problem selected.")
            return
        db = MathProblemDB(self.problem_db.db_path)
        success, message = db.delete_problem(int(problem_id))
        if success:
            QMessageBox.information(self, "Delete Problem", message)
            self.show_next_problem()
        else:
            QMessageBox.critical(self, "Delete Problem", message)

    def save_current_problem(self):
        problem_id = self.left_panel.get_problem_id().strip()
        content = self.editor_panel.text_edit.toPlainText()
        answer = self.left_panel.get_answer().strip()
        notes = self.left_panel.get_notes().strip()
        categories = [cat["name"] for cat in self.left_panel.category_panel.get_selected_categories()]
        earmark = 1 if self.left_panel.get_earmark() else 0
        selected_types = self.left_panel.get_selected_type_ids()
        db = MathProblemDB(self.problem_db.db_path)
        try:
            if problem_id:
                # Update problem
                success, msg = db.update_problem(
                    int(problem_id),
                    content=content,
                    answer=answer,
                    notes=notes,
                    earmark=earmark
                )
                if not success:
                    QMessageBox.critical(self, "Save Problem", f"Failed to update problem: {msg}")
                    return
                # Update categories
                db.cur.execute("DELETE FROM problem_math_categories WHERE problem_id=?", (problem_id,))
                for cat_name in categories:
                    db.add_problem_to_category(int(problem_id), cat_name)
                # Update types
                db.cur.execute("DELETE FROM problem_problem_types WHERE problem_id=?", (problem_id,))
                for type_id in selected_types:
                    db.add_problem_to_type(int(problem_id), type_id)
                # Update image mapping
                update_problem_image_map(int(problem_id), content, db)
                db.conn.commit()
                QMessageBox.information(self, "Save Problem", "Problem updated successfully.")
            else:
                # Add new problem
                success, new_id = db.add_problem(
                    content,
                    answer=answer,
                    notes=notes,
                    earmark=earmark,
                    categories=categories
                )
                if not success:
                    QMessageBox.critical(self, "Save Problem", f"Failed to add problem: {new_id}")
                    return
                for type_id in selected_types:
                    db.add_problem_to_type(int(new_id), type_id)
                # Update image mapping
                update_problem_image_map(int(new_id), content, db)
                db.conn.commit()
                self.left_panel.set_problem_id(str(new_id))
                QMessageBox.information(self, "Save Problem", f"New problem added with ID {new_id}.")
        except Exception as e:
            db.conn.rollback()
            QMessageBox.critical(self, "Save Problem", f"Failed to save problem: {e}")
        finally:
            db.close()

    def reset_fields(self):
        self.left_panel.reset_fields()
        self.editor_panel.text_edit.clear()
        self.preview_panel.clear() 

    def show_editor_screen(self):
        self.stacked_widget.setCurrentWidget(self.editor_container)
        self.menuBar().setVisible(True)

    def browse_all_problems(self):
        self.current_results = self.problem_db.get_problems_list(limit=1000000)[1]
        for p in self.current_results:
            p['id'] = p['problem_id']
        self.current_results.sort(key=lambda p: p['id'])
        self.current_result_index = 0
        if self.current_results:
            self.load_problem_into_ui(self.current_results[0])
            self.show_editor_screen()
        else:
            QMessageBox.information(self, "Browse All", "No problems found in the database.")

    def show_problem_manager_screen(self):
        self.stacked_widget.setCurrentWidget(self.problem_manager_screen)
        self.menuBar().setVisible(True)

    def on_add_selected_problems_to_sets(self):
        selected_problems = self.problem_display_panel.get_selected_problems()
        selected_sets = self.set_panel.get_selected_set_ids() if hasattr(self.set_panel, 'get_selected_set_ids') else []
        print("[DEBUG] on_add_selected_problems_to_sets: selected_sets:", selected_sets)
        if not selected_problems or not selected_sets:
            QMessageBox.warning(self, "Add to Set", "Please select problems and sets.")
            return
        from db.problem_set_db import ProblemSetDB
        db = ProblemSetDB()
        added = 0
        already = 0
        for set_id in selected_sets:
            for prob in selected_problems:
                pid = prob.get('problem_id')
                result = db.add_problem_to_set(set_id, pid)
                if result:
                    added += 1
                else:
                    already += 1
        QMessageBox.information(self, "Add to Set", f"Added {added} problems to {len(selected_sets)} set(s). Already present: {already}.") 