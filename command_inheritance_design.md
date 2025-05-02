# Command Inheritance System Design

This document outlines the design of a robust command inheritance system using Python's class inheritance features.

## Core Design

The system uses an abstract base class to define the fundamental structure of commands, with concrete implementations inheriting and extending this base functionality.

### Base Command Structure

```python
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class AbstractCommand(ABC):
    def __init__(self):
        self._parameters: Dict[str, Any] = {
            "vspace": {
                "type": "string",
                "description": "Vertical space after content",
                "default": "1em"
            },
            "label": {
                "type": "string",
                "description": "Label for referencing",
                "default": None
            }
        }
        # Default template wraps content in an environment and adds vertical space
        self._env_name: str = "text"  # Default environment name, should be overridden
        self._template: str = (
            "\\begin{#ENV_NAME#}#LABEL_PART#\n"
            "#CONTENT#\n"
            "\\end{#ENV_NAME#}\n"
            "\\vspace{#vspace#}"
        )
    
    @property
    def parameters(self) -> Dict[str, Any]:
        return self._parameters
    
    @property
    def template(self) -> str:
        return self._template
    
    def _get_label_part(self) -> str:
        """Generate the label part of the template if label is provided"""
        if self._parameters["label"]["default"]:
            return f"[label={self._parameters['label']['default']}]"
        return ""
    
    @abstractmethod
    def validate_content(self, content: str) -> bool:
        """Validate if the content meets command requirements"""
        pass

    def render(self, content: str, params: Dict[str, Any]) -> str:
        """Render the content with the given parameters"""
        if not self.validate_content(content):
            raise ValueError("Invalid content")
        
        # Replace template placeholders
        rendered = self._template.replace("#ENV_NAME#", self._env_name)
        rendered = rendered.replace("#CONTENT#", content)
        rendered = rendered.replace("#LABEL_PART#", self._get_label_part())
        
        # Replace parameter values
        for param, value in params.items():
            rendered = rendered.replace(f"#{param}#", str(value))
        
        return rendered
```

### Concrete Command Implementation

Specific commands inherit from the base class:

```python
class ProblemCommand(AbstractCommand):
    def __init__(self):
        super().__init__()
        self._env_name = "problem"
        # Add problem-specific parameters
        self._parameters.update({
            "difficulty": {
                "type": "integer",
                "description": "Problem difficulty level",
                "default": 1
            }
        })
        # Customize template to include difficulty
        self._template = (
            "\\begin{#ENV_NAME#}[difficulty=#difficulty#]#LABEL_PART#\n"
            "#CONTENT#\n"
            "\\end{#ENV_NAME#}\n"
            "\\vspace{#vspace#}"
        )
    
    def validate_content(self, content: str) -> bool:
        """Validate problem content"""
        return isinstance(content, str) and len(content.strip()) > 0

class NoteCommand(AbstractCommand):
    def __init__(self):
        super().__init__()
        self._env_name = "note"
        # Uses default template and parameters
    
    def validate_content(self, content: str) -> bool:
        """Validate note content"""
        return isinstance(content, str) and len(content.strip()) > 0

class ImportantNoteCommand(NoteCommand):
    def __init__(self):
        super().__init__()
        self._env_name = "important-note"
        # Add importance level parameter
        self._parameters.update({
            "importance": {
                "type": "integer",
                "description": "Level of importance (1-3)",
                "default": 1
            }
        })
        # Customize template to include importance level
        self._template = (
            "\\begin{#ENV_NAME#}[importance=#importance#]#LABEL_PART#\n"
            "#CONTENT#\n"
            "\\end{#ENV_NAME#}\n"
            "\\vspace{#vspace#}"
        )
    
    def validate_content(self, content: str) -> bool:
        """Validate important note content"""
        # Use parent validation and add additional checks
        basic_valid = super().validate_content(content)
        return basic_valid and len(content) >= 10  # Important notes should be substantial
```

## Advanced Features

### Parameter Inheritance Control

```python
class CommandParameter:
    def __init__(self, type: str, description: str, default: Any):
        self.type = type
        self.description = description
        self.default = default

class AbstractCommand(ABC):
    def inherit_parameters(self, exclude: Optional[List[str]] = None):
        """Inherit parameters from parent class except those in exclude list"""
        pass
```

### Template Composition

```python
class AbstractCommand(ABC):
    def compose_template(self, content_template: str) -> str:
        """Compose a new template by wrapping content_template with base template"""
        pass
```

## Advantages

1. **Unified Structure**: All commands follow the same environment-based pattern with consistent spacing.
2. **Encapsulation**: Each command encapsulates its environment name, parameters, and template.
3. **Validation**: Supports custom validation logic for each command type.
4. **Extensibility**: Easy addition of new command types through inheritance.
5. **Maintainability**: Clear class hierarchy with common base functionality.
6. **Flexibility**: Commands can override default behavior while maintaining consistency.

## Implementation Notes

- All content is wrapped in environments for consistent structure
- Vertical spacing is handled uniformly after each environment
- Labels are optional but consistently supported
- Template rendering is standardized but customizable
- Parameter inheritance is controlled and explicit

### Command Inheritance Examples

Commands can inherit from either `AbstractCommand` or from concrete commands:

1. Direct inheritance from `AbstractCommand`:
   - `ProblemCommand`: Creates basic problem environments
   - `NoteCommand`: Creates basic note environments

2. Inheritance from concrete commands:
   - `ImportantNoteCommand` (inherits from `NoteCommand`):
     - Inherits all note functionality
     - Adds importance level parameter
     - Strengthens content validation
     - Customizes the environment name

This hierarchical inheritance allows for:
- Reuse of common functionality
- Progressive specialization of commands
- Inheritance of validation rules
- Extension of parameters and templates 