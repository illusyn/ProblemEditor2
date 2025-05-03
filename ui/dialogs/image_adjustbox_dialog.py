"""
Adjustbox-based Image Adjustment Dialog for the Simplified Math Editor.

This dialog allows users to adjust LaTeX width (scale), margin, and alignment for an image,
with live preview and persistent settings in the LaTeX code.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import re

class AdjustboxImageDialog:
    """Dialog for adjusting LaTeX adjustbox options for an image with live preview."""
    def __init__(self, parent, editor, image_manager, image_filename):
        """
        Initialize the adjustbox image dialog.

        Args:
            parent: Parent widget
            editor: Editor component to update
            image_manager: The ImageManager instance
            image_filename (str): Filename of the image to adjust
        """
        self.parent = parent
        self.editor = editor
        self.image_manager = image_manager
        self.filename = image_filename

        # Parse current LaTeX settings for this image
        self.width, left, top, bottom, self.align = self.parse_latex_settings()
        self.left_margin_var = tk.DoubleVar(value=left)
        self.top_margin_var = tk.DoubleVar(value=top)
        self.bottom_margin_var = tk.DoubleVar(value=bottom)

        # Get image for preview
        success, image = image_manager.app.image_converter.image_db.get_image(image_filename)
        self.image = image if success else None

        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Adjust Image (adjustbox)")
        self.dialog.geometry("500x600")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Tkinter variables
        self.width_var = tk.DoubleVar(value=self.width)
        self.margin_var = tk.StringVar(value=self.align)

        # Build UI
        self.create_widgets()
        self.update_preview()

        # Wait for dialog to close
        parent.wait_window(self.dialog)

    def parse_latex_settings(self):
        """
        Parse LaTeX code in the editor to extract width, margin, and alignment for this image.
        Returns:
            tuple: (width, left, top, bottom, align)
        """
        content = self.editor.get_content()
        pattern = r'\\adjustbox\{([^}]*)\}\s*\{\s*\\includegraphics\[.*?\]\{' + re.escape(self.filename) + r'\}\s*\}'
        print("Searching for pattern:", pattern)
        print("Content:", content)
        match = re.search(pattern, content, re.DOTALL)
        width = 0.8
        left = top = bottom = 0.0
        align = 'left'
        if match:
            print("Matched options:", match.group(1))
            opts = match.group(1)
            # Parse width
            width_match = re.search(r'width=([0-9.]+)\\textwidth', opts)
            if width_match:
                try:
                    width = float(width_match.group(1))
                except Exception:
                    width = 0.8
            # Parse margin
            margin_match = re.search(r'margin=([^,}]+)', opts)
            if margin_match:
                margin_str = margin_match.group(1)
                print("Margin string:", margin_str)
                parts = margin_str.split()
                print("Margin parts:", parts)
                if len(parts) == 4:
                    try:
                        left = float(parts[0].replace('cm', ''))
                        bottom = float(parts[1].replace('cm', ''))
                        # right = float(parts[2].replace('cm', ''))  # ignored
                        top = float(parts[3].replace('cm', ''))
                    except Exception:
                        left = top = bottom = 0.0
            # Parse align
            for a in ['left', 'center', 'right']:
                if a in opts:
                    align = a
                    break
        else:
            print("No match found for adjustbox pattern.")
        return width, left, top, bottom, align

    def create_widgets(self):
        """Create dialog widgets."""
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        # Scale (width) spinbox
        ttk.Label(frame, text="Scale (width, 0.1–1.0 × text width):").pack(anchor=tk.W, padx=5, pady=5)
        width_spin = ttk.Spinbox(frame, from_=0.1, to=1.0, increment=0.01, textvariable=self.width_var, width=6, format="%.2f")
        width_spin.pack(anchor=tk.W, padx=5, pady=5)

        # Left margin spinbox
        ttk.Label(frame, text="Left margin (cm):").pack(anchor=tk.W, padx=5, pady=5)
        left_margin_spin = ttk.Spinbox(frame, from_=0.0, to=3.0, increment=0.1, textvariable=self.left_margin_var, width=6, format="%.2f")
        left_margin_spin.pack(anchor=tk.W, padx=5, pady=5)

        # Top margin spinbox
        ttk.Label(frame, text="Top margin (cm):").pack(anchor=tk.W, padx=5, pady=5)
        top_margin_spin = ttk.Spinbox(frame, from_=0.0, to=3.0, increment=0.1, textvariable=self.top_margin_var, width=6, format="%.2f")
        top_margin_spin.pack(anchor=tk.W, padx=5, pady=5)

        # Bottom margin spinbox
        ttk.Label(frame, text="Bottom margin (cm):").pack(anchor=tk.W, padx=5, pady=5)
        bottom_margin_spin = ttk.Spinbox(frame, from_=0.0, to=3.0, increment=0.1, textvariable=self.bottom_margin_var, width=6, format="%.2f")
        bottom_margin_spin.pack(anchor=tk.W, padx=5, pady=5)

        # Preview
        ttk.Label(frame, text="Preview:").pack(anchor=tk.W, padx=5, pady=5)
        preview_frame = ttk.Frame(frame)
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.preview_label = ttk.Label(preview_frame)
        self.preview_label.pack(expand=True)

        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, pady=10)
        apply_button = ttk.Button(button_frame, text="Apply", command=self.on_apply)
        apply_button.pack(side=tk.RIGHT, padx=5)
        close_button = ttk.Button(button_frame, text="Close", command=self.dialog.destroy)
        close_button.pack(side=tk.RIGHT, padx=5)

        # Bind events for live preview
        self.width_var.trace_add("write", lambda *args: self.update_preview())
        self.left_margin_var.trace_add("write", lambda *args: self.update_preview())
        self.top_margin_var.trace_add("write", lambda *args: self.update_preview())
        self.bottom_margin_var.trace_add("write", lambda *args: self.update_preview())

    def update_preview(self):
        """Update the image preview."""
        if not self.image:
            return
        # Scale preview width according to width_var (simulate LaTeX width)
        width_factor = self.width_var.get()
        orig_w, orig_h = self.image.size
        preview_w = int(400 * width_factor)  # 400 is max preview width
        preview_h = int(orig_h * (preview_w / orig_w)) if orig_w > 0 else 1
        preview_img = self.image.copy().resize((preview_w, preview_h), Image.LANCZOS)
        photo = ImageTk.PhotoImage(preview_img)
        self.dialog.photo = photo
        self.preview_label.config(image=photo)

    def on_apply(self):
        """Apply the current settings to the LaTeX code in the editor and refresh preview."""
        width = self.width_var.get()
        left_margin = self.left_margin_var.get()
        top_margin = self.top_margin_var.get()
        bottom_margin = self.bottom_margin_var.get()
        # Compose margin string (left, bottom, right=0, top)
        margin = f"{left_margin:.2f}cm {bottom_margin:.2f}cm 0cm {top_margin:.2f}cm"
        align = self.margin_var.get().strip() or 'left'
        # Compose adjustbox options
        adjustbox_opts = [f"width={width:.2f}\\textwidth"]
        if align:
            adjustbox_opts.append(align)
        # Only add margin if any value is nonzero
        if left_margin > 0 or top_margin > 0 or bottom_margin > 0:
            adjustbox_opts.append(f"margin={margin}")
        adjustbox_opts_str = ",".join(adjustbox_opts)
        # Compose new LaTeX tag
        new_tag = f"\\adjustbox{{{adjustbox_opts_str}}}{{\\includegraphics[keepaspectratio]{{{self.filename}}}}}"
        # Replace in editor content
        content = self.editor.get_content()
        pattern = r'\\adjustbox\{[^}]*\}\{\\includegraphics\[.*?\]\{' + re.escape(self.filename) + r'\}\}'
        new_content, count = re.subn(pattern, lambda m: new_tag, content)
        if count == 0:
            pattern2 = r'\\includegraphics\[.*?\]\{' + re.escape(self.filename) + r'\}'
            new_content, count = re.subn(pattern2, lambda m: new_tag, content)
        print("Old content:", content)
        print("New tag:", new_tag)
        print("Count of replacements:", count)
        if count > 0:
            self.editor.set_content(new_content)
            if hasattr(self.editor, 'update_preview'):
                self.editor.update_preview()
            elif hasattr(self.image_manager, 'app') and hasattr(self.image_manager.app, 'update_preview'):
                self.image_manager.app.update_preview()
            print("Content updated and preview triggered.")
        else:
            messagebox.showerror("Error", "Could not locate the image in the document for updating.") 