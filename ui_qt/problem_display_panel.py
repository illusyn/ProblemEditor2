from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QSizePolicy, QScrollArea, QSpacerItem, QHBoxLayout, QComboBox, QGroupBox, QCheckBox, QPushButton, QRubberBand, QApplication
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QPen
from PyQt5.QtCore import Qt, QRect, QPoint, QSize, pyqtSignal
import re, os
from db.math_db import MathProblemDB
from managers.image_manager_qt import ImageManagerQt
import json
from ui_qt.style_config import CATEGORY_BTN_SELECTED_COLOR

class ProblemCellWidget(QWidget):
    def __init__(self, problem, font_size, parent=None):
        super().__init__(parent)
        self.problem = problem
        self.selected = False
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(12)
        self.setLayout(main_layout)

        # --- LEFT: Text and summary ---
        left_vbox = QVBoxLayout()
        # Remove LaTeX between \begin{figure} and \end{figure}
        content = problem.get('content', '')
        content = re.sub(r'\\begin\{figure\}.*?\\end\{figure\}', '', content, flags=re.DOTALL)
        content = re.sub(r'\n\s*\n+', '\n\n', content)
        content = content.strip()
        self.content_label = QLabel(content)
        self.content_label.setAlignment(Qt.AlignTop)
        self.content_label.setWordWrap(True)
        self.content_label.setFont(QFont('Arial', font_size))
        left_vbox.addWidget(self.content_label)

        # Build summary info (ID, Answer, Types, Cat, etc.)
        problem_id = problem.get('problem_id', '')
        answer = problem.get('answer', '').strip()
        summary_top = f'<span style="color:#1976d2;"><b>ID:</b> {problem_id}'
        if answer:
            summary_top += f' &nbsp; <b>Answer:</b> {answer}'
        summary_top += '</span>'

        summary_lines = []
        earmark = problem.get('earmark', None)
        if earmark not in [None, 0, '', False, '0', 'False']:
            summary_lines.append('<b>Earmark:</b> Yes')
        types = problem.get('types', [])
        if types:
            type_names = ', '.join([t['name'] for t in types])
            summary_lines.append(f'<b>Types:</b> {type_names}')
        categories = problem.get('categories', [])
        if categories:
            cat_names = ', '.join([c['name'] for c in categories])
            summary_lines.append(f'<b>Cat:</b> {cat_names}')
        notes = problem.get('notes', '').strip()
        if notes:
            summary_lines.append(f'<b>Notes:</b> {notes}')
        summary_bottom = ''
        if summary_lines:
            summary_bottom = f'<span style="color:#1976d2;">' + '<br>'.join(summary_lines) + '</span>'

        summary_html = summary_top
        if summary_bottom:
            summary_html += '<br>' + summary_bottom
        summary_label = QLabel()
        summary_label.setTextFormat(Qt.RichText)
        summary_label.setText(summary_html)
        summary_label.setWordWrap(True)
        summary_label.setFont(QFont('Arial', 12))
        left_vbox.addWidget(summary_label)
        left_vbox.addStretch(1)

        main_layout.addLayout(left_vbox, stretch=3)

        # --- RIGHT: Images (if any) ---
        images_vbox = QVBoxLayout()
        problem_id = problem.get('problem_id', None)
        image_count = 0
        if problem_id is not None:
            db = MathProblemDB()
            try:
                db.cur.execute("SELECT image_name FROM problem_images WHERE problem_id=?", (problem_id,))
                image_names = [row[0] for row in db.cur.fetchall()]
                image_manager = ImageManagerQt(self)
                for image_name in image_names:
                    image_path = os.path.join('temp', 'images', image_name)
                    if not os.path.exists(image_path):
                        success, msg = image_manager.image_db.export_to_file(image_name, image_path)
                        if not success:
                            continue
                    pixmap = QPixmap(image_path)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaledToWidth(100, Qt.SmoothTransformation)
                        img_label = QLabel()
                        img_label.setPixmap(pixmap)
                        img_label.setAlignment(Qt.AlignCenter)
                        images_vbox.addWidget(img_label)
                        image_count += 1
            except Exception as e:
                print(f"[DEBUG] ProblemCellWidget: error loading images for problem {problem_id}: {e}")
            db.close()
        images_vbox.addStretch(1)
        # Only add the image column if there are images
        if image_count > 0:
            main_layout.addLayout(images_vbox, stretch=2)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setAutoFillBackground(True)

    def set_selected(self, selected: bool):
        self.selected = selected
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.parent() and hasattr(self.parent(), 'on_cell_clicked'):
                self.parent().on_cell_clicked(self)
        super().mousePressEvent(event)

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.selected:
            painter = QPainter(self)
            try:
                pen = QPen(QColor(CATEGORY_BTN_SELECTED_COLOR))
                pen.setWidth(4)
                painter.setPen(pen)
                painter.drawRect(self.rect().adjusted(2, 2, -2, -2))
            finally:
                painter.end()

