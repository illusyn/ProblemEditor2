from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

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
            }
        })

class TextCommand(ContentCommand):
    """Basic text command (#text)"""
    
    def render_markdown(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        return f"#text\n{content}"
    
    def render_text(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        indent = " " * int(params.get("indent", self._parameters["indent"]["default"]) * 2)
        return f"{indent}{content}"
    
    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        indent = params.get("indent", self._parameters["indent"]["default"])
        vspace = params.get('vspace', self._parameters['vspace']['default'])
        if indent > 0:
            return f"\\hspace{{{indent}em}}{content}\\par\n\\vspace{{{vspace}em}}\n"
        return f"{content}\\par\n\\vspace{{{vspace}em}}\n"

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
    
    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        vspace = params.get('vspace', self._parameters['vspace']['default'])
        if params.get("bold", self._parameters["bold"]["default"]):
            return f"\\textbf{{{content}}}\\par\n\\vspace{{{vspace}em}}\n"
        return f"{content}\\par\n\\vspace{{{vspace}em}}\n" 