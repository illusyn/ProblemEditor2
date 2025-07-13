# export_selected_dialog.py
"""
Export Selected Problems dialog for the Simplified Math Editor (PyQt5).

This dialog provides export options for selected problems as a popup.
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


class ExportSelectedDialog(QDialog):
    """Dialog for exporting selected problems to LaTeX"""
    
    # Signals
    export_completed = pyqtSignal(str)  # Emits the output file path
    
    def __init__(self, parent=None, selected_problems=None):
        super().__init__(parent)
        self.selected_problems = selected_problems or []
        self.setWindowTitle("Export Selected Problems to LaTeX")
        self.setModal(True)
        self.setStyleSheet(f"background-color: {WINDOW_BG_COLOR};")
        self._init_ui()
        
    def _init_ui(self):
        """Initialize the UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(PADDING, PADDING, PADDING, PADDING)
        layout.setSpacing(SPACING)
        
        # Info label
        self.info_label = QLabel()
        info_font = QFont(FONT_FAMILY)
        info_font.setPointSizeF(LABEL_FONT_SIZE)
        self.info_label.setFont(info_font)
        self.info_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        # Don't update label yet - export_button doesn't exist
        layout.addWidget(self.info_label)
        
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
        self.title_checkbox.setChecked(False)  # Default to unchecked
        self.title_checkbox.stateChanged.connect(self._on_title_checkbox_changed)
        
        self.title_entry = NeumorphicEntry()
        self.title_entry.setText("Selected Problems")
        self.title_entry.setEnabled(False)  # Disable since checkbox is unchecked by default
        self.title_entry.setMinimumHeight(ENTRY_MIN_HEIGHT)
        
        title_row.addWidget(self.title_checkbox)
        title_row.addWidget(self.title_entry, 1)
        layout.addLayout(title_row)
        
        # Checkbox for including problem numbers
        self.include_numbers_checkbox = QCheckBox("Include problem numbers")
        checkbox_font = QFont(FONT_FAMILY)
        checkbox_font.setPointSizeF(LABEL_FONT_SIZE)
        self.include_numbers_checkbox.setFont(checkbox_font)
        self.include_numbers_checkbox.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        self.include_numbers_checkbox.setChecked(True)  # Default to on
        layout.addWidget(self.include_numbers_checkbox)
        
        # Checkbox for including answers
        self.include_answers_checkbox = QCheckBox("Include answers")
        self.include_answers_checkbox.setFont(checkbox_font)
        self.include_answers_checkbox.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        self.include_answers_checkbox.setChecked(False)  # Default to off
        self.include_answers_checkbox.stateChanged.connect(self._on_answers_checkbox_changed)
        layout.addWidget(self.include_answers_checkbox)
        
        # Checkbox for including metadata
        self.include_metadata_checkbox = QCheckBox("Include metadata (ID, Earmarks, Types, Categories)")
        self.include_metadata_checkbox.setFont(checkbox_font)
        self.include_metadata_checkbox.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        self.include_metadata_checkbox.setChecked(False)
        layout.addWidget(self.include_metadata_checkbox)
        
        # Checkbox for randomizing order
        self.randomize_order_checkbox = QCheckBox("Randomize problem order")
        self.randomize_order_checkbox.setFont(checkbox_font)
        self.randomize_order_checkbox.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        self.randomize_order_checkbox.setChecked(False)
        layout.addWidget(self.randomize_order_checkbox)
        
        # Output file section
        output_label = QLabel("Output File:")
        output_font = QFont(FONT_FAMILY)
        output_font.setPointSizeF(LABEL_FONT_SIZE)
        output_font.setWeight(QFont.Bold)
        output_label.setFont(output_font)
        output_label.setStyleSheet(f"color: {NEUMORPH_TEXT_COLOR};")
        layout.addWidget(output_label)
        
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
        self.browse_button.clicked.connect(self._on_browse_clicked)
        button_box.accepted.connect(self._on_export_clicked)
        button_box.rejected.connect(self.reject)
        
        # Set initial size
        self.resize(600, 300)
        
        # Now update the info label after all widgets are created
        self._update_info_label()
    
    def set_selected_problems(self, problems):
        """Set the list of selected problems to export"""
        self.selected_problems = problems
        self._update_info_label()
    
    def _update_info_label(self):
        """Update the info label with current selection count"""
        count = len(self.selected_problems) if self.selected_problems else 0
        if count == 0:
            self.info_label.setText("No problems selected")
            if hasattr(self, 'export_button'):
                self.export_button.setEnabled(False)
        else:
            self.info_label.setText(f"{count} problem{'s' if count != 1 else ''} selected for export")
            if hasattr(self, 'export_button'):
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
    
    def _on_answers_checkbox_changed(self, state):
        """Update filename when answers checkbox is toggled"""
        current_path = self.output_file_entry.text()
        if not current_path:
            return
        
        # Split the path into directory, basename, and extension
        dir_path = os.path.dirname(current_path)
        filename = os.path.basename(current_path)
        name, ext = os.path.splitext(filename)
        
        # Remove existing "_with_answers" suffix if present
        if name.endswith("_with_answers"):
            name = name[:-len("_with_answers")]
        
        # Add suffix if checkbox is checked
        if self.include_answers_checkbox.isChecked():
            name = name + "_with_answers"
        
        # Reconstruct the path
        new_filename = name + ext
        new_path = os.path.join(dir_path, new_filename) if dir_path else new_filename
        self.output_file_entry.setText(new_path)
    
    def _on_title_checkbox_changed(self, state):
        """Enable/disable title entry based on checkbox state"""
        self.title_entry.setEnabled(self.title_checkbox.isChecked())
    
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
        
        include_title = self.title_checkbox.isChecked()
        title_text = self.title_entry.text() if include_title else None
        include_numbers = self.include_numbers_checkbox.isChecked()
        include_answers = self.include_answers_checkbox.isChecked()
        include_metadata = self.include_metadata_checkbox.isChecked()
        randomize_order = self.randomize_order_checkbox.isChecked()
        
        try:
            # Export the problems
            self._export_problems(output_path, images_dir, title_text, include_numbers, include_answers, include_metadata, randomize_order)
            
            # Show success message
            show_styled_message(self, "Export Complete", f"Successfully exported {len(self.selected_problems)} problems to:\n{output_path}", "info")
            
            # Emit signal and close
            self.export_completed.emit(output_path)
            self.accept()
            
        except Exception as e:
            show_styled_message(self, "Export Error", f"Failed to export problems:\n{str(e)}", "error")
    
    def _export_problems(self, output_path, images_dir, title_text, include_numbers, include_answers, include_metadata, randomize_order=False):
        """Export the selected problems to LaTeX file"""
        import random
        
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
        
        # Create a copy of problems list to potentially randomize
        problems_to_export = self.selected_problems.copy()
        
        # Randomize if requested
        if randomize_order:
            random.shuffle(problems_to_export)
        
        for idx, prob in enumerate(problems_to_export):
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
            
            # Add spacing between problems (except before the first one)
            if idx > 0:
                all_problems_latex += "\\vspace{0.5in}\n"
            
            # Add problem number and content together
            problem_num = idx + 1
            
            # Don't use minipage - it prevents natural page breaks
            all_problems_latex += "\\noindent "
            
            # Strip any leading vspace commands from the latex content
            latex_stripped = latex.strip()
            
            # Handle the common pattern: \vspace{...}\n\fontsize{...}{...}\selectfont content
            # We need to extract and preserve the fontsize command while removing the vspace
            fontsize_match = re.match(r'^\\vspace\{[^}]*\}\s*\n?(\\\\fontsize\{[^}]*\}\{[^}]*\}\\\\selectfont\s*)', latex_stripped)
            
            if fontsize_match:
                # Extract the fontsize command
                fontsize_cmd = fontsize_match.group(1)
                # Remove both vspace and fontsize from the beginning
                content_after_fontsize = latex_stripped[fontsize_match.end():]
                # Build the latex with fontsize applied to both number and content
                if include_numbers:
                    all_problems_latex += fontsize_cmd + "\\makebox[0pt][r]{" + str(problem_num) + ".\\hspace{2em}}" + content_after_fontsize + "\n"
                else:
                    all_problems_latex += fontsize_cmd + content_after_fontsize + "\n"
            elif latex_stripped.startswith("\\vspace"):
                # Just a vspace without fontsize - remove it
                latex_stripped = re.sub(r'^\\vspace\{[^}]*\}\s*\n?', '', latex_stripped)
                if include_numbers:
                    all_problems_latex += "\\makebox[0pt][r]{" + str(problem_num) + ".\\hspace{2em}}" + latex_stripped + "\n"
                else:
                    all_problems_latex += latex_stripped + "\n"
            else:
                # No leading vspace
                if include_numbers:
                    all_problems_latex += "\\makebox[0pt][r]{" + str(problem_num) + ".\\hspace{2em}}" + latex_stripped + "\n"
                else:
                    all_problems_latex += latex_stripped + "\n"
            
            # Add answer if requested (separate from metadata)
            if include_answers:
                answer = prob.get('answer', '').strip()
                if answer:
                    answer_latex = self._format_answer_latex(answer)
                    all_problems_latex += '\n{\\color{red!70!black}\\textbf{Answer:} ' + answer_latex + '}\n'
            
            if include_metadata:
                metadata_block = self._build_metadata_block(prob, include_answer=False)  # Don't include answer in metadata
                if metadata_block:
                    all_problems_latex += '\n{\\color{blue!70!black}\n'
                    all_problems_latex += metadata_block
                    all_problems_latex += '}\n'
        
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
    
    def _format_answer_latex(self, answer):
        """Format answer for LaTeX output"""
        if not answer:
            return ''
            
        # Check if answer contains display math
        if answer.startswith('$$') and answer.endswith('$$'):
            # Display math - return as is
            return answer
        elif answer.startswith(r'\[') and answer.endswith(r'\]'):
            # Display math with \[ \] - return as is
            return answer
        elif answer.startswith('$') and answer.endswith('$') and not answer.startswith('$$'):
            # Inline math - return as is
            return answer
        elif r'\(' in answer or r'\)' in answer:
            # Contains inline math delimiters - return as is
            return answer
        else:
            # Plain text answer, wrap in math mode
            return '$' + self._latex_escape(answer) + '$'
    
    def _build_metadata_block(self, prob, include_answer=True):
        """Build metadata block for a problem"""
        metadata_lines = []
        
        # Problem ID
        metadata_lines.append(r'\textbf{ID:} ' + str(prob['problem_id']))
        
        # Answer (only if include_answer is True)
        if include_answer:
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