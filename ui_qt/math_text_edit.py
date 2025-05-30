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
        QShortcut(QKeySequence("Ctrl+Shift+D"), self, self.insert_degree)
        QShortcut(QKeySequence("Ctrl+R"), self, self.insert_half_power)
        QShortcut(QKeySequence("Ctrl+S"), self, self.insert_sqrt)
        QShortcut(QKeySequence("Ctrl+L"), self, self.paste_latex)
        # New shortcuts for $$...$$ wrapped math
        QShortcut(QKeySequence("Ctrl+Shift+F"), self, self.insert_fraction_dollars)
        QShortcut(QKeySequence("Ctrl+Shift+D"), self, self.insert_degree_dollars)
        QShortcut(QKeySequence("Ctrl+Shift+R"), self, self.insert_half_power_dollars)
        QShortcut(QKeySequence("Ctrl+Shift+S"), self, self.insert_sqrt_dollars)
        QShortcut(QKeySequence("Ctrl+P"), self, self.insert_problem_section)
        QShortcut(QKeySequence("Ctrl+T"), self, self.insert_text_section)

    def show_context_menu(self, pos):
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        menu.addAction("Paste LaTeX as Equation", self.paste_latex)
        menu.addAction("Wrap Math", self.wrap_math_selection)
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
        unit_pattern = r"cm|mm|m|kg|g|s|ms|K|N|J|W|V|A|Hz|rad|deg|mol|Pa|bar|atm|L|h|min|d|yr|eV|u|au|pc|ly|sr|T|C|F|S|Ω|ohm|lx|lm|cd|Bq|Gy|Sv|kat|cal|hp|psi|lb|oz|ton|gal|qt|pt|cup|tbsp|tsp|yd|mi|nmi|acre|ha|angstrom"
        math_symbols = r"[\+\-\=\*/\^<>]|<=|>=|!=|\\leq|\\geq|\\neq|\\approx|\\sim|\\cdot|\\div|\\times|\\pm|\\mp|\\to|\\rightarrow|\\left|\\right|\\infty|\\sqrt|\\frac"
        variable_pattern = r"[A-Z]{2,}|[a-z]{2,}|[a-zA-Z]"
        number_pattern = r"\d+(?:\.\d+)?"
        math_symbols_extended = math_symbols + r"|‖"
        math_token_check = re.compile(rf"{variable_pattern}|{number_pattern}|{math_symbols_extended}")
        segments = re.findall(r"[a-zA-Z']+|[^a-zA-Z']+", text)
        result = []
        buffer = ''
        def is_english_word(token):
            if EN_DICT:
                return EN_DICT.check(token.lower())
            return token.lower() in {'square', 'feet', 'perimeter', 'that', 'has', 'is', 'the', 'a', 'an', 'and', 'or', 'to', 'of', 'in', 'on', 'for', 'by', 'with', 'as', 'at', 'from', 'it', 'this', 'be', 'are', 'was', 'were', 'which', 'but', 'not', 'so', 'if', 'then', 'than', 'when', 'where', 'who', 'what', 'how', 'why', 'can', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'do', 'does', 'did', 'have', 'had', 'having', 'get', 'got', 'make', 'made', 'see', 'seen', 'go', 'went', 'gone', 'come', 'came', 'say', 'said', 'use', 'used', 'using', 'about', 'into', 'over', 'under', 'after', 'before', 'between', 'each', 'all', 'some', 'any', 'no', 'yes', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'first', 'second', 'third', 'last', 'next', 'other', 'more', 'most', 'less', 'least', 'many', 'much', 'few', 'every', 'either', 'neither', 'both', 'just', 'even', 'still', 'yet', 'already', 'always', 'never', 'sometimes', 'often', 'usually', 'again', 'new', 'old', 'young', 'long', 'short', 'high', 'low', 'big', 'small', 'large', 'great', 'little', 'same', 'different', 'own', 'part', 'whole', 'place', 'thing', 'way', 'day', 'week', 'month', 'year', 'time', 'number', 'problem', 'solution', 'question', 'answer', 'example', 'line', 'point', 'segment', 'angle', 'triangle', 'circle', 'rectangle', 'parallelogram', 'rhombus', 'trapezoid', 'polygon', 'area', 'volume', 'length', 'width', 'height', 'radius', 'diameter', 'side', 'base', 'altitude', 'vertex', 'vertices', 'edge', 'edges', 'face', 'faces', 'solid', 'figure', 'diagram', 'graph', 'table', 'chart', 'value', 'values', 'expression', 'equation', 'inequality', 'system', 'set', 'subset', 'element', 'elements', 'member', 'members', 'function', 'domain', 'range', 'input', 'output', 'variable', 'constant', 'coefficient', 'term', 'terms', 'factor', 'factors', 'multiple', 'multiples', 'divisor', 'divisors', 'quotient', 'remainder', 'product', 'sum', 'difference', 'average', 'mean', 'median', 'mode', 'probability', 'percent', 'fraction', 'decimal', 'integer', 'whole', 'natural', 'rational', 'irrational', 'real', 'complex', 'positive', 'negative', 'zero', 'prime', 'composite', 'even', 'odd', 'congruent', 'similar', 'parallel', 'perpendicular', 'right', 'acute', 'obtuse', 'scalene', 'isosceles', 'equilateral'}
        for seg in segments:
            if seg.isalpha() and is_english_word(seg):
                if buffer:
                    m = re.match(r'^(\s*)(.*?)(\s*)$', buffer)
                    leading_space = m.group(1)
                    math_part = m.group(2)
                    trailing_space = m.group(3)
                    if math_part:
                        if math_token_check.search(math_part):
                            if not re.match(r"^\$.*\$$", math_part):
                                result.append(f"{leading_space}${math_part}${trailing_space}")
                            else:
                                result.append(f"{leading_space}{math_part}{trailing_space}")
                        else:
                            result.append(f"{leading_space}{math_part}{trailing_space}")
                    else:
                        result.append(buffer)
                    buffer = ''
                result.append(seg)
            else:
                buffer += seg
        if buffer:
            m = re.match(r'^(\s*)(.*?)(\s*)$', buffer)
            leading_space = m.group(1)
            math_part = m.group(2)
            trailing_space = m.group(3)
            if math_part:
                if math_token_check.search(math_part):
                    if not re.match(r"^\$.*\$$", math_part):
                        result.append(f"{leading_space}${math_part}${trailing_space}")
                    else:
                        result.append(f"{leading_space}{math_part}{trailing_space}")
                else:
                    result.append(f"{leading_space}{math_part}{trailing_space}")
            else:
                result.append(buffer)
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

    def insertFromMimeData(self, source):
        # Override paste to clean text
        text = source.text()
        cleaned = clean_pasted_text(text)
        self.insertPlainText(cleaned) 