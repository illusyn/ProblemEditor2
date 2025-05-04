from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import re
import tkinter as tk

# Context-aware font size configuration
FONT_SIZES = {
    "preview": {
        "problem": 14,
        "text": 14,
        "section": 16,
    },
    "export": {
        "problem": 14,
        "text": 14,
        "section": 16,
    }
}

class Command(ABC):
    """Abstract base class for all markdown commands"""
    
    def __init__(self):
        self._parameters: Dict[str, Any] = {
            "vspace": {
                "type": "float",
                "description": "Vertical space after content in em units",
                "default": 1
            }
        }
    
    @property
    def parameters(self) -> Dict[str, Any]:
        """Get command parameters"""
        return self._parameters
    
    @abstractmethod
    def render_markdown(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Render content in markdown format"""
        pass
    
    @abstractmethod
    def render_text(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Render content in plain text format"""
        pass
    
    @abstractmethod
    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        """Render content in LaTeX format"""
        pass

class ContentCommand(Command):
    """Abstract base for content commands, adds indentation support"""
    
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "indent": {
                "type": "float",
                "description": "Left indentation in em units",
                "default": 0.0
            },
            "font_size_pt": {
                "type": "float",
                "description": "Font size in points (pt) for LaTeX output",
                "default": 16.0  # Set your global default here!
            },
            "font_name": {
                "type": "string",
                "description": "Font family name for LaTeX output (e.g., 'Times New Roman', 'Arial')",
                "default": "Calibri"
            },
            "spacing": {
                "type": "float",
                "description": "Vertical space above and below content in em units",
                "default": 0.25
            },
            "line_spacing": {
                "type": "float",
                "description": "Line spacing (baseline skip) in points for LaTeX output. Controls vertical space between lines in a paragraph.",
                "default": None
            }
        })

    def get_default_line_spacing(self, font_size_pt):
        """Return the default line spacing (baseline skip) for this command. Subclasses can override."""
        return round(font_size_pt * 1.5)

class TextCommand(ContentCommand):
    """Basic text command (#text)"""
    
    def render_markdown(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        return f"#text\n{content}"
    
    def render_text(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        indent = " " * int(params.get("indent", self._parameters["indent"]["default"]) * 2)
        return f"{indent}{content}"
    
    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None, context: str = "export") -> str:
        params = params or {}
        indent = params.get("indent", self._parameters["indent"]["default"])
        spacing = params.get('spacing', self._parameters['spacing']['default'])
        # Context-aware font size
        if context == "export":
            font_size_pt = FONT_SIZES.get(context, {}).get("text", 12)
        else:
            font_size_pt = params.get('font_size_pt', FONT_SIZES.get(context, {}).get("text", 12))
        font_name = params.get('font_name', self._parameters.get('font_name', {}).get('default', 'Calibri'))
        line_spacing = params.get('line_spacing', None)
        if line_spacing is None:
            line_spacing = self.get_default_line_spacing(font_size_pt)
        font_cmd = ""
        if font_size_pt and font_size_pt > 0:
            font_cmd += f"\\fontsize{{{font_size_pt}pt}}{{{line_spacing}pt}}\\selectfont "
        if font_name:
            font_cmd += f"\\setmainfont{{{font_name}}} "
        if indent > 0:
            return f"\\vspace{{{spacing}em}}\n\\hspace{{{indent}em}}{font_cmd}{content}\\par\n\\vspace{{{spacing}em}}\n"
        return f"\\vspace{{{spacing}em}}\n{font_cmd}{content}\\par\n\\vspace{{{spacing}em}}\n"

class EnumCommand(TextCommand):
    """Enumerated item command (#enum)"""
    
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "format": {
                "type": "str",
                "description": "Enumeration format (a), 1., etc.)",
                "default": "a)"
            }
        })
        self._state = {"counter": 0}
    
    def render_markdown(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        return f"#enum\n{content}"
    
    def render_text(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        self._state["counter"] += 1
        format_str = params.get("format", self._parameters["format"]["default"])
        # Simple a), b), ... or 1., 2., ...
        if "a" in format_str:
            prefix = format_str.replace("a", chr(96 + self._state["counter"]))
        elif "1" in format_str:
            prefix = format_str.replace("1", str(self._state["counter"]))
        else:
            prefix = format_str
        indent = " " * int(params.get("indent", self._parameters["indent"]["default"]) * 2)
        return f"{indent}{prefix} {content}"
    
    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        vspace = params.get('vspace', self._parameters['vspace']['default'])
        return f"\\item {content}\n\\vspace{{{vspace}em}}"
    
    def reset_state(self):
        self._state["counter"] = 0

class ProblemCommand(ContentCommand):
    """Problem statement command (#problem)"""
    
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "bold": {
                "type": "boolean",
                "description": "Whether to bold the problem statement",
                "default": False
            }
        })
    
    def render_markdown(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        return f"#problem\n{content}"
    
    def render_text(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        if params.get("bold", self._parameters["bold"]["default"]):
            return f"**{content}**"
        return content
    
    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None, context: str = "export") -> str:
        params = params or {}
        spacing = params.get('spacing', self._parameters['spacing']['default'])
        vspace = params.get('vspace', self._parameters['vspace']['default'])
        # Context-aware font size
        if context == "export":
            font_size_pt = FONT_SIZES.get(context, {}).get("problem", 12)
        else:
            font_size_pt = params.get('font_size_pt', FONT_SIZES.get(context, {}).get("problem", 12))
        font_name = params.get('font_name', self._parameters.get('font_name', {}).get('default', ''))
        line_spacing = params.get('line_spacing', None)
        if line_spacing is None:
            line_spacing = self.get_default_line_spacing(font_size_pt)
        font_cmd = ""
        if font_size_pt and font_size_pt > 0:
            font_cmd += f"\\fontsize{{{font_size_pt}pt}}{{{line_spacing}pt}}\\selectfont "
        if font_name:
            font_cmd += f"\\setmainfont{{{font_name}}} "
        # Prepend problem number if provided
        number = params.get('number', None)
        if number is not None:
            content = f"{number}. {content}"
        # Add spacing above and below content
        return f"\\vspace{{{spacing}em}}\n{font_cmd}{content}\\par\n\\vspace{{{spacing}em}}\n"

def parse_latex_settings(self):
    """
    Parse LaTeX code in the editor to extract width, margin, and alignment for this image.
    Returns:
        tuple: (width, left, top, bottom, align)
    """
    content = self.editor.get_content()
    pattern = r'\\adjustbox\{([^}]*)\}\{\\includegraphics\[.*?\]\{' + re.escape(self.filename) + r'\}\}'
    match = re.search(pattern, content)
    width = 0.8
    left = top = bottom = 0.0
    align = 'left'
    if match:
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
            parts = margin_str.split()
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
    return width, left, top, bottom, align 