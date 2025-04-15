"""
Custom markdown parser for the Simplified Math Editor.

This module provides functionality to convert custom markdown to LaTeX.
"""

import re

class MarkdownParser:
    """Parses custom markdown to LaTeX"""
    
    def __init__(self):
        """Initialize the markdown parser"""
        # Load default template
        self.template = self.load_template()
    
    def load_template(self):
        """Load the default LaTeX template"""
        # Basic template with necessary packages
        return r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{graphicx}
\graphicspath{{./}{./images/}}

% Custom commands for problem-solving
\newcommand{\problem}[1]{\section*{Problem}\medskip{#1}}
\newcommand{\solution}[1]{\section*{Solution}\medskip{#1}}
\newcommand{\question}[1]{\textbf{Question:} #1}

\begin{document}

#CONTENT#

\end{document}
"""
    
    def escape_latex(self, text):
        """
        Escape special LaTeX characters
        
        Args:
            text (str): Raw text to escape
            
        Returns:
            str: LaTeX-escaped text
        """
        # Characters to escape: # $ % & _ { } ~ ^ \
        escape_chars = {
            '#': r'\#',
            '$': r'\$',
            '%': r'\%',
            '&': r'\&',
            '_': r'\_',
            '{': r'\{',
            '}': r'\}',
            '~': r'\textasciitilde{}',
            '^': r'\textasciicircum{}',
            '\\': r'\textbackslash{}'
        }
        
        # Don't escape if it looks like it's already in a LaTeX command or environment
        if (text.strip().startswith('\\') or 
            text.strip().startswith('{') or 
            text.strip().startswith('[') or
            '\\begin{' in text):
            return text
            
        # Escape each special character
        for char, replacement in escape_chars.items():
            # Skip escaping \ and $ as they might be part of LaTeX commands
            if char not in ['\\', '$'] or (char == '$' and text.count('$') % 2 == 0):
                text = text.replace(char, replacement)
                
        return text

    def is_math_environment(self, line):
        """Check if the line is part of a math environment"""
        # Patterns that indicate math environments
        math_patterns = [
            r'\\\[', r'\\\]',  # Display math
            r'\$\$', r'\$',     # Inline math
            r'\\begin\{equation', r'\\end\{equation',  # Equation environment
            r'\\begin\{align', r'\\end\{align',        # Align environment
            r'\\begin\{figure', r'\\end\{figure'       # Figure environment
        ]
        
        # Check if any pattern is in the line
        for pattern in math_patterns:
            if re.search(pattern, line):
                return True
                
        return False
        
    def parse(self, markdown_text):
        """
        Parse custom markdown to LaTeX
        
        Args:
            markdown_text (str): Custom markdown text
            
        Returns:
            str: Compiled LaTeX document
        """
        # Split the markdown into lines
        lines = markdown_text.split('\n')
        
        # Process lines
        latex_lines = []
        in_equation = False
        in_aligned = False
        in_figure = False
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Skip empty lines at the beginning
            if not line.strip() and not latex_lines:
                i += 1
                continue
            
            # Check if we're in a LaTeX environment
            if line.strip().startswith('\\begin{figure}'):
                in_figure = True
                latex_lines.append(line)
                i += 1
                continue
                
            if line.strip().startswith('\\end{figure}'):
                in_figure = False
                latex_lines.append(line)
                i += 1
                continue
                
            if in_figure:
                # Pass through figure content unchanged
                latex_lines.append(line)
                i += 1
                continue
                
            # If line contains \[ or \], preserve it exactly
            if '\\[' in line or '\\]' in line:
                latex_lines.append(line)
                i += 1
                continue
                
            # Process custom markdown tags
            if line.startswith('#problem'):
                # Extract any text after #problem
                problem_text = line[8:].strip()
                if problem_text:
                    latex_lines.append(f"\\problem{{{self.escape_latex(problem_text)}}}")
                else:
                    latex_lines.append("\\problem{}")
                    
            elif line.startswith('#solution'):
                # Extract any text after #solution
                solution_text = line[9:].strip()
                if solution_text:
                    latex_lines.append(f"\\solution{{{self.escape_latex(solution_text)}}}")
                else:
                    latex_lines.append("\\solution{}")
                    
            elif line.startswith('#question'):
                # Extract any text after #question
                question_text = line[9:].strip()
                if question_text:
                    latex_lines.append(f"\\question{{{self.escape_latex(question_text)}}}")
                else:
                    latex_lines.append("\\question{}")
                    
            elif line.startswith('#eq'):
                # Extract any equation text after #eq
                eq_text = line[3:].strip()
                if eq_text:
                    # If there's text, put it in an equation environment
                    latex_lines.append("\\begin{equation*}")
                    latex_lines.append(f"    {eq_text}")
                    latex_lines.append("\\end{equation*}")
                else:
                    # If no text, just create an empty equation environment
                    # The user will add the equation on the next line
                    latex_lines.append("\\begin{equation*}")
                    
                    # Check if the next line has content that should go in the equation
                    if i+1 < len(lines) and lines[i+1].strip() and not lines[i+1].startswith('#'):
                        i += 1
                        latex_lines.append(f"    {lines[i].strip()}")
                    
                    latex_lines.append("\\end{equation*}")
                    
            elif line.startswith('#align'):
                in_aligned = True
                latex_lines.append("\\begin{align*}")
                
            elif line.startswith('#bullet'):
                # Extract the bullet text
                bullet_text = line[7:].strip()
                if bullet_text:
                    latex_lines.append(f"\\item {self.escape_latex(bullet_text)}")
                else:
                    latex_lines.append("\\item")
                    
            elif in_aligned:
                # Check if this line ends the aligned environment
                if not line.strip():
                    in_aligned = False
                    latex_lines.append("\\end{align*}")
                else:
                    # Add the line to the aligned environment
                    latex_lines.append(f"    {line.strip()} \\\\")
                    
            else:
                # Regular text, escape special characters if not in a math/figure environment
                if line.strip() and not self.is_math_environment(line):
                    latex_lines.append(self.escape_latex(line))
                else:
                    # Pass through math environments unchanged
                    latex_lines.append(line)
            
            i += 1
            
        # Ensure aligned environment is closed
        if in_aligned:
            latex_lines.append("\\end{align*}")
            
        # Join the latex lines and insert into the template
        latex_content = '\n'.join(latex_lines)
        
        # Insert the content into the template
        latex_document = self.template.replace('#CONTENT#', latex_content)
        
        return latex_document
