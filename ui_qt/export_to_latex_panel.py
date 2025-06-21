# export_to_latex_panel.py
"""
Export to LaTeX panel for the Simplified Math Editor (PyQt5).

This panel allows exporting selected problems to a LaTeX file with options:
- Include metadata (ID, answer, earmarks, types, categories)
- Choose output filename
- Export selected problems from query results
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame,
    QCheckBox, QLineEdit, QPushButton, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, pyqtSignal
import os
from ui_qt.neumorphic_components import NeumorphicButton, NeumorphicEntry
from ui_qt.style_config import (
    FONT_FAMILY, LABEL_FONT_SIZE, SECTION_LABEL_FONT_SIZE,
    NEUMORPH_TEXT_COLOR, WINDOW_BG_COLOR, BUTTON_FONT_SIZE,
    BUTTON_TEXT_PADDING, PADDING, SPACING, ENTRY_FONT_SIZE,
    ENTRY_MIN_HEIGHT
)
from markdown_parser import MarkdownParser
from db.math_db import MathProblemDB
from db.math_image_db import MathImageDB
import re


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


class ExportToLatexPanel(QWidget):
    """Panel for exporting selected problems to LaTeX"""
    
    # Signals
    export_completed = pyqtSignal(str)  # Emits the output file path
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background: transparent;')
        self.selected_problems = []  # Will be set by query panel
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(SPACING)
        
        # Section title
        title_label = QLabel("Export Selected Problems to LaTeX")
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
        self.info_label = QLabel("No problems selected")
        info_font = QFont(FONT_FAMILY)
        info_font.setPointSizeF(LABEL_FONT_SIZE)
        self.info_label.setFont(info_font)
        self.info_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        content_layout.addWidget(self.info_label)
        
        # Options section
        options_label = QLabel("Export Options:")
        options_font = QFont(FONT_FAMILY)
        options_font.setPointSizeF(LABEL_FONT_SIZE)
        options_font.setWeight(QFont.Bold)
        options_label.setFont(options_font)
        options_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        content_layout.addWidget(options_label)
        
        # Checkbox for including metadata
        self.include_metadata_checkbox = QCheckBox("Include metadata (ID, Answer, Earmarks, Types, Categories)")
        checkbox_font = QFont(FONT_FAMILY)
        checkbox_font.setPointSizeF(LABEL_FONT_SIZE)
        self.include_metadata_checkbox.setFont(checkbox_font)
        self.include_metadata_checkbox.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        self.include_metadata_checkbox.setChecked(True)
        content_layout.addWidget(self.include_metadata_checkbox)
        
        # Output file section
        output_label = QLabel("Output File:")
        output_font = QFont(FONT_FAMILY)
        output_font.setPointSizeF(LABEL_FONT_SIZE)
        output_font.setWeight(QFont.Bold)
        output_label.setFont(output_font)
        output_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        content_layout.addWidget(output_label)
        
        # File selection row
        file_row = QHBoxLayout()
        file_row.setSpacing(SPACING)
        
        self.output_file_entry = NeumorphicEntry()
        self.output_file_entry.setText("exports/selected_problems.tex")
        self.output_file_entry.setMinimumHeight(ENTRY_MIN_HEIGHT)
        
        self.browse_button = NeumorphicButton("Browse...", font_size=BUTTON_FONT_SIZE)
        fm = self.browse_button.fontMetrics()
        text_width = fm.horizontalAdvance(self.browse_button.text()) if hasattr(fm, 'horizontalAdvance') else fm.width(self.browse_button.text())
        self.browse_button.setFixedWidth(text_width + (BUTTON_TEXT_PADDING * 2))
        
        file_row.addWidget(self.output_file_entry)
        file_row.addWidget(self.browse_button)
        
        content_layout.addLayout(file_row)
        
        # Export button
        self.export_button = NeumorphicButton("Export to LaTeX", font_size=BUTTON_FONT_SIZE)
        fm = self.export_button.fontMetrics()
        text_width = fm.horizontalAdvance(self.export_button.text()) if hasattr(fm, 'horizontalAdvance') else fm.width(self.export_button.text())
        self.export_button.setFixedWidth(text_width + (BUTTON_TEXT_PADDING * 2))
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.export_button)
        button_layout.addStretch()
        
        content_layout.addLayout(button_layout)
        
        main_layout.addWidget(content_frame)
        
        # Connect signals
        self.browse_button.clicked.connect(self._on_browse_clicked)
        self.export_button.clicked.connect(self._on_export_clicked)
    
    def set_selected_problems(self, problems):
        """Set the list of selected problems to export"""
        self.selected_problems = problems
        count = len(problems) if problems else 0
        if count == 0:
            self.info_label.setText("No problems selected")
            self.export_button.setEnabled(False)
        else:
            self.info_label.setText(f"{count} problem{'s' if count != 1 else ''} selected for export")
            self.export_button.setEnabled(True)
    
    def _on_browse_clicked(self):
        """Handle browse button click"""
        current_path = self.output_file_entry.text()
        if not current_path:
            current_path = "exports/selected_problems.tex"
        
        # Get the directory and filename
        current_dir = os.path.dirname(current_path) or "exports"
        current_file = os.path.basename(current_path) or "selected_problems.tex"
        
        # Open file dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save LaTeX File",
            os.path.join(current_dir, current_file),
            "LaTeX Files (*.tex);;All Files (*.*)"
        )
        
        if file_path:
            self.output_file_entry.setText(file_path)
    
    def _on_export_clicked(self):
        """Handle export button click"""
        if not self.selected_problems:
            show_styled_message(self, "No Problems", "No problems selected for export.", "warning")
            return
        
        output_path = self.output_file_entry.text()
        if not output_path:
            show_styled_message(self, "No Output File", "Please specify an output file.", "warning")
            return
        
        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                show_styled_message(self, "Error", f"Failed to create output directory: {str(e)}", "error")
                return
        
        # Create images subdirectory
        images_dir = os.path.join(output_dir or '.', 'images')
        try:
            os.makedirs(images_dir, exist_ok=True)
        except Exception as e:
            show_styled_message(self, "Error", f"Failed to create images directory: {str(e)}", "error")
            return
        
        include_metadata = self.include_metadata_checkbox.isChecked()
        
        try:
            # Export the problems
            self._export_problems(output_path, images_dir, include_metadata)
            
            # Show success message
            show_styled_message(self, "Export Complete", f"Successfully exported {len(self.selected_problems)} problems to:\n{output_path}", "info")
            
            # Emit signal
            self.export_completed.emit(output_path)
            
        except Exception as e:
            show_styled_message(self, "Export Error", f"Failed to export problems:\n{str(e)}", "error")
    
    def _export_problems(self, output_path, images_dir, include_metadata):
        """Export the selected problems to LaTeX file"""
        # Initialize markdown parser
        md_parser = MarkdownParser()
        
        # Build LaTeX content
        all_problems_latex = ""
        
        for idx, prob in enumerate(self.selected_problems):
            # Export images for this problem
            self._export_problem_images(prob['problem_id'], prob, images_dir)
            
            # Parse problem content
            content = prob['content']
            problem_number = prob['problem_id']
            latex = md_parser.parse(content, context='export')
            latex = latex.replace(r"\begin{figure}[htbp]", r"\begin{figure}[H]")
            
            # Fix escaped underscores in image filenames within includegraphics
            def fix_image_underscores(match):
                # Return the includegraphics command with unescaped underscores in the filename
                return match.group(1) + match.group(2).replace(r'\_', '_') + match.group(3)
            
            latex = re.sub(r'(\\includegraphics.*?\{)(.*?)(\})', fix_image_underscores, latex)
            # Also fix underscores in label commands
            latex = re.sub(r'(\\label\{)(.*?)(\})', fix_image_underscores, latex)
            
            # Add to LaTeX content
            all_problems_latex += "\\begin{samepage}\n" + latex + "\n"
            
            if include_metadata:
                metadata_block = self._build_metadata_block(prob)
                if metadata_block:
                    all_problems_latex += '{\\color{blue!70!black}\n'
                    all_problems_latex += metadata_block
                    all_problems_latex += '}\n'
            
            all_problems_latex += "\\end{samepage}\n"
            
            # Add spacing/page breaks
            if not ((idx + 1) % 2 == 0 and (idx + 1) != len(self.selected_problems)):
                all_problems_latex += "\\vspace{1cm}\n"
            if (idx + 1) % 2 == 0 and (idx + 1) != len(self.selected_problems):
                all_problems_latex += "\\clearpage\n"
        
        # Create full LaTeX document
        full_latex = md_parser.create_latex_document(all_problems_latex)
        
        # Fix the graphicspath for export context
        full_latex = full_latex.replace(
            r'\graphicspath{{./}{./images/}{./exports/images/}} ',
            r'\graphicspath{{./}{./images/}}'
        ).replace(
            r'\graphicspath{{./}{./images/}{./exports/images/}}',
            r'\graphicspath{{./}{./images/}}'
        )
        
        # Write to file
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_latex)
    
    def _build_metadata_block(self, prob):
        """Build metadata block for a problem"""
        metadata_lines = []
        
        # Problem ID
        metadata_lines.append(r'\textbf{ID:} ' + str(prob['problem_id']))
        
        # Answer
        answer = prob.get('answer', '').strip()
        if answer:
            # Check if answer contains display math
            if answer.startswith('$$') and answer.endswith('$$'):
                # Display math - needs to be on its own line
                metadata_lines.append(r'\textbf{Answer:}\\')
                metadata_lines.append(answer)
            elif answer.startswith(r'\[') and answer.endswith(r'\]'):
                # Display math with \[ \] - needs to be on its own line
                metadata_lines.append(r'\textbf{Answer:}\\')
                metadata_lines.append(answer)
            elif answer.startswith('$') and answer.endswith('$') and not answer.startswith('$$'):
                # Inline math - can be on same line
                metadata_lines.append(r'\textbf{Answer:} ' + answer)
            elif r'\(' in answer or r'\)' in answer:
                # Contains inline math delimiters
                metadata_lines.append(r'\textbf{Answer:} ' + answer)
            else:
                # Plain text answer, wrap in math mode
                metadata_lines.append(r'\textbf{Answer:} $' + self._latex_escape(answer) + r'$')
        
        # Earmarks
        earmarks = prob.get('earmarks', [])
        if earmarks:
            earmark_names = ', '.join([e['name'] for e in earmarks])
            metadata_lines.append(r'\textbf{Earmarks:} ' + self._latex_escape(earmark_names))
        
        # Problem types
        types = prob.get('types', [])
        if types:
            type_names = ', '.join([self._latex_escape(t['name']) for t in types])
            metadata_lines.append(r'\textbf{Types:} ' + type_names)
        
        # Categories
        categories = prob.get('categories', [])
        if categories:
            cat_names = ', '.join([self._latex_escape(cat['name']) for cat in categories])
            metadata_lines.append(r'\textbf{Categories:} ' + cat_names)
        
        # Join with line breaks - but be careful with display math
        if metadata_lines:
            result = []
            for i, line in enumerate(metadata_lines):
                if i > 0:
                    # Check if previous line was "Answer:" and this line is display math
                    if (metadata_lines[i-1].endswith(r'\textbf{Answer:}\\') and 
                        (line.startswith('$$') or line.startswith(r'\['))):
                        # Display math already has proper spacing
                        result.append(line)
                    else:
                        # Normal line break
                        result.append(r'\\')
                        result.append(line)
                else:
                    result.append(line)
            # Add final line break only if last line isn't display math
            if not (result[-1].endswith('$$') or result[-1].endswith(r'\]')):
                result.append(r'\\')
            return ''.join(result)
        return ''
    
    def _latex_escape(self, text):
        """Escape special LaTeX characters"""
        return text.replace('_', r'\_')
    
    def _export_problem_images(self, problem_id, prob_data, images_dir):
        """Export all images for a problem"""
        # Get images from problem data
        images = prob_data.get('images', [])
        
        if images:
            db = MathProblemDB()
            try:
                for img in images:
                    image_id = img['image_id']
                    image_name = img['image_name']
                    output_path = os.path.join(images_dir, image_name)
                    
                    # Export image
                    success, msg = db.export_image(image_id=image_id, output_path=output_path)
                    if not success:
                        print(f"Warning: Could not export image {image_name} (id={image_id}): {msg}")
            finally:
                db.close()
        
        # Also check for images referenced in content
        content = prob_data.get('content', '')
        image_refs = re.findall(r'\\includegraphics.*?\{(.*?)\}', content)
        
        if image_refs:
            image_db = MathImageDB()
            try:
                for image_name in image_refs:
                    # Skip if already exported
                    output_path = os.path.join(images_dir, image_name)
                    if os.path.exists(output_path):
                        continue
                    
                    # Try to get from image database
                    success, data = image_db.get_image(image_name)
                    if success and data:
                        with open(output_path, 'wb') as f:
                            f.write(data)
                    else:
                        print(f"Warning: Image {image_name} referenced in problem {problem_id} not found in database")
            finally:
                image_db.close()