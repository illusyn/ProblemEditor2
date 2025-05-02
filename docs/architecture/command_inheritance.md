# Command Inheritance Architecture

## Overview

The command inheritance system provides a flexible and extensible way to create specialized commands while maintaining consistent behavior and reducing code duplication.

## Inheritance Hierarchy

```
Command (ABC)
├── ContentCommand (ABC)
│   ├── ProblemCommand
│   ├── TextCommand
│   │   ├── ImportantTextCommand
│   │   ├── HighlightedTextCommand
│   │   ├── EnumCommand
│   │   │   └── CustomEnumCommand
│   │   └── BulletCommand
│   └── EquationCommand
│       ├── InlineEquationCommand
│       └── DisplayEquationCommand
└── ResponseCommand (ABC)
    ├── AnswerCommand
    └── SolutionCommand
```

## Abstract Base Classes

### 1. Command (Root)
```python
class Command(ABC):
    def __init__(self):
        self._parameters: Dict[str, Any] = {
            "vspace": {
                "type": "float",
                "description": "Vertical space after content",
                "default": 1
            }
        }
        self._validate_rules: Dict[str, Callable] = {}
    
    @abstractmethod
    def render_markdown(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        pass
    
    @abstractmethod
    def render_text(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        pass
    
    @abstractmethod
    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        pass

    def validate_parameters(self, params: Dict[str, Any]) -> bool:
        return all(rule(params) for rule in self._validate_rules.values())
```

### 2. ContentCommand
```python
class ContentCommand(Command):
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "indent": {
                "type": "float",
                "description": "Left indentation in em units",
                "default": 0.0
            }
        })
    
    def render_text(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        indent = " " * int(params.get("indent", self._parameters["indent"]["default"]) * 2)
        return f"{indent}{content}"
```

### 3. ResponseCommand
```python
class ResponseCommand(Command):
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "show_in_preview": {
                "type": "bool",
                "description": "Whether to show in preview mode",
                "default": False
            }
        })
```

## Implementation Examples

### 1. Text Commands
```python
class TextCommand(ContentCommand):
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "indent": {
                "type": "float",
                "description": "Left indentation in em units",
                "default": 0.0
            }
        })
    
    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        indent = params.get("indent", self._parameters["indent"]["default"])
        return f"\\hspace{{{indent}em}}{content}"

class EnumCommand(TextCommand):
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "format": {
                "type": "str",
                "description": "Enumeration format (a), 1., etc.)",
                "default": "a)"
            }
        })
        self._state = {
            "counter": 0
        }
    
    def render_text(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        self._state["counter"] += 1
        format_str = params.get("format", self._parameters["format"]["default"])
        prefix = format_str.replace("a", chr(96 + self._state["counter"]))  # a, b, c...
        prefix = prefix.replace("1", str(self._state["counter"]))  # 1, 2, 3...
        indent = " " * int(params.get("indent", self._parameters["indent"]["default"]) * 2)
        return f"{indent}{prefix} {content}"

class BulletCommand(TextCommand):
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "bullet_char": {
                "type": "str",
                "description": "Bullet character",
                "default": "•"
            }
        })
    
    def render_text(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        bullet = params.get("bullet_char", self._parameters["bullet_char"]["default"])
        indent = " " * int(params.get("indent", self._parameters["indent"]["default"]) * 2)
        return f"{indent}{bullet} {content}"

    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        indent = params.get("indent", self._parameters["indent"]["default"])
        return f"\\hspace{{{indent}em}}\\textbullet\\ {content}"
```

### 2. Equation Commands
```python
class EquationCommand(ContentCommand):
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "numbered": {
                "type": "bool",
                "description": "Whether to number the equation",
                "default": False
            }
        })

class DisplayEquationCommand(EquationCommand):
    def render_latex(self, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        params = params or {}
        env = "equation" if params.get("numbered", False) else "equation*"
        return f"\\begin{{{env}}}\n{content}\n\\end{{{env}}}"
```

## Parameter Inheritance

1. **Base Parameters**
   - Every command inherits `vspace` from `Command`
   - Content commands inherit `indent` from `ContentCommand`
   - Parameters are merged down the inheritance chain

2. **Parameter Override**
   ```python
   class CustomEnumCommand(EnumCommand):
       def __init__(self):
           super().__init__()
           # Override default value
           self._parameters["format"]["default"] = "1."
           # Add new parameter
           self._parameters.update({
               "prefix": {
                   "type": "str",
                   "description": "Custom prefix before number",
                   "default": ""
               }
           })
   ```

## State Management

1. **Local State**
   ```python
   class EnumCommand(TextCommand):
       def __init__(self):
           super().__init__()
           self._state = {
               "counter": 0
           }
   ```

2. **State Reset**
   ```python
   def reset_state(self):
       """Reset enumeration counter"""
       self._state["counter"] = 0
   ```

## Integration Guidelines

1. **Creating New Commands**
   - Inherit from appropriate base class
   - Override necessary render methods
   - Add command-specific parameters
   - Implement validation rules

2. **Parameter Management**
   - Use descriptive parameter names
   - Provide sensible defaults
   - Document parameter purpose
   - Include validation rules

3. **State Handling**
   - Initialize state in constructor
   - Update state in render methods
   - Reset state when needed
   - Document state dependencies

4. **Testing Requirements**
   - Test parameter inheritance
   - Verify render method overrides
   - Check state management
   - Validate parameter rules

## Best Practices

1. **Design Principles**
   - Follow single responsibility principle
   - Keep inheritance chains shallow
   - Use composition when appropriate
   - Document inheritance relationships

2. **Code Organization**
   - Group related commands
   - Use consistent naming
   - Maintain clear interfaces
   - Document command behavior

3. **Error Handling**
   - Validate parameters
   - Handle edge cases
   - Provide clear error messages
   - Maintain parent class contracts

4. **Documentation**
   - Document parameter inheritance
   - Explain render method behavior
   - Describe state management
   - Include usage examples 