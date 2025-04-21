"""
Preferences dialog for the Simplified Math Editor.

This module provides a dialog for editing application preferences,
including image settings.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path

class PreferencesDialog:
    """Dialog for editing application preferences"""
    
    def __init__(self, parent, config=None, on_save=None):
        """
        Initialize the preferences dialog
        
        Args:
            parent: Parent window
            config (dict, optional): Current configuration dictionary
            on_save (callable, optional): Callback to call when preferences are saved
        """
        self.parent = parent
        self.config = config or {}
        self.on_save = on_save
        
        # Create and show the dialog
        self.create_dialog()
    
    def create_dialog(self):
        """Create the preferences dialog"""
        # Create the dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("Preferences")
        self.dialog.geometry("500x650")  # Increased height for new options
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
        # Create main frame with padding
        main_frame = ttk.Frame(self.dialog, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for different settings categories
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Image settings tab
        image_frame = ttk.Frame(notebook, padding=10)
        notebook.add(image_frame, text="Image Settings")
        
        # Image height setting
        ttk.Label(image_frame, text="Default Max Image Height (pixels):").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Get the current image height configuration or use default
        default_height = self.config.get("image", {}).get("default_max_height", 800)
        
        self.height_var = tk.IntVar(value=default_height)
        height_entry = ttk.Entry(image_frame, textvariable=self.height_var, width=10)
        height_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Add a slider for visual adjustment
        height_slider = ttk.Scale(
            image_frame, 
            from_=100, 
            to=2000, 
            orient=tk.HORIZONTAL, 
            variable=self.height_var, 
            length=300
        )
        height_slider.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Add explanation text
        ttk.Label(image_frame, text="Note: This setting controls the maximum height of images\n"
                                   "when inserted into documents. Images will maintain their\n"
                                   "aspect ratio while being constrained to this height.").grid(
            row=2, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # Caption behavior setting
        ttk.Label(image_frame, text="Default Image Caption Behavior:").grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.caption_var = tk.StringVar(value=self.config.get("image", {}).get("caption_behavior", "none"))
        
        caption_options = ttk.Combobox(
            image_frame, 
            textvariable=self.caption_var,
            values=["none", "empty", "filename"],
            state="readonly",
            width=15
        )
        caption_options.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Add explanation for caption options
        ttk.Label(image_frame, text="none: No caption element\n"
                                   "empty: Include empty caption\n"
                                   "filename: Use filename as caption").grid(
            row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
            
        # Figure indentation setting
        ttk.Label(image_frame, text="Figure Indentation (points):").grid(
            row=5, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Get the current indent configuration or use default
        indent_points = self.config.get("image", {}).get("indent_points", 48)
        self.indent_var = tk.IntVar(value=indent_points)
        indent_entry = ttk.Entry(image_frame, textvariable=self.indent_var, width=10)
        indent_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Add a slider for visual adjustment
        indent_slider = ttk.Scale(
            image_frame, 
            from_=0, 
            to=96,  # Up to 1.33 inches
            orient=tk.HORIZONTAL, 
            variable=self.indent_var, 
            length=300
        )
        indent_slider.grid(row=6, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Add explanation text
        ttk.Label(image_frame, text="Note: This setting controls the indentation of figures from the left margin.\n"
                                   "0 = no indentation, 72 = approximately 1 inch.").grid(
            row=7, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # Editor settings tab
        editor_frame = ttk.Frame(notebook, padding=10)
        notebook.add(editor_frame, text="Editor Settings")
        
        # Default font size
        ttk.Label(editor_frame, text="Editor Font Size:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        font_size = self.config.get("editor", {}).get("font_size", 12)
        self.font_size_var = tk.IntVar(value=font_size)
        
        font_entry = ttk.Entry(editor_frame, textvariable=self.font_size_var, width=5)
        font_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Add a slider for visual adjustment
        font_slider = ttk.Scale(
            editor_frame, 
            from_=8, 
            to=36, 
            orient=tk.HORIZONTAL, 
            variable=self.font_size_var, 
            length=300
        )
        font_slider.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Preview settings tab
        preview_frame = ttk.Frame(notebook, padding=10)
        notebook.add(preview_frame, text="Preview Settings")
        
        # Preview font size
        ttk.Label(preview_frame, text="Preview Font Size:").grid(
            row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        preview_font_size = self.config.get("preview", {}).get("font_size", 16)
        self.preview_font_size_var = tk.IntVar(value=preview_font_size)
        
        preview_font_entry = ttk.Entry(preview_frame, textvariable=self.preview_font_size_var, width=5)
        preview_font_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Add a slider for visual adjustment
        preview_font_slider = ttk.Scale(
            preview_frame, 
            from_=8, 
            to=24, 
            orient=tk.HORIZONTAL, 
            variable=self.preview_font_size_var, 
            length=300
        )
        preview_font_slider.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Preview font family
        ttk.Label(preview_frame, text="Preview Font Family:").grid(
            row=3, column=0, sticky=tk.W, padx=5, pady=5)
        
        preview_font_family = self.config.get("preview", {}).get("font_family", "Carlito")
        # Reset to Computer Modern if currently set to a problematic font
        if preview_font_family in ["Calibri", "Cambria Math"]:
            preview_font_family = "Computer Modern"
        self.preview_font_family_var = tk.StringVar(value=preview_font_family)
        
        font_options = ttk.Combobox(
            preview_frame, 
            textvariable=self.preview_font_family_var,
            values=["Computer Modern", "Times New Roman", "Helvetica", "Courier", "Palatino", "Bookman", "Carlito"],
            state="readonly",
            width=20
        )
        font_options.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        
        # Add explanation for preview font settings
        ttk.Label(preview_frame, text="Note: These settings control the appearance of text in the LaTeX preview.\n"
                                    "Different fonts may display mathematical content differently.\n"
                                    "Computer Modern is the standard LaTeX font.").grid(
            row=4, column=0, columnspan=2, sticky=tk.W, padx=5, pady=10)
        
        # Add explanation about Carlito font
        ttk.Label(preview_frame, text="Note: Carlito is a metrically-compatible alternative to Calibri\n"
                                    "that works well with standard LaTeX.").grid(
            row=5, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Save button
        save_button = ttk.Button(
            button_frame, 
            text="Save", 
            command=self.save_preferences
        )
        save_button.pack(side=tk.RIGHT, padx=5)
        
        # Cancel button
        cancel_button = ttk.Button(
            button_frame, 
            text="Cancel", 
            command=self.dialog.destroy
        )
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
        # Reset to defaults button
        reset_button = ttk.Button(
            button_frame, 
            text="Reset to Defaults", 
            command=self.reset_to_defaults
        )
        reset_button.pack(side=tk.LEFT, padx=5)
        
        # Center the dialog on the parent window
        self.center_dialog()
        
        # Make sure dialog gets closed properly
        self.dialog.protocol("WM_DELETE_WINDOW", self.dialog.destroy)
        
        # Wait for the dialog to be closed
        self.parent.wait_window(self.dialog)
    
    def center_dialog(self):
        """Center the dialog on the parent window"""
        self.dialog.update_idletasks()
        
        # Get parent and dialog dimensions
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        
        dialog_width = self.dialog.winfo_width()
        dialog_height = self.dialog.winfo_height()
        
        # Calculate center position
        x = parent_x + (parent_width - dialog_width) // 2
        y = parent_y + (parent_height - dialog_height) // 2
        
        # Set position
        self.dialog.geometry(f"+{x}+{y}")
    
    def save_preferences(self):
        """Save the preferences and close the dialog"""
        try:
            # Validate inputs
            try:
                # Validate image height
                height = self.height_var.get()
                if height < 50 or height > 5000:
                    raise ValueError("Height must be between 50 and 5000 pixels")
                
                # Validate editor font size
                font_size = self.font_size_var.get()
                if font_size < 8 or font_size > 36:
                    raise ValueError("Editor font size must be between 8 and 36")
                
                # Validate preview font size
                preview_font_size = self.preview_font_size_var.get()
                if preview_font_size < 8 or preview_font_size > 24:
                    raise ValueError("Preview font size must be between 8 and 24")
                
                # Validate figure indentation
                indent_points = self.indent_var.get()
                if indent_points < 0 or indent_points > 144:
                    raise ValueError("Figure indentation must be between 0 and 144 points")
                
            except tk.TclError:
                messagebox.showerror("Invalid Input", "Please enter valid numeric values")
                return
            
            # Update configuration
            if "image" not in self.config:
                self.config["image"] = {}
            
            if "editor" not in self.config:
                self.config["editor"] = {}
                
            if "preview" not in self.config:
                self.config["preview"] = {}
            
            # Update image settings
            self.config["image"]["default_max_height"] = height
            self.config["image"]["caption_behavior"] = self.caption_var.get()
            self.config["image"]["indent_points"] = self.indent_var.get()
            
            # Update editor settings
            self.config["editor"]["font_size"] = font_size
            
            # Update preview settings
            self.config["preview"]["font_size"] = preview_font_size
            self.config["preview"]["font_family"] = self.preview_font_family_var.get()
            
            # Call the save callback if provided
            if self.on_save:
                self.on_save(self.config)
            
            # Close the dialog
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save preferences: {str(e)}")
    
    def reset_to_defaults(self):
        """Reset preferences to default values"""
        if messagebox.askyesno("Reset Defaults", "Are you sure you want to reset all preferences to defaults?"):
            # Reset image settings
            self.height_var.set(800)
            self.caption_var.set("none")
            self.indent_var.set(48)  # Set to your preferred default
            
            # Reset editor settings
            self.font_size_var.set(12)
            
            # Reset preview settings
            self.preview_font_size_var.set(16)  # Set to your preferred default
            self.preview_font_family_var.set("Carlito")  # Set to your preferred default