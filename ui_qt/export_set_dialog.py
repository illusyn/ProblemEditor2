# export_set_dialog.py
"""
Export Set to LaTeX dialog for the Simplified Math Editor (PyQt5).

This dialog provides export options for a selected problem set.
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox,
    QLineEdit, QPushButton, QFileDialog, QDialogButtonBox
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
    from PyQt5.QtWidgets import QMessageBox
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


class ExportSetDialog(QDialog):
    """Dialog for exporting a problem set to LaTeX"""
    
    # Signals
    export_completed = pyqtSignal(str)  # Emits the output file path
    
    def __init__(self, parent=None, set_id=None, set_name=None):
        super().__init__(parent)
        self.set_id = set_id
        self.set_name = set_name or "Unnamed Set"
        self.setWindowTitle("Export Set to LaTeX")
        self.setModal(True)
        self.setStyleSheet(f"background-color: {WINDOW_BG_COLOR};")
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        layout.setSpacing(SPACING)
        
        # Set name display
        set_info_label = QLabel(f"Set: {self.set_name}")
        info_font = QFont(FONT_FAMILY)
        info_font.setPointSizeF(LABEL_FONT_SIZE)
        info_font.setWeight(QFont.Bold)
        set_info_label.setFont(info_font)
        set_info_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        layout.addWidget(set_info_label)
        
        # Options section
        options_label = QLabel("Export Options:")
        options_font = QFont(FONT_FAMILY)
        options_font.setPointSizeF(LABEL_FONT_SIZE)
        options_font.setWeight(QFont.Bold)
        options_label.setFont(options_font)
        options_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        layout.addWidget(options_label)
        
        # Title checkbox and entry
        title_row = QHBoxLayout()
        title_row.setSpacing(SPACING)
        
        self.title_checkbox = QCheckBox("Title:")
        checkbox_font = QFont(FONT_FAMILY)
        checkbox_font.setPointSizeF(LABEL_FONT_SIZE)
        self.title_checkbox.setFont(checkbox_font)
        self.title_checkbox.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        self.title_checkbox.setChecked(True)  # Default to checked
        
        self.title_entry = NeumorphicEntry()
        self.title_entry.setText(self.set_name)
        self.title_entry.setEnabled(True)  # Enable since checkbox is checked by default
        self.title_entry.setMinimumHeight(ENTRY_MIN_HEIGHT)
        
        title_row.addWidget(self.title_checkbox)
        title_row.addWidget(self.title_entry, 1)
        layout.addLayout(title_row)
        
        # Number problems checkbox
        self.number_problems_checkbox = QCheckBox("Number Problems")
        self.number_problems_checkbox.setFont(checkbox_font)
        self.number_problems_checkbox.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        self.number_problems_checkbox.setChecked(True)  # Default to checked
        layout.addWidget(self.number_problems_checkbox)
        
        # Include answers checkbox
        self.include_answers_checkbox = QCheckBox("Include Answers")
        self.include_answers_checkbox.setFont(checkbox_font)
        self.include_answers_checkbox.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        self.include_answers_checkbox.setChecked(False)  # Default to unchecked
        layout.addWidget(self.include_answers_checkbox)
        
        # Output file section
        output_label = QLabel("Output File:")
        output_label.setFont(options_font)  # Reuse the options_font
        output_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        layout.addWidget(output_label)
        
        # File selection row
        file_row = QHBoxLayout()
        file_row.setSpacing(SPACING)
        
        self.output_file_entry = NeumorphicEntry()
        # Use set name in default filename
        safe_filename = re.sub(r'[^\w\s-]', '', self.set_name)
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
        self.output_file_entry.setText(f"exports/{safe_filename}.tex")
        self.output_file_entry.setMinimumHeight(ENTRY_MIN_HEIGHT)
        
        self.browse_button = NeumorphicButton("Browse...", font_size=BUTTON_FONT_SIZE)
        fm = self.browse_button.fontMetrics()
        text_width = fm.horizontalAdvance(self.browse_button.text()) if hasattr(fm, 'horizontalAdvance') else fm.width(self.browse_button.text())
        self.browse_button.setFixedWidth(text_width + (BUTTON_TEXT_PADDING * 2))
        
        file_row.addWidget(self.output_file_entry)
        file_row.addWidget(self.browse_button)
        
        layout.addLayout(file_row)
        
        # Dialog buttons
        button_box = QDialogButtonBox()
        self.export_button = QPushButton("Export")
        self.cancel_button = QPushButton("Cancel")
        
        # Style the dialog buttons
        for btn in [self.export_button, self.cancel_button]:
            btn_font = QFont(FONT_FAMILY)
            btn_font.setPointSizeF(BUTTON_FONT_SIZE)
            btn.setFont(btn_font)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: #e0e0e3;
                    color: {NEUMORPH_TEXT_COLOR};
                    border: 1px solid #b0b0b3;
                    border-radius: 4px;
                    padding: 5px 15px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: #d0d0d3;
                }}
            """)
        
        button_box.addButton(self.export_button, QDialogButtonBox.AcceptRole)
        button_box.addButton(self.cancel_button, QDialogButtonBox.RejectRole)
        
        layout.addWidget(button_box)
        
        # Connect signals
        self.title_checkbox.toggled.connect(self.title_entry.setEnabled)
        self.browse_button.clicked.connect(self._on_browse_clicked)
        button_box.accepted.connect(self._on_export_clicked)
        button_box.rejected.connect(self.reject)
        
        # Set initial size
        self.resize(600, 350)
    
    def _on_browse_clicked(self):
        """Handle browse button click"""
        current_path = self.output_file_entry.text()
        if not current_path:
            current_path = "exports/set_export.tex"
        
        # Get the directory and filename
        current_dir = os.path.dirname(current_path) or "exports"
        current_file = os.path.basename(current_path) or "set_export.tex"
        
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
        if not self.set_id:
            show_styled_message(self, "No Set", "No set selected for export.", "warning")
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
        
        include_title = self.title_checkbox.isChecked()
        title_text = self.title_entry.text() if include_title else None
        number_problems = self.number_problems_checkbox.isChecked()
        include_answers = self.include_answers_checkbox.isChecked()
        
        try:
            # Export the set
            self._export_set(output_path, images_dir, title_text, number_problems, include_answers)
            
            # Show success message
            show_styled_message(self, "Export Complete", f"Successfully exported set '{self.set_name}' to:\n{output_path}", "info")
            
            # Emit signal and close
            self.export_completed.emit(output_path)
            self.accept()
            
        except Exception as e:
            show_styled_message(self, "Export Error", f"Failed to export set:\n{str(e)}", "error")
    
    def _export_set(self, output_path, images_dir, title_text, number_problems, include_answers):
        """Export the problem set to LaTeX file"""
        # Get problems in the set
        db = MathProblemDB()
        problems = db.list_problems_in_set(self.set_id)
        
        if not isinstance(problems, list):
            db.close()
            raise Exception(f"Failed to get problems from set: {problems}")
        
        if not problems:
            db.close()
            raise Exception("No problems found in the selected set")
        
        # Get full problem data for each problem
        full_problems = []
        for p in problems:
            problem_id = p['problem_id']
            success, prob_data = db.get_problem(problem_id, with_images=True, with_categories=True)
            if success and prob_data:
                # Get earmarks and types
                earmarks_success, earmarks = db.get_earmarks_for_problem(problem_id)
                if earmarks_success:
                    prob_data['earmarks'] = earmarks
                
                types_success, types = db.get_types_for_problem(problem_id)
                if types_success:
                    prob_data['types'] = types
                
                full_problems.append(prob_data)
            else:
                # Log the error but continue with other problems
                print(f"[ERROR] Failed to load problem {problem_id}: {prob_data}")
        
        db.close()
        
        if not full_problems:
            raise Exception("Failed to load problem data")
        
        # Initialize markdown parser
        md_parser = MarkdownParser()
        
        # Build LaTeX content
        all_problems_latex = ""
        
        # Add title if requested
        if title_text:
            # Center the title using LaTeX commands with 26pt font
            all_problems_latex += "\\begin{center}\n"
            all_problems_latex += "{\\fontsize{26pt}{30pt}\\selectfont\\textbf{" + title_text + "}}\n"
            all_problems_latex += "\\end{center}\n"
            all_problems_latex += "\\vspace{1cm}\n\n"
        
        for idx, prob in enumerate(full_problems):
            # Export images for this problem
            self._export_problem_images(prob['problem_id'], prob, images_dir)
            
            # Parse problem content
            content = prob['content']
            problem_number = prob['problem_id']
            latex = md_parser.parse(content, context='export')
            latex = latex.replace(r"\begin{figure}[htbp]", r"\begin{figure}[H]")
            
            # Fix escaped underscores in image filenames within includegraphics
            def fix_image_underscores(match):
                return match.group(1) + match.group(2).replace(r'\_', '_') + match.group(3)
            
            latex = re.sub(r'(\\includegraphics.*?\{)(.*?)(\})', fix_image_underscores, latex)
            latex = re.sub(r'(\\label\{)(.*?)(\})', fix_image_underscores, latex)
            
            # Add filbreak to suggest good page break point before problem
            if idx > 0:
                all_problems_latex += "\\filbreak\n"
            
            if number_problems:
                # Strip any leading newlines or spaces from latex content
                latex_stripped = latex.lstrip('\n \t')
                
                # Remove leading \vspace commands that might cause line breaks
                latex_stripped = re.sub(r'^\\vspace\{[^}]*\}\s*', '', latex_stripped)
                
                # Use parbox approach for proper alignment
                problem_num = idx + 1
                all_problems_latex += "\\noindent\\begin{minipage}{\\textwidth}\n"
                all_problems_latex += "\\noindent\\parbox[t]{2.5em}{\\textbf{" + str(problem_num) + ".}}"
                all_problems_latex += "\\parbox[t]{\\dimexpr\\textwidth-2.5em\\relax}{"
                all_problems_latex += latex_stripped
                all_problems_latex += "}\n"
                all_problems_latex += "\\end{minipage}\n"
            else:
                # Wrap entire problem in minipage to prevent page breaks
                all_problems_latex += "\\noindent\\begin{minipage}{\\textwidth}\n"
                all_problems_latex += latex + "\n"
                all_problems_latex += "\\end{minipage}\n"
            
            # Add answer if requested
            if include_answers and prob.get('answer', '').strip():
                answer = prob['answer'].strip()
                all_problems_latex += "\\vspace{0.2cm}\n"
                all_problems_latex += "{\\color{red}\\footnotesize\\linespread{0.8}\\selectfont\n"
                all_problems_latex += "\\textbf{Answer:} "
                # Process answer - handle potential math content
                all_problems_latex += self._process_answer(answer) + "\\par\n"
                all_problems_latex += "}\n"
            
            # Add spacing between problems (except after the last one)
            if idx < len(full_problems) - 1:
                all_problems_latex += "\\vspace{0.5cm}\n\\noindent\n"
        
        # Create full LaTeX document with export context for larger margins
        full_latex = md_parser.create_latex_document(all_problems_latex, context='export')
        
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
    
    def _process_answer(self, answer):
        """Process answer text as plain text only"""
        # Split answer into lines and join with semicolon for multi-line answers
        lines = answer.split('\n')
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        
        # Join multiple lines with semicolon and space
        if len(cleaned_lines) > 1:
            single_line = '; '.join(cleaned_lines)
        else:
            single_line = cleaned_lines[0] if cleaned_lines else ''
        
        # Replace infinity symbols with words
        single_line = single_line.replace(r'\infty', 'Infinity')
        single_line = single_line.replace('-\\infty', '-Infinity')
        
        # Escape the caret character which triggers math mode
        single_line = single_line.replace('^', r'\textasciicircum{}')
        
        return single_line
    
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