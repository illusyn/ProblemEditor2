"""Parser for the simplified math editor markdown format."""

from typing import List, Tuple, Optional, Dict, Any
from .commands import (
    Command,
    ProblemCommand,
    TextCommand,
    EnumCommand
)

class MarkdownParser:
    """Parses markdown text into commands and handles enumeration."""
    
    def __init__(self):
        # Initialize command instances
        self.commands = {
            "problem": ProblemCommand(),
            "text": TextCommand(),
            "enum": EnumCommand()
        }
        # Track enumeration state
        self.enum_count = 0
        self.in_enum_block = False
    
    def split_into_blocks(self, markdown: str) -> List[Tuple[str, str]]:
        """
        Split markdown into (command, content) blocks.
        
        Args:
            markdown: The markdown text to parse
            
        Returns:
            List of (command_name, content) tuples
        """
        blocks = []
        current_command = None
        current_content = []
        
        for line in markdown.split('\n'):
            if line.startswith('#'):
                # Save previous block if it exists
                if current_command is not None:
                    content = '\n'.join(current_content).strip()
                    if content:
                        blocks.append((current_command, content))
                # Start new block
                current_command = line[1:].strip()  # Remove # and whitespace
                current_content = []
            else:
                if current_command is not None:
                    current_content.append(line)
        
        # Add final block
        if current_command is not None:
            content = '\n'.join(current_content).strip()
            if content:
                blocks.append((current_command, content))
        
        return blocks
    
    def parse_block(self, command: str, content: str, params: Optional[Dict[str, Any]] = None) -> str:
        """
        Parse a single markdown block into LaTeX.
        
        Args:
            command: The command name (without #)
            content: The content for the command
            params: Optional parameters for the command
            
        Returns:
            LaTeX output for the block
        """
        if command not in self.commands:
            raise ValueError(f"Unknown command: #{command}")
        
        cmd = self.commands[command]
        
        # Handle enumeration
        if command == "enum":
            latex = ""  # Initialize latex variable
            if not self.in_enum_block:
                self.in_enum_block = True
                self.enum_count = 0
                latex = "\\begin{enumerate}[label={\\alph*)}]\n"
            self.enum_count += 1
            latex += cmd.render_latex(content, params)
            return latex
        else:
            # Close enum block if we were in one
            if self.in_enum_block:
                self.in_enum_block = False
                prefix = "\\end{enumerate}\n\n"
            else:
                prefix = ""
            
            return prefix + cmd.render_latex(content, params)
    
    def parse(self, markdown: str) -> str:
        """
        Parse markdown text into LaTeX.
        
        Args:
            markdown: The markdown text to parse
            
        Returns:
            LaTeX output
        """
        blocks = self.split_into_blocks(markdown)
        latex_parts = []
        
        for command, content in blocks:
            latex_parts.append(self.parse_block(command, content))
        
        # Close any open enum block
        if self.in_enum_block:
            latex_parts.append("\\end{enumerate}\n")
            self.in_enum_block = False
        
        return "\n".join(latex_parts) 