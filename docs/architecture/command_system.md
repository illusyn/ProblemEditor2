# Command System Architecture

## Overview

The command system is built on a hierarchical class structure that enables:
- Consistent command behavior
- Code reuse through inheritance
- Flexible parameter management
- Multiple output format support

## Core Components

### 1. Base Command Class

```python
class Command(ABC):
    """Abstract base class for all commands"""
    
    def __init__(self):
        self._parameters: Dict[str, Any] = {
            "vspace": {
                "type": "float",
                "description": "Vertical space after content",
                "default": 1
            }
        }
    
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
```

### 2. Command Categories

1. **Content Commands**
   - ProblemCommand
   - TextCommand
   - EquationCommand

2. **Structural Commands**
   - EnumCommand
   - BulletCommand

3. **Response Commands**
   - AnswerCommand

## Inheritance Patterns

### 1. Direct Inheritance

Commands that inherit directly from the base Command class:

```python
class TextCommand(Command):
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "indent": {
                "type": "float",
                "description": "Left indentation",
                "default": 0.0
            }
        })
```

### 2. Specialized Inheritance

Commands that inherit from other concrete commands:

```python
class ImportantTextCommand(TextCommand):
    def __init__(self):
        super().__init__()
        self._parameters.update({
            "highlight": {
                "type": "boolean",
                "description": "Whether to highlight the text",
                "default": True
            }
        })
```

## Parameter System

1. **Parameter Definition**
   - Type information
   - Description
   - Default value
   - Validation rules

2. **Parameter Inheritance**
   - Parameters are inherited from parent classes
   - Child classes can override or extend parameters
   - Default values can be customized

## Rendering System

1. **Multiple Output Formats**
   - Markdown (for editing)
   - Plain text (for display)
   - LaTeX (for PDF generation)

2. **Format-Specific Behavior**
   - Each format has its own rendering method
   - Consistent spacing and formatting
   - Special character handling

## Integration with Parser

```python
class MarkdownParser:
    def __init__(self):
        self.commands = {
            "problem": ProblemCommand(),
            "text": TextCommand(),
            "enum": EnumCommand(),
            "bullet": BulletCommand(),
            "eq": EquationCommand(),
            "answer": AnswerCommand()
        }
```

## Best Practices

1. **Command Implementation**
   - Keep commands focused and single-purpose
   - Validate input in render methods
   - Handle parameters consistently
   - Document command behavior

2. **Parameter Management**
   - Use descriptive parameter names
   - Provide sensible defaults
   - Document parameter purpose
   - Include validation rules

3. **Inheritance Usage**
   - Inherit when sharing significant functionality
   - Override methods when necessary
   - Maintain consistent interface
   - Document inheritance relationships

## Future Extensions

1. **New Command Types**
   - Define clear inheritance path
   - Follow existing patterns
   - Include comprehensive tests
   - Update documentation

2. **Parameter Enhancements**
   - Type validation
   - Dynamic defaults
   - Dependent parameters
   - Parameter groups

3. **Rendering Improvements**
   - Additional output formats
   - Custom templates
   - Style configuration
   - Format-specific options 