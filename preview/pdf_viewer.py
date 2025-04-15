"""
PDF viewer component for the Simplified Math Editor.

This module provides functionality to display compiled PDF documents
within the application.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os

# Check if pdf2image is available and import it
try:
    from pdf2image import convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

class PDFViewer:
    """Component for displaying PDF files in the application"""
    
    def __init__(self, parent):
        """
        Initialize the PDF viewer
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        
        # Initialize viewer state
        self.current_pdf = None
        self.zoom_level = 1.0  # 100% zoom
        self.images = []  # Store references to prevent garbage collection
        
        # Create the viewer widget
        self.create_viewer()
        
        # Check PDF viewing dependencies
        self.check_dependencies()
    
    def create_viewer(self):
        """Create the PDF viewer widget"""
        # Create main frame
        self.frame = ttk.Frame(self.parent)
        self.frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Toolbar for viewer controls
        self.toolbar = ttk.Frame(self.frame)
        self.toolbar.pack(fill=tk.X, padx=5, pady=5)
        
        # Zoom controls
        ttk.Label(self.toolbar, text="Zoom:").pack(side=tk.LEFT, padx=5)
        
        self.zoom_out_btn = ttk.Button(self.toolbar, text="-", width=2, command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT)
        
        self.zoom_var = tk.StringVar(value="100%")
        zoom_label = ttk.Label(self.toolbar, textvariable=self.zoom_var, width=5)
        zoom_label.pack(side=tk.LEFT, padx=5)
        
        self.zoom_in_btn = ttk.Button(self.toolbar, text="+", width=2, command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT)
        
        # Canvas and scrollbar for PDF display
        self.canvas_frame = ttk.Frame(self.frame)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create scrollable canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.scrollbar_y = ttk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        
        # Configure canvas scrolling
        self.canvas.configure(yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set)
        
        # Pack scrollbars and canvas
        self.scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Frame inside canvas for PDF content
        self.pdf_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.pdf_frame, anchor=tk.NW)
        
        # Configure scrolling behavior
        self.pdf_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Status message
        self.status_var = tk.StringVar(value="PDF Preview")
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var, anchor=tk.W)
        self.status_label.pack(fill=tk.X, padx=5, pady=2)
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        if not PDF2IMAGE_AVAILABLE:
            self.status_var.set("Warning: pdf2image not installed. PDF preview not available.")
            messagebox.showwarning(
                "Missing Dependencies",
                "The pdf2image library is required for PDF preview.\n\n"
                "Install it with: pip install pdf2image\n\n"
                "You may also need to install poppler for your operating system."
            )
    
    def on_frame_configure(self, event=None):
        """Update the scrollregion when the frame changes size"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event=None):
        """Update the canvas window width when the canvas changes size"""
        if event:
            width = event.width
            self.canvas.itemconfig(self.canvas_window, width=width)
    
    def display_pdf(self, pdf_path):
        """
        Display a PDF file in the viewer
        
        Args:
            pdf_path (str): Path to the PDF file
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not PDF2IMAGE_AVAILABLE:
            self.status_var.set("Error: pdf2image library not available")
            return False
        
        if not os.path.exists(pdf_path):
            self.status_var.set(f"Error: PDF file not found at {pdf_path}")
            return False
        
        try:
            # Store the current PDF path
            self.current_pdf = pdf_path
            
            # Clear existing content
            for widget in self.pdf_frame.winfo_children():
                widget.destroy()
            
            # Clear image references
            self.images = []
            
            # Convert PDF to images
            dpi = int(100 * self.zoom_level)  # Base DPI = 100
            images = convert_from_path(pdf_path, dpi=dpi)
            
            # Display each page
            for i, img in enumerate(images):
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(img)
                self.images.append(photo)  # Keep reference
                
                # Display image
                img_label = ttk.Label(self.pdf_frame, image=photo)
                img_label.pack(pady=10)
                
                # Add separator between pages
                if i < len(images) - 1:
                    ttk.Separator(self.pdf_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=5)
            
            # Update canvas scroll region
            self.on_frame_configure()
            
            # Update status
            self.status_var.set(f"Displaying PDF: {os.path.basename(pdf_path)}")
            return True
            
        except Exception as e:
            self.status_var.set(f"Error displaying PDF: {str(e)}")
            return False
    
    def zoom_in(self):
        """Increase zoom level"""
        if self.zoom_level < 2.0:  # Limit maximum zoom
            self.zoom_level += 0.25
            self.zoom_var.set(f"{int(self.zoom_level * 100)}%")
            
            # Refresh the current PDF with new zoom level
            if self.current_pdf:
                self.display_pdf(self.current_pdf)
    
    def zoom_out(self):
        """Decrease zoom level"""
        if self.zoom_level > 0.5:  # Limit minimum zoom
            self.zoom_level -= 0.25
            self.zoom_var.set(f"{int(self.zoom_level * 100)}%")
            
            # Refresh the current PDF with new zoom level
            if self.current_pdf:
                self.display_pdf(self.current_pdf)
    
    def clear(self):
        """Clear the viewer"""
        for widget in self.pdf_frame.winfo_children():
            widget.destroy()
        
        self.images = []
        self.current_pdf = None
        self.status_var.set("PDF Preview")