"""
MathTextEdit: QTextEdit subclass for math/markdown editing with context menu and shortcuts.
"""

import re
import unicodedata
from PyQt5.QtWidgets import QTextEdit, QMenu, QAction, QApplication, QMessageBox, QShortcut
from PyQt5.QtGui import QKeySequence, QTextCursor, QFont
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
        font = QFont(EDITOR_FONT_FAMILY, EDITOR_FONT_SIZE)
        self.setFont(font)
        self.setStyleSheet(f"background: {EDITOR_BG_COLOR};")
        self.setMinimumSize(400, 300)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
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

    def show_context_menu(self, pos):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction("Paste LaTeX as Equation", self.paste_latex)
        menu.addAction("Wrap Math", self.wrap_math_selection)
        menu.addAction("Overline Selection", self.overline_selection)
        menu.addAction("Overline Selection (with $)", self.overline_selection_dollars)
        menu.addAction("Wide Hat Selection", self.widehat_selection)
        menu.addAction("Wide Hat Selection (with $)", self.widehat_selection_dollars)
        menu.exec_(self.mapToGlobal(pos))

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
        This function processes selected text and wraps math content while preserving
        punctuation and English words outside of the math delimiters.
        """
        # First, let's handle the simple case where the entire selection is wrapped
        if text.startswith('$') and text.endswith('$'):
            return text
            
        # Helper function to check if token is an English word
        def is_english_word(token):
            if not token or not token.isalpha():
                return False
            if ENGLISH_WORDS:
                return token.lower() in ENGLISH_WORDS
            # Fallback for when english-words package is not installed
            return False
        
        # Use a more sophisticated regex to find mathematical expressions
        # This regex looks for:
        # 1. Expressions in parentheses with numbers: (0, 6)
        # 2. Single variables: x, y, c
        # 3. Mathematical expressions: x^2, πr^2
        # 4. Numbers: 10, 3.14
        math_pattern = r'\([^)]*\d[^)]*\)|[a-zA-Z]\^[\d.]+|[a-zA-Z]+\d+|\d+\.?\d*|[a-zA-Z](?![a-zA-Z])|[\+\-\*/=<>]|\\[a-zA-Z]+|π|θ|α|β|γ|δ|ε|λ|μ|σ|τ|φ|ω'
        
        # Split text into tokens while preserving spaces
        tokens = re.split(r'(\s+)', text)
        result = []
        
        for token in tokens:
            # Skip empty tokens or whitespace
            if not token or token.isspace():
                result.append(token)
                continue
                
            # Check if it's already wrapped in dollars
            if token.startswith('$') and token.endswith('$'):
                result.append(token)
                continue
            
            # Check for sentence-ending punctuation at the end
            trailing_punct = ''
            if token and token[-1] in ',.;:!?':
                trailing_punct = token[-1]
                token = token[:-1]
            
            # If it's an English word, don't wrap it
            if is_english_word(token):
                result.append(token + trailing_punct)
            # If it contains mathematical patterns, wrap it
            elif re.search(math_pattern, token):
                result.append(f'${token}$' + trailing_punct)
            else:
                result.append(token + trailing_punct)
                
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