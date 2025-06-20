"""
MathTextEdit: QTextEdit subclass for math/markdown editing with context menu and shortcuts.
"""

import re
import unicodedata
from PyQt5.QtWidgets import QTextEdit, QMenu, QAction, QApplication, QMessageBox, QShortcut
from PyQt5.QtGui import QKeySequence, QTextCursor, QFont, QContextMenuEvent, QMouseEvent, QPalette
from PyQt5.QtCore import Qt
from ui_qt.style_config import EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE, EDITOR_BG_COLOR

try:
    import enchant
    EN_DICT = enchant.Dict("en_US")
except ImportError:
    EN_DICT = None

try:
    from english_words import english_words_set
    # Convert to lowercase for easier comparison
    ENGLISH_WORDS = {word.lower() for word in english_words_set}
except ImportError:
    ENGLISH_WORDS = None

UNICODE_LATEX_MAP = {
    "π": r"\pi",
    "Π": r"\Pi",
    "α": r"\alpha",
    "β": r"\beta",
    "θ": r"\theta",
    "μ": r"\mu",
    "–": "-",  # en-dash
    "—": "--", # em-dash
    "“": '"', "”": '"', "‘": "'", "’": "'",
    # Add more as needed
}

GREEK_COMMANDS = [
    "pi", "alpha", "beta", "theta", "mu", "Pi", "Alpha", "Beta", "Theta", "Mu"
    # Add more as needed
]

def clean_pasted_text(text):
    text = unicodedata.normalize('NFKC', text)
    for uni, latex in UNICODE_LATEX_MAP.items():
        text = text.replace(uni, latex)
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    greek_pattern = r'\\(' + '|'.join(GREEK_COMMANDS) + r')(?![a-zA-Z])'
    text = re.sub(greek_pattern, r'\\\1\\,', text)
    return text

class MathTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        font = QFont(EDITOR_FONT_FAMILY)
        font.setPointSizeF(EDITOR_FONT_SIZE)
        self.setFont(font)
        self.setStyleSheet(f"background: {EDITOR_BG_COLOR};")
        self.setMinimumSize(400, 300)
        # Keep selection visible even when focus is lost
        palette = self.palette()
        palette.setColor(palette.Inactive, palette.HighlightedText, palette.color(palette.Active, palette.HighlightedText))
        palette.setColor(palette.Inactive, palette.Highlight, palette.color(palette.Active, palette.Highlight))
        self.setPalette(palette)
        # Shortcuts
        QShortcut(QKeySequence("Ctrl+F"), self, self.insert_fraction)
        QShortcut(QKeySequence("Ctrl+D"), self, self.insert_degree)
        QShortcut(QKeySequence("Ctrl+R"), self, self.insert_half_power)
        QShortcut(QKeySequence("Ctrl+S"), self, self.insert_sqrt)
        QShortcut(QKeySequence("Ctrl+L"), self, self.paste_latex)
        # New shortcuts for $$...$$ wrapped math
        QShortcut(QKeySequence("Ctrl+Shift+F"), self, self.insert_fraction_dollars)
        QShortcut(QKeySequence("Ctrl+Shift+D"), self, self.insert_degree_dollars)
        QShortcut(QKeySequence("Ctrl+Shift+R"), self, self.insert_half_power_dollars)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.insert_sqrt_dollars)
        QShortcut(QKeySequence("Ctrl+P"), self, self.insert_problem_section)
        QShortcut(QKeySequence("Ctrl+Alt+T"), self, self.insert_text_section)  # Changed from Ctrl+T
        QShortcut(QKeySequence("Ctrl+Shift+N"), self, self.insert_vspace)
        # New triangle shortcuts
        QShortcut(QKeySequence("Ctrl+T"), self, self.insert_triangle)
        QShortcut(QKeySequence("Ctrl+Shift+T"), self, self.insert_triangle_dollars)
        # Overline shortcuts
        QShortcut(QKeySequence("Ctrl+O"), self, self.overline_selection)
        QShortcut(QKeySequence("Ctrl+Shift+O"), self, self.overline_selection_dollars)
        # Wide hat shortcuts
        QShortcut(QKeySequence("Alt+A"), self, self.widehat_selection)
        QShortcut(QKeySequence("Alt+Shift+A"), self, self.widehat_selection_dollars)
        # Angle shortcuts - Note: This will override the default Select All (Ctrl+A)
        QShortcut(QKeySequence("Ctrl+A"), self, self.insert_angle)
        QShortcut(QKeySequence("Ctrl+Shift+A"), self, self.insert_angle_dollars)

    def mousePressEvent(self, event):
        """Override mouse press to preserve selection on right-click."""
        if event.button() == Qt.RightButton:
            # Do nothing - let mouseReleaseEvent handle it
            event.accept()
        else:
            # For other buttons, use default behavior
            super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """Show context menu on right-click release."""
        if event.button() == Qt.RightButton:
            # Show context menu on release
            menu = self.createStandardContextMenu()
            menu.addSeparator()
            menu.addAction("Paste LaTeX as Equation", self.paste_latex)
            menu.addAction("Wrap Math", self.wrap_math_selection)
            menu.addAction("Overline Selection", self.overline_selection)
            menu.addAction("Overline Selection (with $)", self.overline_selection_dollars)
            menu.addAction("Wide Hat Selection", self.widehat_selection)
            menu.addAction("Wide Hat Selection (with $)", self.widehat_selection_dollars)
            
            # Apply custom styling
            menu.setStyleSheet("""
                QMenu {
                    background-color: #f5f5f5;
                    color: #333333;
                    border: 1px solid #cccccc;
                    padding: 4px;
                }
                QMenu::item {
                    background-color: transparent;
                    color: #333333;
                    padding: 6px 20px;
                }
                QMenu::item:selected {
                    background-color: #4a90e2;
                    color: #ffffff;
                }
                QMenu::item:disabled {
                    color: #999999;
                }
                QMenu::separator {
                    height: 1px;
                    background-color: #cccccc;
                    margin: 4px 10px;
                }
            """)
            
            menu.exec_(event.globalPos())
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def contextMenuEvent(self, event):
        """Override context menu event to prevent default behavior."""
        # Do nothing - we handle context menu in mouseReleaseEvent
        event.accept()

    def paste_latex(self):
        clipboard = QApplication.clipboard()
        latex = clipboard.text()
        if latex:
            formatted = self.format_as_equation(latex)
            self.insertPlainText(formatted)
        else:
            QMessageBox.warning(self, "Clipboard Error", "No LaTeX content found in clipboard.")

    def format_as_equation(self, latex):
        return f"#eq\n{latex}\n"

    def wrap_math_selection(self):
        cursor = self.textCursor()
        if not cursor.hasSelection():
            QMessageBox.information(self, "No Selection", "Please select text to wrap with math.")
            return
        selected_text = cursor.selectedText()
        wrapped = self._wrap_math_runs_exclude_words(selected_text)
        cursor.insertText(wrapped)
    

    def _wrap_math_runs_exclude_words(self, text):
        """
        Wrap mathematical expressions in dollar signs while excluding English words.
        This function uses a greedy approach to wrap entire mathematical expressions
        instead of individual tokens.
        """
        # First, let's handle the simple case where the entire selection is wrapped
        if text.startswith('$') and text.endswith('$'):
            return text
            
        # Helper function to check if a word is likely English (not math)
        def is_english_word(word):
            if not word or not word.isalpha():
                return False
            # Common English words that might appear in math context
            common_words = {'is', 'the', 'of', 'and', 'or', 'if', 'then', 'where', 
                           'find', 'calculate', 'solve', 'given', 'what', 'how',
                           'with', 'has', 'have', 'be', 'are', 'was', 'were'}
            if word.lower() in common_words:
                return True
            if ENGLISH_WORDS and len(word) > 2:  # Skip single letters
                return word.lower() in ENGLISH_WORDS
            return False
        
        # Pattern to identify mathematical content
        # This includes: variables, numbers, operators, functions, parentheses, etc.
        math_chars = r'[a-zA-Z0-9\+\-\*/=<>^_\(\)\[\]\{\}\\.,]'
        
        # Split text into potential math expressions and non-math text
        # Look for continuous runs of mathematical characters
        parts = re.split(r'(\s+)', text)
        
        result = []
        i = 0
        while i < len(parts):
            part = parts[i]
            
            # Skip whitespace
            if part.isspace():
                result.append(part)
                i += 1
                continue
            
            # Check if this looks like the start of a math expression
            # Common patterns: f(x), g(x), equations, expressions with operators
            if (re.match(r'[a-zA-Z]\([a-zA-Z]\)', part) or  # Function notation f(x)
                re.search(r'[=\+\-\*/\^]', part) or          # Contains operators
                re.match(r'\d+', part) or                    # Starts with number
                re.match(r'[a-zA-Z]\d', part) or             # Variable with subscript
                re.match(r'[a-zA-Z]\^', part)):              # Variable with exponent
                
                # Start collecting the math expression
                math_expr = [part]
                j = i + 1
                
                # Continue collecting while we have math-like content
                while j < len(parts):
                    if parts[j].isspace():
                        # Include space in math expression
                        math_expr.append(parts[j])
                        j += 1
                    elif j < len(parts) and re.match(math_chars + '+', parts[j]):
                        # Check if it's a standalone English word
                        if parts[j].isalpha() and is_english_word(parts[j]):
                            # Don't include English words unless they're single letters
                            if len(parts[j]) > 1:
                                break
                        math_expr.append(parts[j])
                        j += 1
                    else:
                        break
                
                # Join the math expression and wrap it
                math_text = ''.join(math_expr).strip()
                
                # Handle trailing punctuation
                trailing_punct = ''
                if math_text and math_text[-1] in ',.;:!?':
                    trailing_punct = math_text[-1]
                    math_text = math_text[:-1].strip()
                
                # Wrap the entire expression
                if math_text:
                    result.append(f'${math_text}$' + trailing_punct)
                
                i = j
            else:
                # Not math, just append as is
                result.append(part)
                i += 1
        
        return ''.join(result)

    def insert_fraction(self):
        self.insertPlainText(r"\frac{}{}")
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 2)
        self.setTextCursor(cursor)

    def insert_degree(self):
        self.insertPlainText(r"^\circ")

    def insert_half_power(self):
        self.insertPlainText("^.5")

    def insert_sqrt(self):
        self.insertPlainText(r"\sqrt{}")
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
        self.setTextCursor(cursor)

    def insert_fraction_dollars(self):
        self.insertPlainText(r"$\frac{}{}$")
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 2)
        self.setTextCursor(cursor)

    def insert_degree_dollars(self):
        self.insertPlainText(r"$^\circ$")

    def insert_half_power_dollars(self):
        self.insertPlainText(r"$^.5$")

    def insert_sqrt_dollars(self):
        self.insertPlainText(r"$\sqrt{}$")
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.Left, QTextCursor.MoveAnchor, 1)
        self.setTextCursor(cursor)

    def insert_problem_section(self):
        self.insertPlainText("#problem\n")

    def insert_text_section(self):
        self.insertPlainText("#text\n")
    
    def insert_vspace(self):
        self.insertPlainText(r"\\[2mm]")
    
    def insert_triangle(self):
        self.insertPlainText(r"\bigtriangleup")
    
    def insert_triangle_dollars(self):
        self.insertPlainText(r"$\bigtriangleup$")
    
    def overline_selection(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"\\overline{{{selected_text}}}")
        else:
            self.insertPlainText("\\overline{}")
    
    
    def overline_selection_dollars(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"$\\overline{{{selected_text}}}$")
        else:
            self.insertPlainText("$\\overline{}$")
    
    
    def widehat_selection(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"\\widehat{{{selected_text}}}")
        else:
            self.insertPlainText("\\widehat{}")
    
    
    def widehat_selection_dollars(self):
        cursor = self.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            cursor.insertText(f"$\\widehat{{{selected_text}}}$")
        else:
            self.insertPlainText("$\\widehat{}$")
    
    
    def insert_angle(self):
        self.insertPlainText(r"\angle")
    
    def insert_angle_dollars(self):
        self.insertPlainText(r"$\angle$")

    def insertFromMimeData(self, source):
        # Override paste to clean text
        text = source.text()
        cleaned = clean_pasted_text(text)
        self.insertPlainText(cleaned) 