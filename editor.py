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
        
        # Bind events
        self.editor.bind("<Button-3>", self.show_context_menu)
        self.editor.bind("<Control-l>", lambda e: self.paste_latex())
        
        # Configure tags for syntax highlighting
        self.editor.tag_configure("command", foreground="blue")
        self.editor.tag_configure("parameter", foreground="green")
        self.editor.tag_configure("equation", foreground="purple")
        
        # Bind syntax highlighting
        self.editor.bind("<KeyRelease>", self.highlight_syntax)
    
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