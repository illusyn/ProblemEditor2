"""
Main PyQt5 window for the Simplified Math Editor (migration skeleton).
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMenuBar, QAction, QFileDialog, QMessageBox, QPushButton, QVBoxLayout, QDialog
from ui_qt.left_panel import LeftPanel
from ui_qt.editor_panel import EditorPanel
from ui_qt.preview_panel import PreviewPanel
from db.problem_database import ProblemDatabase
from managers.file_manager_qt import FileManager
from managers.image_manager_qt import ImageManagerQt
from managers.image_manager_qt import ImageDetailsDialog
from ui_qt.image_dialog import ImageSizeAdjustDialog
import re
from pathlib import Path
import os
from converters.image_converter import ImageConverter

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simplified Math Editor (PyQt5)")
        self.setGeometry(100, 100, 1200, 800)

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
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)

        # Real panels
        self.left_panel = LeftPanel()
        self.left_panel.setFixedWidth(780)
        layout.addWidget(self.left_panel)
        # Connect query button to filtering
        self.left_panel.query_button.clicked.connect(self.on_query)
        # Connect navigation buttons
        self.left_panel.next_match_button.clicked.connect(self.show_next_problem)
        self.left_panel.prev_match_button.clicked.connect(self.show_previous_problem)
        # Connect preview and delete problem buttons
        self.left_panel.preview_button.clicked.connect(self.update_preview)
        # self.left_panel.delete_problem_button.clicked.connect(self.file_manager.delete_problem)  # Removed as requested

        # Real database connection
        self.problem_db = ProblemDatabase()

        # --- Top 2 Rows of Buttons ---
        """
        row1 = QHBoxLayout()
        for label in ["Reset", "Save Problem", "Delete Problem"]:
            btn = self.left_panel.buttons[label]
            if label == "Delete Problem":
                btn.setText("Preview")
                btn.clicked.disconnect()
                btn.clicked.connect(self.update_preview)
            row1.addWidget(btn)
        layout.addLayout(row1)
        """

        # Editor panel with preview and navigation buttons
        editor_container = QWidget()
        editor_vlayout = QVBoxLayout(editor_container)
        self.editor_panel = EditorPanel()
        editor_vlayout.addWidget(self.editor_panel)
        nav_layout = QHBoxLayout()
        # Remove Previous and Next buttons, only add the new Delete Problem button
        delete_btn = QPushButton("Delete Problem")
        delete_btn.clicked.connect(self.delete_current_problem)
        nav_layout.addWidget(delete_btn)
        editor_vlayout.addLayout(nav_layout)
        layout.addWidget(editor_container, stretch=2)

        self.preview_panel = PreviewPanel()
        layout.addWidget(self.preview_panel, stretch=3)
        
        # Connect preview panel to main window for image adjustment
        self.preview_panel.set_main_window(self)

        # For result navigation
        self.current_results = []
        self.current_result_index = -1

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

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
        search_text = self.left_panel.get_search_text().strip().lower()
        selected_cats = {cat["name"] for cat in self.left_panel.category_panel.get_selected_categories()}
        selected_types = set(self.left_panel.sat_type_panel.get_selected_types())

        problems = self.problem_db.get_all_problems()
        results = []
        for p in problems:
            # Filter by search text
            if search_text and search_text not in (p.get('content','').lower()) and search_text not in (p.get('title','').lower()):
                continue
            # Filter by categories (must include all selected)
            problem_cat_names = {c["name"] for c in p.get('categories', [])}
            if selected_cats and not selected_cats.issubset(problem_cat_names):
                continue
            # Filter by SAT types (must include all selected)
            if selected_types and not selected_types.issubset(set(p.get('sat_types', []))):
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
        # Editor content
        self.editor_panel.text_edit.setPlainText(problem.get("content", ""))
        # Problem ID
        self.left_panel.set_problem_id(str(problem.get("id", "")))
        # Answer
        self.left_panel.set_answer(problem.get("answer", ""))
        # Notes
        self.left_panel.set_notes(problem.get("notes", ""))
        # Categories
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
        # SAT types
        selected_types = set(problem.get("sat_types", []))
        for t, cb in self.left_panel.sat_type_panel.checkboxes.items():
            cb.setChecked(t in selected_types)

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
        problem_id = self.left_panel.get_problem_id()
        if not problem_id:
            QMessageBox.warning(self, "Delete Problem", "No problem selected.")
            return
        success = self.problem_db.delete_problem(problem_id)
        if success:
            QMessageBox.information(self, "Delete Problem", "Problem deleted.")
            # Optionally clear UI or refresh list
            self.editor_panel.text_edit.clear()
            self.left_panel.set_problem_id("")
            self.left_panel.set_answer("")
            self.left_panel.set_notes("")
        else:
            QMessageBox.critical(self, "Delete Problem", "Failed to delete problem.") 