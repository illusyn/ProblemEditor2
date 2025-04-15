"""
Core editor component for the Simplified Math Editor.

This module provides the main text editing functionality with support for
MathML pasting, custom markdown syntax, and highlighting.
"""

import tkinter as tk
from tkinter import scrolledtext, messagebox
import re

from converters.mathml_converter import MathMLConverter

class EditorComponent:
    """Text editing area with support for MathML conversion and syntax highlighting"""
    
    def __init__(self, parent, font_size=12):
        """
        Initialize the editor component
        
        Args:
            parent: Parent widget
            font_size (int): Font size for the editor
        """
        self.parent = parent
        self.font_size = font_size
        
        # Initialize editor font
        self.editor_font = ('Courier', self.font_size)
        
        # Create the editor widget
        self.create_editor()
        
        # Initialize the MathML converter
        self.mathml_converter = MathMLConverter()
        
        # Set up context menu
        self.create_context_menu()
        
        # Set up keyboard shortcuts
        self.bind_shortcuts()
    
    def create_editor(self):
        """Create the editor widget"""
        # Text editor frame
        self.editor_frame = tk.Frame(self.parent)
        self.editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Text editor with scrollbar
        self.editor = scrolledtext.ScrolledText(
            self.editor_frame,
            wrap=tk.WORD,
            undo=True,
            font=self.editor_font,
            background="white",
            foreground="black",
            insertbackground="black"
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Add syntax highlighting through tags
        self.editor.tag_configure("equation", foreground="blue")
        self.editor.tag_configure("command", foreground="green", font=(self.editor_font[0], self.editor_font[1], "bold"))
        self.editor.tag_configure("question", foreground="red")
        self.editor.tag_configure("bullet", foreground="purple")
        self.editor.tag_configure("section", foreground="darkblue", font=(self.editor_font[0], self.editor_font[1], "bold"))
        
        # Bind events for syntax highlighting
        self.editor.bind("<KeyRelease>", self.highlight_syntax)
    
    def create_context_menu(self):
        """Create right-click context menu"""
        self.context_menu = tk.Menu(self.parent, tearoff=0)
        self.context_menu.add_command(label="Cut", command=self.cut_text)
        self.context_menu.add_command(label="Copy", command=self.copy_text)
        self.context_menu.add_command(label="Paste", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Paste MathML as LaTeX", command=self.paste_mathml)
        self.context_menu.add_separator()
        
        # Add markdown commands submenu
        markdown_menu = tk.Menu(self.context_menu, tearoff=0)
        markdown_menu.add_command(label="Problem Section", command=self.insert_problem_section)
        markdown_menu.add_command(label="Solution Section", command=self.insert_solution_section)
        markdown_menu.add_command(label="Question", command=self.insert_question)
        markdown_menu.add_command(label="Equation", command=self.insert_equation)
        markdown_menu.add_command(label="Aligned Equations", command=self.insert_aligned_equations)
        markdown_menu.add_command(label="Bullet Point", command=self.insert_bullet_point)
        
        self.context_menu.add_cascade(label="Insert Markdown", menu=markdown_menu)
        
        # Bind right-click to show context menu
        self.editor.bind("<Button-3>", self.show_context_menu)
    
    def bind_shortcuts(self):
        """Set up keyboard shortcuts"""
        # Standard shortcuts
        self.editor.bind("<Control-c>", lambda e: self.copy_text())
        self.editor.bind("<Control-x>", lambda e: self.cut_text())
        self.editor.bind("<Control-v>", lambda e: self.paste_text())
        self.editor.bind("<Control-z>", lambda e: self.editor.edit_undo())
        self.editor.bind("<Control-y>", lambda e: self.editor.edit_redo())
        
        # Custom shortcuts
        self.editor.bind("<Control-m>", lambda e: self.paste_mathml())
        self.editor.bind("<Control-p>", lambda e: self.insert_problem_section())
        self.editor.bind("<Control-s>", lambda e: self.insert_solution_section())
        self.editor.bind("<Control-q>", lambda e: self.insert_question())
        self.editor.bind("<Control-e>", lambda e: self.insert_equation())
    
    def show_context_menu(self, event):
        """Show the context menu at the current mouse position"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()
    
    def cut_text(self):
        """Cut selected text to clipboard"""
        try:
            self.editor.event_generate("<<Cut>>")
        except:
            pass  # Ignore if nothing selected
    
    def copy_text(self):
        """Copy selected text to clipboard"""
        try:
            self.editor.event_generate("<<Copy>>")
        except:
            pass  # Ignore if nothing selected
    
    def paste_text(self):
        """Paste text from clipboard"""
        try:
            self.editor.event_generate("<<Paste>>")
        except:
            pass
    
    def paste_mathml(self):
        """Paste MathML from clipboard as LaTeX"""
        try:
            # Get clipboard content
            clipboard_content = self.editor.clipboard_get()
            if not clipboard_content:
                messagebox.showinfo("Clipboard Empty", "No text found in clipboard.")
                return
            
            # Check if content looks like MathML (simple check)
            if '<math' not in clipboard_content:
                if not messagebox.askyesno(
                    "Not MathML", 
                    "Clipboard content doesn't appear to be MathML. Try to convert anyway?"
                ):
                    return
            
            # Convert to LaTeX
            latex = self.mathml_converter.convert(clipboard_content)
            
            # Format as an equation
            formatted_latex = self.mathml_converter.format_as_equation(latex)
            
            # Insert at cursor position
            self.editor.insert(tk.INSERT, formatted_latex)
            
            # Highlight the newly inserted equation
            self.highlight_syntax()
            
        except tk.TclError:
            # Empty clipboard or not text content
            messagebox.showinfo("Clipboard Empty", "No text found in clipboard.")
        except Exception as e:
            messagebox.showerror("Conversion Error", str(e))

    def paste_latex(self):
        """Paste LaTeX from clipboard and format as equation"""
        try:
            # Get clipboard content
            clipboard_content = self.editor.clipboard_get()
            if not clipboard_content:
                messagebox.showinfo("Clipboard Empty", "No text found in clipboard.")
                return
            
            # Format as an equation
            formatted_latex = self.mathml_converter.format_as_equation(clipboard_content)
            
            # Insert at cursor position
            self.editor.insert(tk.INSERT, formatted_latex)
            
            # Highlight the newly inserted equation
            self.highlight_syntax()
            
        except tk.TclError:
            # Empty clipboard or not text content
            messagebox.showinfo("Clipboard Empty", "No text found in clipboard.")
        except Exception as e:
            messagebox.showerror("Conversion Error", str(e))
    
    def insert_problem_section(self):
        """Insert a problem section marker"""
        self.editor.insert(tk.INSERT, "\n#problem\n")
        self.highlight_syntax()
    
    def insert_solution_section(self):
        """Insert a solution section marker"""
        self.editor.insert(tk.INSERT, "\n#solution\n")
        self.highlight_syntax()
    
    def insert_question(self):
        """Insert a question marker"""
        self.editor.insert(tk.INSERT, "\n#question\n")
        self.highlight_syntax()
    
    def insert_equation(self):
        """Insert an equation marker"""
        self.editor.insert(tk.INSERT, "\n#eq\n")
        self.highlight_syntax()
    
    def insert_aligned_equations(self):
        """Insert an aligned equations marker"""
        self.editor.insert(tk.INSERT, "\n#align\n")
        self.highlight_syntax()
    
    def insert_bullet_point(self):
        """Insert a bullet point marker"""
        self.editor.insert(tk.INSERT, "\n#bullet ")
        self.highlight_syntax()

    def highlight_syntax(self, event=None):
        """Apply syntax highlighting to the editor content"""
        # Remove existing tags
        for tag in ["equation", "command", "question", "bullet", "section"]:
            self.editor.tag_remove(tag, "1.0", tk.END)
        
        # Highlight equations (text between \[ and \])
        start_idx = "1.0"
        while True:
            eq_start = self.editor.search(r"\[", start_idx, tk.END, regexp=True)
            if not eq_start:
                break
                
            eq_end = self.editor.search(r"\]", eq_start, tk.END, regexp=True)
            if not eq_end:
                break
                
            eq_end = f"{eq_end}+2c"  # Include the closing \]
            self.editor.tag_add("equation", eq_start, eq_end)
            start_idx = eq_end
        
        # Highlight custom markdown commands
        start_idx = "1.0"
        while True:
            cmd_start = self.editor.search(r"^#\w+", start_idx, tk.END, regexp=True)
            if not cmd_start:
                break
                
            line_end = cmd_start.split('.')[0] + ".end"
            cmd_end = self.editor.search(r"\s", cmd_start, line_end)
            if not cmd_end:
                cmd_end = line_end
            
            # Get the command text
            cmd_text = self.editor.get(cmd_start, cmd_end)
            
            # Apply appropriate tag based on command
            if cmd_text == "#problem" or cmd_text == "#solution":
                self.editor.tag_add("section", cmd_start, cmd_end)
            elif cmd_text == "#question":
                self.editor.tag_add("question", cmd_start, cmd_end)
            elif cmd_text == "#eq" or cmd_text == "#align":
                self.editor.tag_add("equation", cmd_start, cmd_end)
            elif cmd_text.startswith("#bullet"):
                self.editor.tag_add("bullet", cmd_start, cmd_end)
            else:
                self.editor.tag_add("command", cmd_start, cmd_end)
                
            start_idx = line_end + "+1c"
    
    def get_content(self):
        """Get the current editor content"""
        return self.editor.get("1.0", tk.END)
    
    def set_content(self, content):
        """Set the editor content"""
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", content)
        self.highlight_syntax()
    
    def increase_font_size(self):
        """Increase the editor font size"""
        self.font_size += 2
        self.editor_font = ('Courier', self.font_size)
        self.editor.configure(font=self.editor_font)
    
    def decrease_font_size(self):
        """Decrease the editor font size"""
        if self.font_size > 8:
            self.font_size -= 2
            self.editor_font = ('Courier', self.font_size)
            self.editor.configure(font=self.editor_font)