class ProblemDisplayPanel(QWidget):
    CONFIG_PATH = "user_settings.json"
    selection_changed = pyqtSignal(list)

    def __init__(self, parent=None):
        print("ProblemDisplayPanel init:0")
        super().__init__(parent)
        print("ProblemDisplayPanel init")
        self.outer_layout = QVBoxLayout(self)
        self.setLayout(self.outer_layout)

        # --- Display configuration panel ---
        config_group = QGroupBox("Display Configuration")
        config_layout = QHBoxLayout()
        config_group.setLayout(config_layout)
        config_layout.addWidget(QLabel("Font size:"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(i) for i in range(10, 33)])
        # Load saved font size if available
        self.font_size_combo.setCurrentText(str(self.load_saved_font_size()))
        self.current_font_size = int(self.font_size_combo.currentText())
        config_layout.addWidget(self.font_size_combo)
        # Add 'Save Fontsize' button instead of checkbox
        self.save_font_btn = QPushButton("Save Fontsize")
        config_layout.addWidget(self.save_font_btn)
        self.save_font_btn.clicked.connect(self.on_save_font_btn_clicked)
        config_layout.addStretch(1)
        self.outer_layout.addWidget(config_group)
        self.font_size_combo.currentTextChanged.connect(self.on_font_size_changed)

        # Scrollable area for problems
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_content = QWidget()
        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(12)
        self.scroll_content.setLayout(self.grid)
        self.scroll_area.setWidget(self.scroll_content)

        # Add scroll area to the upper 60%
        self.outer_layout.addWidget(self.scroll_area, stretch=3)  # 60%
        # Add a spacer to fill the lower 40%
        self.outer_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.problems = []
        self.problem_cells = []
        self.selected_problem_ids = set()
        self.selection_anchor_idx = None  # Track anchor for shift-selection
        self.rubber_band = None
        self.origin = QPoint()
        self.scroll_content.installEventFilter(self)

        # Set a fixed height for the panel (adjust as needed)
        # self.setFixedHeight(600)

    def set_problems(self, problems):
        # Clear existing widgets
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.problems = problems
        self.problem_cells = []
        self.selected_problem_ids = set()
        self.selection_anchor_idx = None
        if not problems:
            return
        cols = 3  # Number of columns in the grid
        for idx, problem in enumerate(problems):
            row = idx // cols
            col = idx % cols
            cell = ProblemCellWidget(problem, self.current_font_size, parent=self.scroll_content)
            self.grid.addWidget(cell, row, col)
            self.problem_cells.append(cell)
        self.update_all_content_fonts()

    def update_all_content_fonts(self):
        try:
            font_size = int(self.font_size_combo.currentText())
        except Exception:
            font_size = 14
        self.current_font_size = font_size
        for cell in self.problem_cells:
            cell.content_label.setFont(QFont('Arial', font_size))

    def load_saved_font_size(self):
        if os.path.exists(self.CONFIG_PATH):
            with open(self.CONFIG_PATH, "r") as f:
                data = json.load(f)
                return data.get("problem_manager_font_size", 14)
        return 14

    def save_font_size(self, size):
        data = {}
        if os.path.exists(self.CONFIG_PATH):
            with open(self.CONFIG_PATH, "r") as f:
                data = json.load(f)
        data["problem_manager_font_size"] = int(size)
        with open(self.CONFIG_PATH, "w") as f:
            json.dump(data, f)

    def on_font_size_changed(self, size):
        self.update_all_content_fonts()
        # No auto-save on change; only save when button is clicked

    def on_save_font_btn_clicked(self):
        self.save_font_size(self.font_size_combo.currentText())

    def load_remember_font_setting(self):
        # Deprecated, no longer used
        return True

    def save_remember_font_setting(self, remember):
        # Deprecated, no longer used
        pass

    def on_cell_clicked(self, cell):
        prob_id = cell.problem.get('problem_id')
        if prob_id is None:
            return
        idx = self.problem_cells.index(cell)
        modifiers = QApplication.keyboardModifiers()
        if modifiers & Qt.ControlModifier:
            # Ctrl+Click toggles selection
            if prob_id in self.selected_problem_ids:
                self.selected_problem_ids.remove(prob_id)
                cell.set_selected(False)
            else:
                self.selected_problem_ids.add(prob_id)
                cell.set_selected(True)
            self.selection_anchor_idx = idx
        elif modifiers & Qt.ShiftModifier:
            # Shift+Click: expand selection from anchor to clicked cell
            if self.selection_anchor_idx is not None:
                start, end = sorted([self.selection_anchor_idx, idx])
                for i in range(start, end+1):
                    pid = self.problem_cells[i].problem.get('problem_id')
                    self.selected_problem_ids.add(pid)
                    self.problem_cells[i].set_selected(True)
            else:
                self.selected_problem_ids.add(prob_id)
                cell.set_selected(True)
                self.selection_anchor_idx = idx
        else:
            # Single click: clear others, select this
            for c in self.problem_cells:
                c.set_selected(False)
            self.selected_problem_ids = {prob_id}
            cell.set_selected(True)
            self.selection_anchor_idx = idx
        self.selection_changed.emit(list(self.selected_problem_ids))

    def clear_selection(self):
        self.selected_problem_ids.clear()
        for c in self.problem_cells:
            c.set_selected(False)
        self.selection_anchor_idx = None
        self.selection_changed.emit([])

    def get_selected_problems(self):
        selected = [c.problem for c in self.problem_cells if c.problem.get('problem_id') in self.selected_problem_ids]
        print("[DEBUG] get_selected_problems called, returning:", [p.get('problem_id') for p in selected])
        return selected

    # --- Rubber-band selection ---
    def eventFilter(self, obj, event):
        if not self.isVisible():
            return False
        if obj is self.scroll_content:
            if event.type() == event.MouseButtonPress and event.button() == Qt.LeftButton:
                self.origin = event.pos()
                if not self.rubber_band:
                    self.rubber_band = QRubberBand(QRubberBand.Rectangle, self.scroll_content)
                self.rubber_band.setGeometry(QRect(self.origin, QSize()))
                self.rubber_band.show()
                return True
            elif event.type() == event.MouseMove and self.rubber_band and self.rubber_band.isVisible():
                rect = QRect(self.origin, event.pos()).normalized()
                self.rubber_band.setGeometry(rect)
                return True
            elif event.type() == event.MouseButtonRelease and self.rubber_band and self.rubber_band.isVisible():
                rect = self.rubber_band.geometry()
                self.rubber_band.hide()
                shift_held = QApplication.keyboardModifiers() & Qt.ShiftModifier
                self._select_cells_in_rect(rect, expand=shift_held)
                return True
        return super().eventFilter(obj, event)

    def _select_cells_in_rect(self, rect, expand=False):
        # If expand is True, add to selection; else, clear and select only those in rect
        if not expand:
            for c in self.problem_cells:
                c.set_selected(False)
            self.selected_problem_ids.clear()
        last_selected_idx = None
        for i, c in enumerate(self.problem_cells):
            cell_rect = c.geometry()
            if rect.intersects(cell_rect):
                pid = c.problem.get('problem_id')
                self.selected_problem_ids.add(pid)
                c.set_selected(True)
                last_selected_idx = i
        # Update anchor to last cell in selection if any
        if last_selected_idx is not None:
            self.selection_anchor_idx = last_selected_idx
        self.selection_changed.emit(list(self.selected_problem_ids)) 