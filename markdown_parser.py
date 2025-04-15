"""
Custom markdown parser for the Simplified Math Editor.

This module provides functionality to convert custom markdown to LaTeX,
supporting special commands for math problem structure.
"""

import re

class MarkdownParser:
    """Converts custom markdown to LaTeX with special handling for math problems"""
    
    def __init__(self):
        """Initialize the markdown parser"""
        # Define custom commands mapping
        self.custom_commands = {
            "#problem": "\\section*{#TEXT#}",
            "#solution": "\\section*{Solution}",
            "#question": "#TEXT#",
            "#eq": "$#TEXT#$",  # Changed to inline math mode for simpler equations
            "#align": "\\begin{align}\n#TEXT#\n\\end{align}",
            "#bullet": "\\item #TEXT#"
        }
        
        # LaTeX special characters that need to be escaped
        self.latex_special_chars = {
            '#': '\\#',
            '$': '\\$',
            '%': '\\%',
            '&': '\\&',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '^': '\\textasciicircum{}',
            '\\': '\\textbackslash{}'
        }
    
    def escape_latex(self, text):
        """
        Escape special LaTeX characters in text
        
        Args:
            text (str): Text to escape
            
        Returns:
            str: Escaped text safe for LaTeX
        """
        # Don't escape if the text is empty
        if not text:
            return text
            
        # Don't escape math expressions inside $ $ or \[ \]
        if text.startswith('$') and text.endswith('$'):
            return text
        if text.startswith('\\[') and text.endswith('\\]'):
            return text
            
        # Escape each special character
        result = text
        for char, replacement in self.latex_special_chars.items():
            result = result.replace(char, replacement)
            
        return result
    
    def parse(self, markdown_text):
        """
        Convert markdown to LaTeX
        
        Args:
            markdown_text (str): Markdown content to convert
            
        Returns:
            str: Converted LaTeX document
        """
        # Process the content line by line
        lines = markdown_text.strip().split('\n')
        processed_lines = []
        
        i = 0
        in_itemize = False  # Track if we're inside an itemize environment
        in_figure = False   # Track if we're inside a figure environment
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Special handling for figure environments
            if line.startswith('\\begin{figure'):
                # Start collecting the figure environment
                in_figure = True
                processed_lines.append(line)
                i += 1
                continue
            
            if in_figure:
                # If we're in a figure environment, add the line unchanged
                processed_lines.append(lines[i])  # Use original line with whitespace
                
                # Check if this line ends the figure environment
                if '\\end{figure}' in line:
                    in_figure = False
                
                i += 1
                continue
            
            # Handle math expressions with \[ \]
            if line.startswith('\\['):
                # Collect all lines until closing \]
                math_content = [line]
                i += 1
                while i < len(lines) and '\\]' not in lines[i]:
                    math_content.append(lines[i])
                    i += 1
                
                # Add the closing line if found
                if i < len(lines):
                    math_content.append(lines[i])
                    i += 1
                
                # Add the math block directly (no escaping needed)
                processed_lines.extend(math_content)
                continue
                
            # Detect existing math delimiters
            if line.startswith('$') and line.endswith('$'):
                processed_lines.append(line)
                i += 1
                continue
            
            # Problem section
            if line.startswith("#problem"):
                # Extract problem title if present
                problem_title = line[len("#problem"):].strip()
                if problem_title:
                    # Escape special characters in the title
                    problem_title = self.escape_latex(problem_title)
                    processed_lines.append("\\section*{" + problem_title + "}")
                else:
                    processed_lines.append("\\section*{}")
                i += 1
                
            # Solution section
            elif line == "#solution":
                processed_lines.append("\\section*{Solution}")
                i += 1
                
            # Bullet points
            elif line.startswith("#bullet"):
                # Extract the bullet content
                bullet_content = line[len("#bullet"):].strip()
                
                # Escape special characters in the bullet content
                bullet_content = self.escape_latex(bullet_content)
                
                # Start itemize environment if we're not already in one
                if not in_itemize:
                    processed_lines.append("\\begin{itemize}")
                    in_itemize = True
                
                # Add the bullet item
                processed_lines.append("\\item " + bullet_content)
                
                # Check if next line is also a bullet
                next_is_bullet = i+1 < len(lines) and lines[i+1].strip().startswith("#bullet")
                
                # End itemize environment if next line is not a bullet
                if not next_is_bullet and in_itemize:
                    processed_lines.append("\\end{itemize}")
                    in_itemize = False
                
                i += 1
                
            # Question with no prefix
            elif line == "#question":
                i += 1  # Move to the line with the question content
                if i < len(lines):
                    question_text = lines[i].strip()
                    # Escape special characters in the question text
                    question_text = self.escape_latex(question_text)
                    processed_lines.append(question_text)
                i += 1
                
            # Equation - FIXED HANDLING
            elif line.startswith("#eq"):
                # Extract equation content from either this line or the next
                eq_content = line[len("#eq"):].strip()
                
                # If no content on this line, get from next line
                if not eq_content and i + 1 < len(lines):
                    i += 1
                    eq_content = lines[i].strip()
                
                # Use display math mode for the equation
                processed_lines.append("\\begin{equation*}")  # Added * for unnumbered equation
                processed_lines.append(eq_content)
                processed_lines.append("\\end{equation*}")
                
                i += 1
                
            # Aligned equations environment
            elif line == "#align":
                i += 1  # Move to the first line of aligned equations
                align_content = []
                
                # Collect all lines until next command or end
                while i < len(lines) and not lines[i].strip().startswith('#'):
                    if lines[i].strip():  # Only add non-empty lines
                        align_content.append(lines[i].strip())
                    i += 1
                
                # Use aligned environment
                processed_lines.append("\\begin{align*}")  # Added * for unnumbered equations
                processed_lines.append(" \\\\ ".join(align_content))
                processed_lines.append("\\end{align*}")
                
            # Regular text
            else:
                # Escape special characters in regular text
                escaped_line = self.escape_latex(line)
                processed_lines.append(escaped_line)
                i += 1
        
        # If we're still in an itemize environment at the end, close it
        if in_itemize:
            processed_lines.append("\\end{itemize}")
        
        # Join the processed lines
        content = '\n'.join(processed_lines)
        
        # Create the full LaTeX document
        document = self.create_latex_document(content)
        
        return document
    
    def create_latex_document(self, content):
        """
        Create a full LaTeX document with the processed content
        
        Args:
            content (str): Processed LaTeX content
            
        Returns:
            str: Complete LaTeX document
        """
        # Create a LaTeX document with necessary packages for math and images
        # Using raw string to avoid any issues with string formatting
        template = r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\graphicspath{{./}{./images/}}
\usepackage{geometry}

% Set margins
\geometry{margin=1in}

% Define custom commands for problem formatting
\newcommand{\problem}[1]{\section*{#1}}

\begin{document}

""" + content + r"""

\end{document}
"""
        
        return template