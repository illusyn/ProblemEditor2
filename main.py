#!/usr/bin/env python3
"""
Main application entry point for the Simplified Math Editor.

This module sets up the main application window with support for custom markdown.
"""

import tkinter as tk
from math_editor import MathEditor

# Import the markdown parser directly - this was missing or incorrectly imported
try:
    from markdown_parser import MarkdownParser
except ImportError:
    print("Warning: MarkdownParser not found. Make sure markdown_parser.py is in the correct location.")
    # Create a stub class as a fallback
    class MarkdownParser:
        def __init__(self):
            pass
        def parse(self, text):
            return text

def main():
    """Application entry point"""
    # Create the main window
    root = tk.Tk()
    
    # Set application title
    root.title("Simplified Math Editor")
    
    # Create the application instance
    app = MathEditor(root)
    
    # Start the main event loop
    root.mainloop()

if __name__ == "__main__":
    main()