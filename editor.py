"""
Text editing area with custom markdown syntax and highlighting.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
import unicodedata

UNICODE_LATEX_MAP = {
    "π": r"\pi",
    "Π": r"\Pi",
    "α": r"\alpha",
    "β": r"\beta",
    "θ": r"\theta",
    "μ": r"\mu",
    "–": "-",  # en-dash
    "—": "--", # em-dash
    "“": "\"", "”": "\"", "‘": "'", "’": "'",
    # Add more as needed
}

GREEK_COMMANDS = [
    "pi", "alpha", "beta", "theta", "mu", "Pi", "Alpha", "Beta", "Theta", "Mu"
    # Add more as needed
]

try:
    import enchant
    EN_DICT = enchant.Dict("en_US")
except ImportError:
    EN_DICT = None

def clean_pasted_text(text):
    # Normalize to NFKC to catch composed characters
    text = unicodedata.normalize('NFKC', text)
    for uni, latex in UNICODE_LATEX_MAP.items():
        text = text.replace(uni, latex)
    # Remove any remaining non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    # Add thin space after Greek letter commands when followed by units (cm, mm, m, etc.)
    greek_pattern = r'\\(' + '|'.join(GREEK_COMMANDS) + r')(?=\s*(cm|mm|m|km|in|ft|yd|g|kg|s|ms|K|N|J|W|V|A|Hz|rad|deg|mol|Pa|bar|atm|L|l|h|min|d|yr|eV|u|au|pc|ly|sr|T|C|F|S|S/m|Ω|ohm|lx|lm|cd|Bq|Gy|Sv|kat|cal|calorie|BTU|hp|psi|lb|oz|ton|gal|qt|pt|cup|tbsp|tsp|yd|mi|nmi|acre|ha|angstrom|barn|furlong|chain|rod|link|mil|thou|hand|pica|point|pixel|dot|dpi|ppi|sp|em|ex|rem|ch|vw|vh|vmin|vmax|Q|H|G|D|S|P|E|Z|Y|da|h|k|M|G|T|P|E|Z|Y))'
    text = re.sub(greek_pattern, r'\\\1\\,', text)
    return text

class Editor(ttk.Frame):
    """Text editing area with syntax highlighting"""
    
    def __init__(self, parent):
        """Initialize the editor"""
        super().__init__(parent)
        
        # Create the text widget
        self.editor = tk.Text(
            self,
            wrap=tk.WORD,
            undo=True,
            font=("Courier New", 12)
        )
        self.editor.pack(expand=True, fill="both")
        
        # Create scrollbar
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.editor.yview)
        scrollbar.pack(side="right", fill="y")
        self.editor["yscrollcommand"] = scrollbar.set
        
        # Create context menu
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Cut", command=self.cut_text)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Paste LaTeX as Equation", command=self.paste_latex)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Wrap Math", command=self.wrap_math_selection)
        
        # Bind events
        self.editor.bind("<Button-3>", self.show_context_menu)
        self.editor.bind("<Control-l>", lambda e: self.paste_latex())
        
        # Configure tags for syntax highlighting
        self.editor.tag_configure("command", foreground="blue")
        self.editor.tag_configure("parameter", foreground="green")
        self.editor.tag_configure("equation", foreground="purple")
        
        # Bind syntax highlighting
        self.editor.bind("<KeyRelease>", self.highlight_syntax)
        
        # Keyboard shortcuts
        self.editor.bind("<Control-f>", lambda e: self.insert_fraction())
        self.editor.bind("<Control-Shift-D>", lambda e: self.insert_degree())
        self.editor.bind("<Control-r>", lambda e: self.insert_half_power(e))
        self.editor.bind("<Control-R>", lambda e: self.insert_half_power(e))
        self.editor.bind("<Control-s>", lambda e: self.insert_sqrt(e))
    
    def show_context_menu(self, event):
        """Show the context menu"""
        self.context_menu.post(event.x_root, event.y_root)
    
    def cut_text(self):
        """Cut selected text"""
        self.editor.event_generate("<<Cut>>")
    
    def copy_text(self):
        """Copy selected text"""
        self.editor.event_generate("<<Copy>>")
    
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            clipboard_content = self.editor.clipboard_get()
            cleaned = clean_pasted_text(clipboard_content)
            self.editor.insert("insert", cleaned)
        except tk.TclError:
            pass
        self.highlight_syntax()
    
    def paste_latex(self):
        """Paste LaTeX from clipboard as equation"""
        try:
            clipboard_content = self.clipboard_get()
            if not clipboard_content:
                return
            
            formatted_latex = self.format_as_equation(clipboard_content)
            self.editor.insert("insert", formatted_latex)
            self.highlight_syntax()
            
        except tk.TclError:
            messagebox.showerror(
                "Clipboard Error",
                "Failed to access clipboard content"
            )
    
    def format_as_equation(self, latex):
        """Format LaTeX as an equation block"""
        return f"#eq\n{latex}\n"
    
    def highlight_syntax(self, event=None):
        """Apply syntax highlighting to the text"""
        content = self.editor.get("1.0", "end-1c")
        
        # Remove existing tags
        for tag in ["command", "parameter", "equation"]:
            self.editor.tag_remove(tag, "1.0", "end")
        
        # Highlight commands
        for match in re.finditer(r'#\w+(?:\[.*?\])?', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("command", start, end)
        
        # Highlight parameters
        for match in re.finditer(r'\[.*?\]', content):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("parameter", start, end)
        
        # Highlight equation blocks
        for match in re.finditer(r'#eq\n.*?\n', content, re.DOTALL):
            start = f"1.0+{match.start()}c"
            end = f"1.0+{match.end()}c"
            self.editor.tag_add("equation", start, end)
    
    def get_text(self):
        """Get the editor content"""
        return self.editor.get("1.0", "end-1c")
    
    def get_content(self):
        """Alias for get_text for compatibility"""
        return self.get_text()
    
    def set_text(self, text):
        """Set the text content of the editor"""
        cleaned_text = clean_pasted_text(text)
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", cleaned_text)
        self.highlight_syntax()

    def set_content(self, text):
        """Alias for set_text for compatibility"""
        self.set_text(text)
    
    def clear(self):
        """Clear the editor content"""
        self.editor.delete("1.0", "end")

    def insert(self, position, text):
        """Insert text at the specified position"""
        self.editor.insert(position, text)
        self.highlight_syntax()

    def insert_problem_section(self):
        """Insert a problem section marker"""
        self.insert("insert", "\n#problem\n")

    def insert_solution_section(self):
        """Insert a solution section marker"""
        self.insert("insert", "\n#solution\n")

    def insert_text_block(self):
        """Insert a text block marker"""
        self.insert("insert", "\n#text\n")

    def insert_problem_with_text(self):
        """Insert a problem with text content"""
        self.insert("insert", "\n#problem\n#text\n")

    def insert_question(self):
        """Insert a question marker"""
        self.insert("insert", "\n#question\n")

    def insert_equation(self):
        """Insert an equation marker"""
        self.insert("insert", "\n#eq\n")

    def insert_aligned_equations(self):
        """Insert an aligned equations marker"""
        self.insert("insert", "\n#align\n")

    def insert_bullet_point(self):
        """Insert a bullet point marker"""
        self.insert("insert", "\n#bullet\n")

    def wrap_math_selection(self):
        """Wrap contiguous math substrings (variables, numbers, units, math symbols, and spaces between them) in the selected text with a single $...$ block, minimizing the number of $...$ pairs. Multi-letter variables are only wrapped if not English words (using enchant if available)."""
        try:
            sel_start = self.editor.index(tk.SEL_FIRST)
            sel_end = self.editor.index(tk.SEL_LAST)
            selected_text = self.editor.get(sel_start, sel_end)
        except tk.TclError:
            messagebox.showinfo("No Selection", "Please select text to wrap with math.")
            return

        unit_pattern = r"cm|mm|m|kg|g|s|ms|K|N|J|W|V|A|Hz|rad|deg|mol|Pa|bar|atm|L|h|min|d|yr|eV|u|au|pc|ly|sr|T|C|F|S|Ω|ohm|lx|lm|cd|Bq|Gy|Sv|kat|cal|hp|psi|lb|oz|ton|gal|qt|pt|cup|tbsp|tsp|yd|mi|nmi|acre|ha|angstrom"
        math_symbols = r"[\+\-\=\*/\^<>]|<=|>=|!=|\\leq|\\geq|\\neq|\\approx|\\sim|\\cdot|\\div|\\times|\\pm|\\mp|\\to|\\rightarrow|\\left|\\right|\\infty|\\sqrt|\\frac"
        variable_pattern = r"[A-Z]{2,}|[a-z]{2,}|[a-zA-Z]"
        number_pattern = r"\d+(?:\.\d+)?"
        unit_full_pattern = rf"(?:{unit_pattern})"
        math_symbols_extended = math_symbols + r"|‖"
        math_token_check = re.compile(rf"{variable_pattern}|{number_pattern}|{math_symbols_extended}")

        # Tokenize into word and non-word segments, wrap maximal non-word runs
        def wrap_math_runs_exclude_words(text):
            segments = re.findall(r"[a-zA-Z']+|[^a-zA-Z']+", text)
            result = []
            buffer = ''
            def is_english_word(token):
                if EN_DICT:
                    return EN_DICT.check(token.lower())
                return token.lower() in {'square', 'feet', 'perimeter', 'that', 'has', 'is', 'the', 'a', 'an', 'and', 'or', 'to', 'of', 'in', 'on', 'for', 'by', 'with', 'as', 'at', 'from', 'it', 'this', 'be', 'are', 'was', 'were', 'which', 'but', 'not', 'so', 'if', 'then', 'than', 'when', 'where', 'who', 'what', 'how', 'why', 'can', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'do', 'does', 'did', 'have', 'had', 'having', 'get', 'got', 'make', 'made', 'see', 'seen', 'go', 'went', 'gone', 'come', 'came', 'say', 'said', 'use', 'used', 'using', 'about', 'into', 'over', 'under', 'after', 'before', 'between', 'each', 'all', 'some', 'any', 'no', 'yes', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'first', 'second', 'third', 'last', 'next', 'other', 'more', 'most', 'less', 'least', 'many', 'much', 'few', 'every', 'either', 'neither', 'both', 'just', 'even', 'still', 'yet', 'already', 'always', 'never', 'sometimes', 'often', 'usually', 'again', 'new', 'old', 'young', 'long', 'short', 'high', 'low', 'big', 'small', 'large', 'great', 'little', 'same', 'different', 'own', 'part', 'whole', 'place', 'thing', 'way', 'day', 'week', 'month', 'year', 'time', 'number', 'problem', 'solution', 'question', 'answer', 'example', 'line', 'point', 'segment', 'angle', 'triangle', 'circle', 'rectangle', 'parallelogram', 'rhombus', 'trapezoid', 'polygon', 'area', 'volume', 'length', 'width', 'height', 'radius', 'diameter', 'side', 'base', 'altitude', 'vertex', 'vertices', 'edge', 'edges', 'face', 'faces', 'solid', 'figure', 'diagram', 'graph', 'table', 'chart', 'value', 'values', 'expression', 'equation', 'inequality', 'system', 'set', 'subset', 'element', 'elements', 'member', 'members', 'function', 'domain', 'range', 'input', 'output', 'variable', 'constant', 'coefficient', 'term', 'terms', 'factor', 'factors', 'multiple', 'multiples', 'divisor', 'divisors', 'quotient', 'remainder', 'product', 'sum', 'difference', 'average', 'mean', 'median', 'mode', 'probability', 'percent', 'fraction', 'decimal', 'integer', 'whole', 'natural', 'rational', 'irrational', 'real', 'complex', 'positive', 'negative', 'zero', 'prime', 'composite', 'even', 'odd', 'congruent', 'similar', 'parallel', 'perpendicular', 'right', 'acute', 'obtuse', 'scalene', 'isosceles', 'equilateral'}
            # Regex for math tokens (remove units)
            math_token_check = re.compile(rf"{variable_pattern}|{number_pattern}|{math_symbols_extended}")
            for seg in segments:
                if seg.isalpha() and is_english_word(seg):
                    # Flush buffer as math run if not empty and contains a math token
                    if buffer:
                        # Separate leading and trailing spaces from buffer
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
            # Flush any remaining buffer if it contains a math token
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

        wrapped = wrap_math_runs_exclude_words(selected_text)
        self.editor.delete(sel_start, sel_end)
        self.editor.insert(sel_start, wrapped)
        self.highlight_syntax()

    def insert_fraction(self):
        """Insert a LaTeX fraction template at the cursor position"""
        self.insert("insert", r"\frac{}{}")
        # Optionally, move cursor inside first braces
        self.editor.mark_set("insert", "insert-6c")

    def insert_degree(self):
        """Insert the degree symbol (^{\circ}) at the cursor position"""
        self.insert("insert", r"^\circ")

    def insert_half_power(self, event=None):
        """Insert ^.5 at the current cursor position"""
        print("Ctrl+R pressed: inserting ^.5")
        self.editor.insert("insert", "^.5")
        return "break"

    def insert_sqrt(self, event=None):
        """Insert \sqrt{} at the current cursor position and place cursor inside braces"""
        self.insert("insert", r"\sqrt{}")
        self.editor.mark_set("insert", "insert-1c")
        return "break"