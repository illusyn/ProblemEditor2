from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout, QSizePolicy, QScrollArea, QSpacerItem, QHBoxLayout, QComboBox, QGroupBox
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import re, os
from db.math_db import MathProblemDB
from managers.image_manager_qt import ImageManagerQt

class ProblemCellWidget(QWidget):
    def __init__(self, problem, font_size, parent=None):
        super().__init__(parent)
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
                db.cur.execute("SELECT image_name FROM problem_image_map WHERE problem_id=?", (problem_id,))
                image_names = [row[0] for row in db.cur.fetchall()]
                image_manager = ImageManagerQt(self)
                for image_name in image_names:
                    image_path = os.path.join('temp', 'images', image_name)
                    if not os.path.exists(image_path):
                        success, msg = image_manager.image_db.export_to_file(image_name, image_path)
                        if not success:
                            print(f"[DEBUG] Could not export image {image_name}: {msg}")
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

class ProblemDisplayPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.outer_layout = QVBoxLayout(self)
        self.setLayout(self.outer_layout)

        # --- Display configuration panel ---
        config_group = QGroupBox("Display Configuration")
        config_layout = QHBoxLayout()
        config_group.setLayout(config_layout)
        config_layout.addWidget(QLabel("Font size:"))
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems([str(i) for i in range(10, 33)])
        self.font_size_combo.setCurrentText("14")
        config_layout.addWidget(self.font_size_combo)
        config_layout.addStretch(1)
        self.outer_layout.addWidget(config_group)
        self.font_size_combo.currentTextChanged.connect(self.update_all_content_fonts)
        self.current_font_size = 14

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

    def set_problems(self, problems):
        # Clear existing widgets
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.problems = problems
        self.problem_cells = []
        if not problems:
            return
        cols = 3  # Number of columns in the grid
        for idx, problem in enumerate(problems):
            row = idx // cols
            col = idx % cols
            cell = ProblemCellWidget(problem, self.current_font_size)
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