"""
Custom markdown parser for the Math Problem Editor with dynamic templates and enum tracking.
"""

import re
from config_loader import ConfigLoader
import sys
sys.path.append('./core')
from core.commands import ContentCommand, TextCommand, ProblemCommand, EnumCommand

class MarkdownParser:
    """Converts custom parameterized markdown to LaTeX with enum tracking"""
    
    def __init__(self, config_file=None, config_manager=None):
        """
        Initialize the markdown parser
        
        Args:
            config_file (str, optional): Path to the configuration file
            config_manager: Configuration manager instance for accessing app settings
        """
        print(f"Markdown Parser: Initializing with config_file={config_file}")
        # Initialize the configuration loader
        try:
            self.config = ConfigLoader(config_file)
            print(f"Markdown Parser: Config file path used: {getattr(self.config, 'config_file', 'BUILT-IN DEFAULT')}")
            text_cmd_config = self.config.get_command_config("text")
            if text_cmd_config:
                print(f"Markdown Parser: Loaded #text template: {text_cmd_config.get('latex_template', 'NOT FOUND')}")
                if 'parameters' in text_cmd_config:
                    print(f"Markdown Parser: #text parameters: {text_cmd_config['parameters']}")
            else:
                print("Markdown Parser: #text command configuration not found!")
        except Exception as e:
            print(f"Warning: Failed to load config file: {str(e)}")
            print("Using default configuration")
            self.config = ConfigLoader()
        
        # Store config manager for accessing app settings
        self.config_manager = config_manager
        
        # Document content collected before parsing
        self.document_content = ""
        
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
        
        # Initialize counter for enumeration tracking
        self.enum_counter = 0
        # Flag to track if we're in an enumeration block
        self.in_enum_block = False
        # Track if there is content between enums
        self.has_content_between_enums = False
    
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
            
        # Split text into math and non-math parts
        parts = []
        current_part = ""
        in_math = False
        
        i = 0
        while i < len(text):
            if text[i:i+2] == '\\[' or text[i:i+2] == '\\]':
                if current_part:
                    parts.append((current_part, in_math))
                    current_part = ""
                current_part += text[i:i+2]
                i += 2
                in_math = not in_math
            elif text[i] == '$':
                if current_part:
                    parts.append((current_part, in_math))
                    current_part = ""
                current_part += text[i]
                i += 1
                in_math = not in_math
            else:
                current_part += text[i]
                i += 1
        
        if current_part:
            parts.append((current_part, in_math))
        
        # Process each part
        result = ""
        for part, is_math in parts:
            if is_math:
                result += part  # Don't escape math parts
            else:
                # Create a copy of special chars without % for text content
                special_chars = {k: v for k, v in self.latex_special_chars.items() if k != '%'}
                # Escape special characters in non-math parts
                escaped_part = part
                for char, replacement in special_chars.items():
                    escaped_part = escaped_part.replace(char, replacement)
                result += escaped_part
        
        return result
    
    def parse_parameters(self, param_text):
        """
        Parse parameter string into a dictionary of parameters
        
        Args:
            param_text (str): Parameter string in format "param1:value1, param2:value2"
            
        Returns:
            dict: Dictionary of parameter name-value pairs
        """
        params = {}
        
        if not param_text:
            return params
        
        # Remove outer braces if present
        param_text = param_text.strip()
        if param_text.startswith('{') and param_text.endswith('}'):
            param_text = param_text[1:-1]
        
        # Split by commas, but respect quoted strings
        param_parts = []
        in_quotes = False
        in_array = False
        current_part = ""
        
        for char in param_text:
            if char == '"' or char == "'":
                in_quotes = not in_quotes
                current_part += char
            elif char == '[' and not in_quotes:
                in_array = True
                current_part += char
            elif char == ']' and not in_quotes:
                in_array = False
                current_part += char
            elif char == ',' and not in_quotes and not in_array:
                param_parts.append(current_part.strip())
                current_part = ""
            else:
                current_part += char
        
        if current_part:
            param_parts.append(current_part.strip())
        
        # Parse each parameter
        for part in param_parts:
            if ':' in part:
                key, value = part.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Handle array values [item1, item2, ...]
                if value.startswith('[') and value.endswith(']'):
                    array_items = self.parse_array(value[1:-1])
                    params[key] = array_items
                    continue
                
                # Remove quotes if present
                if (value.startswith('"') and value.endswith('"')) or \
                   (value.startswith("'") and value.endswith("'")):
                    value = value[1:-1]
                
                # Convert to appropriate type
                if value.lower() == 'true':
                    value = True
                elif value.lower() == 'false':
                    value = False
                elif value.isdigit():
                    value = int(value)
                elif value.replace('.', '', 1).isdigit() and value.count('.') <= 1:
                    value = float(value)
                
                params[key] = value
        
        return params
    
    def parse_array(self, array_text):
        """
        Parse array parameter
        
        Args:
            array_text (str): Text inside square brackets
            
        Returns:
            list: List of values
        """
        items = []
        
        # Split by commas, respecting quotes
        in_quotes = False
        current_item = ""
        
        for char in array_text:
            if char == '"' or char == "'":
                in_quotes = not in_quotes
                current_item += char
            elif char == ',' and not in_quotes:
                items.append(current_item.strip())
                current_item = ""
            else:
                current_item += char
        
        if current_item:
            items.append(current_item.strip())
        
        # Process each item to remove quotes and convert types
        processed_items = []
        for item in items:
            item = item.strip()
            if (item.startswith('"') and item.endswith('"')) or \
               (item.startswith("'") and item.endswith("'")):
                item = item[1:-1]
            
            # Convert to appropriate type
            if item.lower() == 'true':
                item = True
            elif item.lower() == 'false':
                item = False
            elif item.isdigit():
                item = int(item)
            elif item.replace('.', '', 1).isdigit() and item.count('.') <= 1:
                item = float(item)
                
            processed_items.append(item)
        
        return processed_items
    
    def apply_template(self, template, params, content=None):
        """
        Apply parameters to a LaTeX template with conditional sections
        
        Args:
            template (str): LaTeX template with placeholders
            params (dict): Parameters to apply
            content (str, optional): Content to insert in #CONTENT# placeholder
            
        Returns:
            str: Processed LaTeX content
        """
        result = template
        
        # Simple If-Else conditionals
        # Format: #IF condition# content #ELSE# content #ENDIF#
        
        # Process equality conditionals
        pattern = r'#IF\s+([^=<>!]+)=([^#]+)#(.*?)(?:#ELSE#(.*?))?#ENDIF#'
        
        def replace_conditional(match):
            param_name = match.group(1).strip()
            param_value = match.group(2).strip()
            if_content = match.group(3)
            else_content = match.group(4) or ''
            
            # Convert param_value to appropriate type for comparison
            if param_value.lower() == 'true':
                param_value = True
            elif param_value.lower() == 'false':
                param_value = False
            elif param_value.isdigit():
                param_value = int(param_value)
            elif param_value.replace('.', '', 1).isdigit() and param_value.count('.') <= 1:
                param_value = float(param_value)
            
            # Check if parameter matches the condition
            if param_name in params and params[param_name] == param_value:
                return if_content
            else:
                return else_content
        
        # Replace conditionals
        result = re.sub(pattern, replace_conditional, result, flags=re.DOTALL)
        
        # Process comparison conditionals
        comp_pattern = r'#IF\s+([^<>=!]+)([<>=!]+)([^#]+)#(.*?)(?:#ELSE#(.*?))?#ENDIF#'
        
        def replace_comparison(match):
            param_name = match.group(1).strip()
            operator = match.group(2).strip()
            param_value = match.group(3).strip()
            if_content = match.group(4)
            else_content = match.group(5) or ''
            
            # Convert param_value to appropriate type for comparison
            if param_value.lower() == 'true':
                param_value = True
            elif param_value.lower() == 'false':
                param_value = False
            elif param_value.isdigit():
                param_value = int(param_value)
            elif param_value.replace('.', '', 1).isdigit() and param_value.count('.') <= 1:
                param_value = float(param_value)
            
            # Check if parameter isn't present
            if param_name not in params:
                return else_content
            
            # Get parameter value
            actual_value = params[param_name]
            
            # Compare based on operator
            if operator == '>' and actual_value > param_value:
                return if_content
            elif operator == '>=' and actual_value >= param_value:
                return if_content
            elif operator == '<' and actual_value < param_value:
                return if_content
            elif operator == '<=' and actual_value <= param_value:
                return if_content
            elif operator == '==' and actual_value == param_value:
                return if_content
            elif operator == '!=' and actual_value != param_value:
                return if_content
            else:
                return else_content
        
        # Replace comparison conditionals
        result = re.sub(comp_pattern, replace_comparison, result, flags=re.DOTALL)
        
        # Replace parameter placeholders (case-insensitive)
        for param_name, param_value in params.items():
            # Convert param_value to string if it's not already
            if not isinstance(param_value, str):
                param_value = str(param_value)
                
            # Replace both #param# and #PARAM# patterns
            placeholder_lower = f'#{param_name.lower()}#'
            placeholder_upper = f'#{param_name.upper()}#'
            result = result.replace(placeholder_lower, param_value)
            result = result.replace(placeholder_upper, param_value)
        
        # Replace content placeholder
        if content is not None:
            result = result.replace('#CONTENT#', content)
        
        return result
    
    def handle_config_command(self, command_params, content_lines):
        """
        Handle the #config command to set document-level configuration
        
        Args:
            command_params (dict): Parameters from the config command
            content_lines (list): Content lines after the command
            
        Returns:
            str: Empty string (config command doesn't produce output)
        """
        # Process configuration content
        config_content = "\n".join(content_lines)
        
        try:
            # Try to parse as JSON if there's content
            if config_content.strip():
                # Replace escaped backslashes in the JSON string
                config_content = config_content.replace("\\\\", "\\")
                import json
                doc_config = json.loads(config_content)
                self.config.set_document_config(doc_config)
            elif command_params:
                # If parameters are provided, convert them to a document config
                doc_config = {"commands": {}}
                
                for param_name, param_value in command_params.items():
                    if "." in param_name:
                        # Parameter format: command.parameter.option
                        parts = param_name.split(".")
                        
                        if len(parts) >= 2:
                            cmd_name = parts[0]
                            
                            # Ensure command exists
                            if cmd_name not in doc_config["commands"]:
                                doc_config["commands"][cmd_name] = {
                                    "parameters": {}
                                }
                                
                            if len(parts) == 2:
                                # It's a command property like command.template
                                prop_name = parts[1]
                                if prop_name == "template":
                                    doc_config["commands"][cmd_name]["latex_template"] = param_value
                                else:
                                    doc_config["commands"][cmd_name][prop_name] = param_value
                            elif len(parts) >= 3:
                                # It's a parameter property like command.param.default
                                param_name = parts[1]
                                
                                # Ensure parameter exists
                                if "parameters" not in doc_config["commands"][cmd_name]:
                                    doc_config["commands"][cmd_name]["parameters"] = {}
                                    
                                if param_name not in doc_config["commands"][cmd_name]["parameters"]:
                                    doc_config["commands"][cmd_name]["parameters"][param_name] = {}
                                
                                # Set parameter property
                                prop_name = parts[2]
                                doc_config["commands"][cmd_name]["parameters"][param_name][prop_name] = param_value
                
                self.config.set_document_config(doc_config)
                
        except Exception as e:
            print(f"Error processing config command: {str(e)}")
            
        # No output from config command
        return ""
    
    def handle_enum_command(self, command_params, content_lines):
        """
        Handle the #enum command to create incremental enumerated lists
        
        Args:
            command_params (dict): Parameters from the enum command
            content_lines (list): Content lines after the command
            
        Returns:
            str: LaTeX enumerated list with proper continuation
        """
        # Get content
        content = "\n".join(content_lines)
        
        # If there was content between enums, or this is the first enum, 
        # we need to start a new enumeration environment
        if not self.in_enum_block or self.has_content_between_enums:
            # This is the first enum in a sequence or there was text between enums
            self.enum_counter = 1  # Reset counter
            self.in_enum_block = True
            self.has_content_between_enums = False
            
            # Start a new enumeration environment
            result = "\\begin{enumerate}\n\\item " + content + "\n\\end{enumerate}"
        else:
            # Continuing an existing enumeration
            self.enum_counter += 1
            
            # Just return the item without the environment - we'll rebuild the environments later
            result = "\\item " + content
        
        return result
    
    def parse_command(self, markdown_text, context="export"):
        """
        Parse a single command line and its content
        
        Args:
            markdown_text (str): Markdown command with optional parameters and content
            context (str): Rendering context (e.g., 'export', 'preview')
        
        Returns:
            str: Processed LaTeX content
        """
        print(f"parse_command: markdown_text={markdown_text}")
        lines = markdown_text.strip().split('\n')
        
        # Parse the command line
        if not lines or not lines[0].startswith('#'):
            return markdown_text
        
        command_line = lines[0]
        content_lines = lines[1:] if len(lines) > 1 else []
        
        # Extract command name and parameters
        command_pattern = r'^#(\w+)(?:\{([^}]*)\})?$'
        match = re.match(command_pattern, command_line)
        
        if not match:
            return markdown_text
        
        command_name = match.group(1)
        param_text = match.group(2) or ""
        
        # Parse parameters
        params = self.parse_parameters(param_text)
        
        # Special handling for config command
        if command_name == "config":
            return self.handle_config_command(params, content_lines)
        
        # Special handling for enum commands
        if command_name == "enum":
            # Get content
            content = "\n".join(content_lines)
            
            if not self.in_enum_block:
                # Start a new enumeration if we're not already in one
                self.in_enum_block = True
                return "\\begin{enumerate}\n\\item " + content
            else:
                # Continue the existing enumeration
                return "\\item " + content
        
        # For non-enum commands, check if we need to close an enum block
        if self.in_enum_block:
            self.in_enum_block = False
            return "\\end{enumerate}\n\n" + self.parse_standard_command(command_name, params, content_lines, context=context)
        
        # Standard command handling
        return self.parse_standard_command(command_name, params, content_lines, context=context)

    def parse_standard_command(self, command_name, params, content_lines, context="export"):
        """
        Parse a standard (non-enum) command
        
        Args:
            command_name (str): Name of the command
            params (dict): Command parameters
            content_lines (list): Content lines
            context (str): Rendering context (e.g., 'export', 'preview')
        
        Returns:
            str: Processed LaTeX content
        """
        print(f"parse_standard_command: command_name={command_name}, params={params}")
        # PATCH: Ignore all command/parameter definitions in config. Use only code-defined commands/parameters.
        code_commands = {
            'text': TextCommand(),
            'problem': ProblemCommand(),
            'enum': EnumCommand(),
        }
        if command_name in code_commands:
            code_cmd = code_commands[command_name]
            for param_name, param_config in code_cmd.parameters.items():
                if param_name not in params and 'default' in param_config:
                    params[param_name] = param_config['default']
            content = "\n".join(content_lines)
            # Allow variable substitution from config variables
            template = code_cmd.render_latex(content, params, context=context)
            # Substitute $variables.varname$ in the output
            for var, value in self.config.get_all_variables().items():
                template = template.replace(f'$variables.{var}$', value)
            return template
        return "#" + command_name
    
    def post_process_enums(self, latex_content):
        """
        Fix the enum environments in the LaTeX content
        
        Args:
            latex_content (str): The LaTeX content to process
            
        Returns:
            str: Fixed LaTeX content
        """
        import re
        
        # Pattern to find consecutive enum environments
        pattern = r'\\end{enumerate}\s*\\begin{enumerate}'
        
        # Replace with just an item separator
        fixed_content = re.sub(pattern, '\\\\item', latex_content)
        
        return fixed_content    
    
    def preprocess_document(self, markdown_text):
        """
        Preprocess the document text before parsing
        
        Args:
            markdown_text (str): Raw markdown text
            
        Returns:
            str: Preprocessed text
        """
        if not markdown_text:
            return ""
            
        # Store original content
        self.document_content = markdown_text
        
        # Automatically escape unescaped % signs
        processed_text = ""
        i = 0
        while i < len(markdown_text):
            if markdown_text[i] == '%' and (i == 0 or markdown_text[i-1] != '\\'):
                processed_text += '\\%'
            else:
                processed_text += markdown_text[i]
            i += 1
            
        # Split into lines and remove trailing whitespace
        lines = processed_text.splitlines()
        
        # Remove trailing whitespace from each line
        lines = [line.rstrip() for line in lines]
        
        # Join lines back together
        return "\n".join(lines)
    
    def parse(self, markdown_text, context="export"):
        """
        Convert markdown to LaTeX
        
        Args:
            markdown_text (str): Markdown content to convert
            context (str): Rendering context (e.g., 'export', 'preview')
        
        Returns:
            str: Converted LaTeX document
        """
        # Reset enum state
        self.in_enum_block = False
        
        # Store original document content
        self.document_content = markdown_text
        
        # Preprocess to extract and process configuration blocks
        markdown_text = self.preprocess_document(markdown_text)
        
        # Process the content line by line
        lines = markdown_text.strip().split('\n')
        processed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Check if this is a command line
            if line.startswith('#'):
                # Find the end of the command content
                command_name = re.match(r'^#(\w+)', line)
                if command_name is None:
                    # Not a valid command, treat as regular text
                    processed_lines.append(self.escape_latex(lines[i]))
                    i += 1
                    continue
                    
                command_name = command_name.group(1)
                command_content = [line]
                i += 1
                
                # Collect content until next command or end of input
                command_ended = False
                while i < len(lines) and not command_ended:
                    current_line = lines[i].strip()
                    # Check if this is a standalone #eq that terminates the equation
                    if current_line == f"#{command_name}" and command_name == "eq":
                        # This is a terminator for the current command
                        command_ended = True
                    # Check if this is a new command
                    elif current_line.startswith('#'):
                        # New command found, don't include it
                        break
                    else:
                        # Add this line to the current command's content
                        command_content.append(lines[i])
                    i += 1
                
                # Parse the command and its content
                command_text = '\n'.join(command_content)
                processed_command = self.parse_command(command_text, context=context)
                processed_lines.append(processed_command)
            else:
                # Regular text - escape LaTeX special characters
                escaped_line = self.escape_latex(line)
                
                # If we are in an enum block, we need to close it before adding regular text
                if self.in_enum_block and escaped_line.strip():
                    processed_lines.append("\\end{enumerate}")
                    self.in_enum_block = False
                
                processed_lines.append(escaped_line)
                i += 1
        
        # Join the processed lines
        content = '\n'.join(processed_lines)
        
        # Close any open enum block
        if self.in_enum_block:
            content += "\n\\end{enumerate}"
            self.in_enum_block = False
        
        # Return only the content, not a full LaTeX document
        return content
    
    def wrap_enum_items(self, content):
        """
        Fix issues with enumeration environments in LaTeX content
        
        Args:
            content (str): LaTeX content to process
            
        Returns:
            str: Processed content with fixed enumerate environments
        """
        import re
        
        # First, remove nested enumeration environments
        content = re.sub(r'\\begin{enumerate}\s*\\begin{enumerate}', r'\\begin{enumerate}', content)
        content = re.sub(r'\\end{enumerate}\s*\\end{enumerate}', r'\\end{enumerate}', content)
        
        # Fix any empty enumeration environments
        content = re.sub(r'\\begin{enumerate}\s*\\end{enumerate}', r'', content)
        
        return content
    
    def process_enum_sequences(self, content):
        """
        Process LaTeX content to fix separate enum environments
        
        Args:
            content (str): LaTeX content to process
            
        Returns:
            str: Fixed LaTeX content with consolidated enum environments
        """
        import re
        
        # Fix isolated \item commands that appear outside enumerate environments
        pattern = r'(\\end{enumerate})\s*(\\item\s+[^\n]+)'
        
        # Keep applying the fix until no more matches are found
        while re.search(pattern, content):
            content = re.sub(pattern, r'\2', content)
        
        # Now ensure all \item commands are within enumerate environments
        lines = content.split('\n')
        result = []
        in_enum = False
        
        for line in lines:
            stripped = line.strip()
            
            if stripped.startswith('\\item '):
                if not in_enum:
                    # Start a new enumeration
                    result.append('\\begin{enumerate}')
                    in_enum = True
                result.append(line)
            elif in_enum and '\\end{enumerate}' in stripped:
                # End the current enumeration
                in_enum = False
                result.append(stripped)
            elif in_enum and '\\begin{document}' in stripped:
                # We've reached the end of the document without closing the enumeration
                result.append('\\end{enumerate}')
                in_enum = False
                result.append(stripped)
            else:
                result.append(line)
        
        # Ensure any open enumeration is closed before the end of the document
        if in_enum:
            # Find the index of \end{document}
            content = '\n'.join(result)
            doc_end_index = content.rfind('\\end{document}')
            
            if doc_end_index >= 0:
                # Insert \end{enumerate} before \end{document}
                content = content[:doc_end_index] + '\\end{enumerate}\n' + content[doc_end_index:]
            else:
                # Append \end{enumerate} if \end{document} not found
                content += '\n\\end{enumerate}'
        else:
            content = '\n'.join(result)
        
        return content

    def process_enumeration_items(self, content):
        """
        Process and consolidate enumeration items into proper LaTeX lists
        
        Args:
            content (str): Processed content with individual enum items
            
        Returns:
            str: Content with proper LaTeX enumeration environments
        """
        # Find isolated \item entries and consolidate them into environments
        lines = content.split('\n')
        result_lines = []
        
        # Tracking enum state
        in_enum = False
        current_enum = []
        
        for line in lines:
            if line.strip().startswith('\\item '):
                if not in_enum:
                    # Start a new enumeration
                    in_enum = True
                    current_enum = ["\\begin{enumerate}"]
                
                # Add the item
                current_enum.append(line)
            else:
                if in_enum:
                    # Close the current enumeration
                    current_enum.append("\\end{enumerate}")
                    result_lines.extend(current_enum)
                    in_enum = False
                    current_enum = []
                
                # Add the non-enum line
                result_lines.append(line)
        
        # Don't forget to close the last enum if there is one
        if in_enum:
            current_enum.append("\\end{enumerate}")
            result_lines.extend(current_enum)
        
        return '\n'.join(result_lines)
    
    def create_latex_document(self, content):
        """
        Create a full LaTeX document with the processed content
        
        Args:
            content (str): Processed LaTeX content
            
        Returns:
            str: Complete LaTeX document
        """
        # Get font size from configuration if available
        font_size = 14  # Default font size
        if self.config_manager:
            font_size = self.config_manager.get_value("preview", "font_size", 14)
        
        # Get font family from configuration
        font_family = "Computer Modern"  # Default LaTeX font
        if self.config_manager:
            font_family = self.config_manager.get_value("preview", "font_family", "Computer Modern")
        
        # Map font size to standard LaTeX font size commands
        font_size_cmd = ""
        if font_size <= 8:
            font_size_cmd = "\\small"
        elif font_size <= 10:
            font_size_cmd = "\\normalsize"
        elif font_size <= 12:
            font_size_cmd = "\\large"
        elif font_size <= 14:
            font_size_cmd = "\\Large"
        elif font_size <= 17:
            font_size_cmd = "\\LARGE"
        elif font_size <= 20:
            font_size_cmd = "\\huge"
        else:
            font_size_cmd = "\\Huge"
        
        # Font package and command based on selected font
        font_packages = ""
        font_command = ""
        
        if font_family == "Times New Roman":
            font_packages = "\\usepackage{times}"
            font_command = "\\rmfamily"
        elif font_family == "Helvetica":
            font_packages = "\\usepackage{helvet}\n\\renewcommand{\\familydefault}{\\sfdefault}"
            font_command = ""
        elif font_family == "Courier":
            font_packages = "\\usepackage{courier}"
            font_command = "\\ttfamily"
        elif font_family == "Palatino":
            font_packages = "\\usepackage{palatino}"
            font_command = ""
        elif font_family == "Bookman":
            font_packages = "\\usepackage{bookman}"
            font_command = ""
        elif font_family == "Carlito":
            font_packages = "\\usepackage{carlito}"
            font_command = ""
        # Add fontspec for custom fonts (e.g., Calibri)
        if font_family not in ["Computer Modern", "Times New Roman", "Helvetica", "Courier", "Palatino", "Bookman", "Carlito"]:
            font_packages = "\\usepackage{fontspec}\n" + font_packages
        
        # Create a LaTeX document with necessary packages for math and images
        template = r"""\documentclass{article}
    \usepackage{amsmath}
    \usepackage{amssymb}
    \usepackage{graphicx}
    \graphicspath{{./}{./images/}}
    \usepackage{geometry}
    \usepackage{xcolor}
    \usepackage{mdframed}
    \usepackage{enumitem}
    """ + font_packages + r"""

    % Set margins
    \geometry{margin=1in}

    % Set paragraph indentation to zero
    \setlength{\parindent}{0pt}
    
    \newcommand{\mydefaultsize}{\fontsize{14pt}{16pt}\selectfont}
    \begin{document}

    """ + font_size_cmd + font_command + r"""

    """ + content + r"""

    \end{document}
    """
        
        return template