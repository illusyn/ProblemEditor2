#!/usr/bin/env python3
"""
Main application entry point for the Simplified Math Editor.

This module sets up the main application window with support for custom markdown.
"""

import tkinter as tk
from math_editor import MathEditor

# Import the database module and interface
from math_db import MathProblemDB
from db_interface import DatabaseInterface

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