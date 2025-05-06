"""
Main PyQt5 window for the Simplified Math Editor (migration skeleton).
"""

from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QMenuBar, QAction, QFileDialog, QMessageBox, QPushButton, QVBoxLayout
from ui_qt.left_panel import LeftPanel
from ui_qt.editor_panel import EditorPanel
from ui_qt.preview_panel import PreviewPanel
from db.problem_database import ProblemDatabase

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simplified Math Editor (PyQt5)")
        self.setGeometry(100, 100, 1200, 800)

        # Menu bar
        menubar = QMenuBar(self)
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        saveas_action = QAction("Save As...", self)
        saveas_action.triggered.connect(self.save_file_as)
        file_menu.addAction(saveas_action)

        # Additional message box demo actions
        info_action = QAction("Show Info", self)
        info_action.triggered.connect(self.show_info_box)
        file_menu.addAction(info_action)

        error_action = QAction("Show Error", self)
        error_action.triggered.connect(self.show_error_box)
        file_menu.addAction(error_action)

        question_action = QAction("Ask Question", self)
        question_action.triggered.connect(self.ask_question_box)
        file_menu.addAction(question_action)

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

        # Real database connection
        self.problem_db = ProblemDatabase()

        # Editor panel with preview and navigation buttons
        editor_container = QWidget()
        editor_vlayout = QVBoxLayout(editor_container)
        self.editor_panel = EditorPanel()
        editor_vlayout.addWidget(self.editor_panel)
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.show_previous_problem)
        nav_layout.addWidget(self.prev_btn)
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self.update_preview)
        nav_layout.addWidget(preview_btn)
        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.show_next_problem)
        nav_layout.addWidget(self.next_btn)
        editor_vlayout.addLayout(nav_layout)
        layout.addWidget(editor_container, stretch=2)

        self.preview_panel = PreviewPanel()
        layout.addWidget(self.preview_panel, stretch=3)

        # For result navigation
        self.current_results = []
        self.current_result_index = -1

    def open_file(self):
        filename, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;Text Files (*.txt)")
        if filename:
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    text = f.read()
                self.editor_panel.text_edit.setPlainText(text)
                QMessageBox.information(self, "File Opened", f"Loaded file: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open file:\n{e}")

    def save_file_as(self):
        filename, _ = QFileDialog.getSaveFileName(self, "Save File As", "", "All Files (*);;Text Files (*.txt)")
        if filename:
            try:
                text = self.editor_panel.text_edit.toPlainText()
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(text)
                QMessageBox.information(self, "File Saved", f"Saved to: {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file:\n{e}")

    def update_preview(self):
        text = self.editor_panel.text_edit.toPlainText()
        self.preview_panel.preview_label.setText(text)

    def show_info_box(self):
        QMessageBox.information(self, "Information", "This is an information message.")

    def show_error_box(self):
        QMessageBox.critical(self, "Error", "This is an error message.")

    def ask_question_box(self):
        result = QMessageBox.question(self, "Question", "Do you want to continue?")
        if result == QMessageBox.Yes:
            QMessageBox.information(self, "Result", "You chose Yes.")
        else:
            QMessageBox.information(self, "Result", "You chose No.")

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