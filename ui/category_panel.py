"""
Category panel component for the Simplified Math Editor.

This module provides a UI component that displays a scrollable grid of category
buttons that can be clicked to select or filter by category.
"""

import tkinter as tk
from tkinter import Frame, Button, Canvas, Scrollbar


class CategoryPanel:
    """UI component that displays a grid of category buttons"""
    
    def __init__(self, parent):
        """
        Initialize the category panel
        
        Args:
            parent: Parent widget
        """
        # Create a frame that contains both canvas and scrollbar
        self.container = Frame(parent)
        self.container.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Add a scrollbar
        self.scrollbar = Scrollbar(self.container, orient=tk.VERTICAL)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create canvas with scrollbar - significantly increased width
        self.canvas = Canvas(self.container, yscrollcommand=self.scrollbar.set, width=330)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.scrollbar.config(command=self.canvas.yview)
        
        # Create frame inside canvas for buttons
        self.frame = Frame(self.canvas)
        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor=tk.NW)
        
        # Configure canvas to resize with window and update scrollregion
        self.frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Set a fixed height to accommodate more rows with the new compact buttons
        # With the reduced button height, we can now fit approximately 18-20 rows (36-40 categories in 2 columns)
        self.canvas.config(height=460)  # Keeping the same height but with more compact buttons
        
        # Only show scrollbar when needed
        self.scrollbar.pack_forget()  # Hide scrollbar initially
        
        self.buttons = {}
        self.on_click_callback = None
        self.multi_select_mode = False
        self.selected_categories = set()

    def _on_frame_configure(self, event):
        """Update the scrollregion when the frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Show scrollbar only if content exceeds canvas height
        if self.frame.winfo_reqheight() > self.canvas.winfo_height():
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            self.scrollbar.pack_forget()  # Hide scrollbar
    
    def _on_canvas_configure(self, event):
        """Update the width of the frame when the canvas changes size"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width)
        
        # Check if scrollbar is needed after resize
        if self.frame.winfo_reqheight() > event.height:
            self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            self.scrollbar.pack_forget()  # Hide scrollbar

    def set_on_category_click_callback(self, callback):
        """
        Set a callback function to be called when a category is clicked
        
        Args:
            callback: Function to call, which should accept a category name parameter
        """
        self.on_click_callback = callback

    def set_multi_select(self, enabled: bool):
        """
        Set whether multiple categories can be selected
        
        Args:
            enabled: True to enable multi-select, False for single-select
        """
        self.multi_select_mode = enabled
        self.selected_categories.clear()
        for cat, btn in self.buttons.items():
            btn.configure(bg="SystemButtonFace")

    def update_display(self, categories):
        """
        Update the display with a new list of categories
        
        Args:
            categories: List of category names
        """
        for widget in self.frame.winfo_children():
            widget.destroy()

        self.buttons = {}
        
        col_count = 2  # Keep 2 columns
        
        # Further reduced button size for more compact display
        for idx, cat in enumerate(categories):
            btn = Button(self.frame, text=cat, relief=tk.RAISED, width=23, anchor="w", 
                         padx=1, pady=0)  # Increased width from 17 to 23
            btn.configure(height=0)  # Smallest possible height
            btn.config(borderwidth=1)  # Reduced border width
            btn.grid(row=idx // col_count, column=idx % col_count, sticky="ew", padx=1, pady=0)  # Reduced padding between rows
            btn.configure(command=lambda c=cat: self._on_category_click(c))
            self.buttons[cat] = btn
            
            # Set initial state based on selected_categories
            if cat in self.selected_categories:
                btn.configure(bg="#cccccc")
            else:
                btn.configure(bg="SystemButtonFace")
        
        # Force update to ensure scrollbar visibility is correct
        self.frame.update_idletasks()
        self._on_frame_configure(None)

    def _on_category_click(self, category):
        """
        Handle category button click
        
        Args:
            category: Name of the category that was clicked
        """
        if self.multi_select_mode:
            # Grid View toggle behavior
            if category in self.selected_categories:
                self.selected_categories.remove(category)
                self.buttons[category].configure(bg="SystemButtonFace")
            else:
                self.selected_categories.add(category)
                self.buttons[category].configure(bg="#cccccc")
            if self.on_click_callback:
                self.on_click_callback(category)
        else:
            # Single View behavior
            if self.on_click_callback:
                self.on_click_callback(category)
                
    def highlight_category(self, category, selected):
        """
        Highlight or unhighlight a specific category button
        
        Args:
            category: Name of the category
            selected: True to highlight, False to unhighlight
        """
        if category in self.buttons:
            if selected:
                self.buttons[category].configure(bg="#cccccc")
            else:
                self.buttons[category].configure(bg="SystemButtonFace")

    def get_selected_categories(self):
        """
        Get the list of currently selected categories
        
        Returns:
            list: Names of selected categories
        """
        return list(self.selected_categories)