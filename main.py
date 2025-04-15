#!/usr/bin/env python3
"""
Main application entry point for the Simplified Math Editor.

This module sets up the main application window.
"""

import tkinter as tk
from math_editor import MathEditor

def main():
    """Application entry point"""
    root = tk.Tk()
    app = MathEditor(root)
    root.mainloop()

if __name__ == "__main__":
    main()