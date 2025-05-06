#!/usr/bin/env python3
"""
Enhanced Python Dependency Tracker

This script analyzes a Python file (default: main_qt.py) and generates a list of all
files it depends on, including recursive dependencies. It tracks Python files as well
as other file types like .tex and .json that are imported or loaded in the code.
The list is saved to a text file. Standard library imports are excluded.

Usage:
    python dependency_tracker.py [root_file] [-o output_file] [-e extensions] [-v] [-s] [-x exclude]

Options:
    root_file             Root Python file to analyze (default: main_qt.py)
    -o, --output          Output file name (default: project_dependencies.txt)
    -e, --extensions      Additional file extensions to track (comma-separated, default: .tex,.json)
    -v, --verbose         Enable verbose output for debugging
    -s, --scan-dir        Scan entire directory for tracked file types
    -x, --exclude         Comma-separated list of files or directories to exclude

Example:
    python dependency_tracker.py main_qt.py -o deps.txt -e .tex,.json -v -s -x exports/debug_latex.tex,tmp
"""

import argparse
import os
import re
import sys
from pathlib import Path


class DependencyTracker:
    """
    Tracks file dependencies in a Python project.
    
    This class scans Python files for imports and file operations to identify
    all dependencies, including Python modules and other file types like .tex
    and .json that are referenced in the code.
    """
    
    def __init__(self, root_file):
        """
        Initialize the dependency tracker.
        
        Args:
            root_file: Path to the root Python file to analyze
        """
        self.root_file = Path(root_file).resolve()
        self.root_dir = self.root_file.parent
        self.dependencies = set()
        self.processed_files = set()
        self.verbose = False
        
        # Files and directories to exclude (output files, temp files, etc.)
        self.excluded_paths = {
            'exports',                  # Entire exports directory
            'exports/',                 # With trailing slash
            'exports\\',                # Windows path variant
            '/exports',                 # With leading slash
            '\\exports',                # Windows path variant
            '__pycache__',              # Common directories to exclude
            '.git',
            'venv',
            'env',
            'build',
            'dist',
            'output',
            'temp_scripts',            # Project-specific temp directories
            'temp_images',
            'latex_test_output',
            'db_backups',
            '.cursor',
            'junkdir',
        }
        
        # Regular expressions for different import patterns
        self.import_patterns = [
            re.compile(r'^\s*import\s+([a-zA-Z0-9_., ]+)'),  # import module, package
            re.compile(r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import'),  # from module import ...
            re.compile(r'^\s*from\s+\.+([a-zA-Z0-9_.]*)\s+import'),  # from .module import ...
            re.compile(r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import\s+\*'),  # from module import *
        ]
        
        # Extensions to track (besides Python files)
        self.tracked_extensions = {'.tex', '.json'}  # Only essential file types for app operation
        
        # Standard library modules to ignore
        self.std_lib_modules = set(sys.builtin_module_names)
        # Add common standard library modules
        self.std_lib_modules.update([
            'os', 're', 'sys', 'math', 'datetime', 'time', 'random', 'json',
            'csv', 'argparse', 'logging', 'pathlib', 'collections', 'itertools',
            'functools', 'typing', 'shutil', 'tempfile', 'threading', 'multiprocessing',
            'subprocess', 'socket', 'http', 'urllib', 'unittest', 'pytest',
            'io', 'hashlib', 'uuid', 'getopt', 'configparser', 'pickle', 'base64',
            'importlib', 'inspect', 'ast', 'traceback', 'warnings', 'contextlib',
            'zipfile', 'gzip', 'tarfile', 'copy', 'enum', 'statistics', 'turtle',
            # PyQt modules
            'PyQt5', 'PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets',
            'PyQt5.QtPrintSupport', 'PyQt5.QtSvg', 'PyQt5.QtXml',
            # Additional common modules
            'numpy', 'pandas', 'matplotlib', 'PIL', 'PIL.Image', 'PIL.ImageQt',
            'sqlite3', 'sqlalchemy', 'pymongo', 'requests', 'urllib3',
            'yaml', 'toml', 'ini', 'configparser', 'xml', 'html', 'markdown'
        ])
        
        # Regular expressions for file operations
        self.file_patterns = [
            # Common open() patterns
            re.compile(r'open\(\s*[\'"]([^\'"]+)[\'"]'),
            # Common Path operations
            re.compile(r'Path\(\s*[\'"]([^\'"]+)[\'"]'),
            # JSON loads from file
            re.compile(r'json\.load\(\s*open\(\s*[\'"]([^\'"]+)[\'"]'),
            # JSON operations
            re.compile(r'json\.(load|loads)\s*\(\s*[^,\)]*[\'"]([^\'"]+\.json)[\'"]'),
            re.compile(r'with\s+open\(\s*[\'"]([^\'"]+\.json)[\'"]'),
            re.compile(r'[\'"]([^\'"\s]+\.json)[\'"]'),
            # TEX files
            re.compile(r'[\'"]([^\'"\s]+\.tex)[\'"]'),
            # with open pattern
            re.compile(r'with\s+open\(\s*[\'"]([^\'"]+)[\'"]'),
            # os.path operations
            re.compile(r'os\.path\.(join|abspath|dirname)\(.*[\'"]([^\'"]+)[\'"]'),
            # Variable assignment with file paths
            re.compile(r'(?:file|path|filepath|file_path|template|config)\s*=\s*[\'"]([^\'"]+)[\'"]'),
            # Read file patterns
            re.compile(r'read_file\(\s*[\'"]([^\'"]+)[\'"]'),
            re.compile(r'load_file\(\s*[\'"]([^\'"]+)[\'"]'),
            re.compile(r'parse_file\(\s*[\'"]([^\'"]+)[\'"]'),
            re.compile(r'load\(\s*[\'"]([^\'"]+)[\'"]'),
            # Import from file like syntax
            re.compile(r'import\s+[^\'"\n]*\s+from\s+[\'"]([^\'"]+)[\'"]'),
            # Require syntax (for JavaScript-like imports)
            re.compile(r'require\(\s*[\'"]([^\'"]+)[\'"]'),
            # PyQt specific patterns
            re.compile(r'QIcon\(\s*[\'"]([^\'"]+)[\'"]'),
            re.compile(r'QImage\(\s*[\'"]([^\'"]+)[\'"]'),
            re.compile(r'QPixmap\(\s*[\'"]([^\'"]+)[\'"]'),
            re.compile(r'load\(\s*[\'"]([^\'"]+)[\'"]'),
        ]
    
    def set_verbose(self, verbose):
        """
        Set verbose mode.
        
        Args:
            verbose: Boolean flag to enable verbose output
        """
        self.verbose = verbose
    
    def log(self, message):
        """
        Log a message if verbose mode is enabled.
        
        Args:
            message: Message to log
        """
        if self.verbose:
            print(message)
    
    def find_file(self, module_name, from_file=None):
        """
        Find the file path for a module name.
        
        Args:
            module_name: Name of the module to find
            from_file: Path of the file importing this module
            
        Returns:
            Path object for the found file or None if not found
        """
        if from_file is None:
            from_file = self.root_file
        
        from_dir = from_file.parent
        
        # Handle relative imports
        if module_name.startswith('.'):
            # Count the number of dots for relative imports
            dot_count = 0
            while module_name[dot_count] == '.':
                dot_count += 1
            
            # Remove dots from module name
            module_name = module_name[dot_count:]
            
            # Go up the directory tree for each dot
            current_dir = from_dir
            for _ in range(dot_count - 1):
                current_dir = current_dir.parent
                
            # Build the path
            if module_name:
                module_path = current_dir / (module_name.replace('.', '/') + '.py')
            else:
                # Handle case like "from . import module"
                module_path = current_dir / '__init__.py'
                
            return module_path if module_path.exists() else None
        
        # Try standard module path
        module_path = from_dir / (module_name.replace('.', '/') + '.py')
        if module_path.exists():
            return module_path
        
        # Try as a package with __init__.py
        init_path = from_dir / module_name.replace('.', '/') / '__init__.py'
        if init_path.exists():
            return init_path
        
        # Try in the root directory
        root_module_path = self.root_dir / (module_name.replace('.', '/') + '.py')
        if root_module_path.exists():
            return root_module_path
            
        root_init_path = self.root_dir / module_name.replace('.', '/') / '__init__.py'
        if root_init_path.exists():
            return root_init_path
            
        # Try in common subdirectories
        common_dirs = ['ui_qt', 'managers', 'core', 'converters', 'db', 'utils', 'preview']
        for common_dir in common_dirs:
            # Check relative to importing file
            dir_path = from_dir / common_dir / (module_name.replace('.', '/') + '.py')
            if dir_path.exists():
                return dir_path
                
            # Check relative to project root
            root_dir_path = self.root_dir / common_dir / (module_name.replace('.', '/') + '.py')
            if root_dir_path.exists():
                return root_dir_path
                
            # Try with __init__.py
            dir_init_path = from_dir / common_dir / module_name.replace('.', '/') / '__init__.py'
            if dir_init_path.exists():
                return dir_init_path
                
            root_dir_init_path = self.root_dir / common_dir / module_name.replace('.', '/') / '__init__.py'
            if root_dir_init_path.exists():
                return root_dir_init_path
            
        return None
    
    def resolve_file_path(self, file_name, from_file):
        """
        Resolve a referenced file path relative to the importing file.
        
        Args:
            file_name: Name or path of the file
            from_file: Path of the file referencing this file
            
        Returns:
            Path object for the resolved file or None if not found
        """
        from_dir = from_file.parent
        
        # Clean up the file_name (remove quotes and spaces)
        file_name = file_name.strip('\'"').strip()
        
        # Skip if it's obviously not a file path
        if len(file_name) < 2 or '{' in file_name or '$' in file_name or '%' in file_name:
            return None
            
        # If it's a full path, try it directly
        if os.path.isabs(file_name):
            abs_path = Path(file_name)
            if abs_path.exists() and abs_path.suffix in self.tracked_extensions:
                return abs_path
        
        # Try direct path relative to importing file
        file_path = from_dir / file_name
        if file_path.exists():
            return file_path
        
        # Try relative to project root
        root_path = self.root_dir / file_name
        if root_path.exists():
            return root_path
        
        # Try in common subdirectories
        common_dirs = ['data', 'templates', 'resources', 'assets', 'config', 'docs']
        for common_dir in common_dirs:
            # Check relative to importing file
            dir_path = from_dir / common_dir / file_name
            if dir_path.exists():
                return dir_path
                
            # Check relative to project root
            root_dir_path = self.root_dir / common_dir / file_name
            if root_dir_path.exists():
                return root_dir_path
            
        # Check if we only have a filename (no directory)
        if '/' not in file_name and '\\' not in file_name:
            # Search recursively by name in project directory
            for check_dir in [self.root_dir]:
                try:
                    # First try to find exact name match
                    matches = list(check_dir.glob(f"**/{file_name}"))
                    if matches:
                        return matches[0]
                    
                    # If it has an extension we're tracking, try by extension and name
                    file_obj = Path(file_name)
                    if file_obj.suffix in self.tracked_extensions:
                        # Try by name without path
                        matches = list(check_dir.glob(f"**/{file_obj.name}"))
                        if matches:
                            return matches[0]
                except Exception as e:
                    self.log(f"Error during glob search: {e}")
        
        # For paths that might be constructed with variables, try to match by extension and partial name
        try:
            file_obj = Path(file_name)
            if file_obj.suffix in self.tracked_extensions:
                basename = file_obj.stem
                # If basename is substantial (not just a variable placeholder)
                if len(basename) > 3:
                    # Search for files with similar names and the same extension
                    for check_dir in [from_dir, self.root_dir]:
                        for item in check_dir.glob(f"**/*{basename}*{file_obj.suffix}"):
                            return item
                # Just try to find any file with the right extension
                for check_dir in [from_dir, self.root_dir]:
                    try:
                        matches = list(check_dir.glob(f"**/*.{file_obj.suffix.lstrip('.')}"))
                        if matches:
                            self.log(f"Found potential match for '{file_name}': {matches[0]}")
                            return matches[0]
                    except Exception as e:
                        self.log(f"Error during extension glob search: {e}")
        except Exception as e:
            self.log(f"Error processing file name '{file_name}': {e}")
            
        # If we get here, we couldn't find the file
        # Let's log that it was referenced but not found
        self.log(f"WARNING: Referenced file '{file_name}' not found in the project")
        return None
    
    def parse_imports(self, file_path):
        """
        Parse import statements from a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List of imported module names
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            imported_modules = []
            
            # Process line by line to handle imports
            for line in content.split('\n'):
                for pattern in self.import_patterns:
                    match = pattern.match(line)
                    if match:
                        modules = match.group(1).strip()
                        # Handle 'import module1, module2'
                        if ',' in modules and 'import' in line.split()[0]:
                            for module in modules.split(','):
                                imported_modules.append(module.strip())
                        else:
                            imported_modules.append(modules)
            
            return imported_modules
            
        except Exception as e:
            self.log(f"Error parsing {file_path}: {e}")
            return []
    
    def parse_file_references(self, file_path):
        """
        Parse file references from a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            List of referenced file paths
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
            referenced_files = []
            
            # First, find all string literals that could be file paths
            for ext in self.tracked_extensions:
                string_literals = re.findall(r'[\'"]([^\'"]+' + re.escape(ext) + r')[\'"]', content)
                for literal in string_literals:
                    if Path(literal).suffix in self.tracked_extensions:
                        referenced_files.append(literal)
            
            # Process with regex patterns
            for line in content.split('\n'):
                for pattern in self.file_patterns:
                    for match in pattern.finditer(line):
                        # Different patterns have the file path in different groups
                        for group_idx in range(1, len(match.groups()) + 1):
                            if group_idx <= len(match.groups()):  # Ensure group exists
                                potential_file = match.group(group_idx)
                                if potential_file and isinstance(potential_file, str):
                                    # Check if it has one of the tracked extensions
                                    file_obj = Path(potential_file)
                                    if file_obj.suffix in self.tracked_extensions:
                                        referenced_files.append(potential_file)
                                        break
                                    # Check if it might be a path with the extension we care about
                                    elif any(ext in potential_file for ext in self.tracked_extensions):
                                        referenced_files.append(potential_file)
                                        break
            
            # Special check for common patterns like loading a JSON config
            if '.json' in self.tracked_extensions:
                json_patterns = [
                    r'config_file\s*=\s*[\'"]([^\'"]+)[\'"]',
                    r'with\s+open\([\'"]([^\'"]+\.json)[\'"]',
                    r'json.load\(open\([\'"]([^\'"]+)[\'"]'
                ]
                for pattern in json_patterns:
                    matches = re.findall(pattern, content)
                    referenced_files.extend(matches)
            
            # Special check for TeX files
            if '.tex' in self.tracked_extensions:
                tex_patterns = [
                    r'template_file\s*=\s*[\'"]([^\'"]+\.tex)[\'"]',
                    r'with\s+open\([\'"]([^\'"]+\.tex)[\'"]'
                ]
                for pattern in tex_patterns:
                    matches = re.findall(pattern, content)
                    referenced_files.extend(matches)
            
            # Remove duplicates and filter non-relevant files
            unique_files = []
            for file_ref in referenced_files:
                if file_ref not in unique_files:
                    unique_files.append(file_ref)
            
            return unique_files
            
        except Exception as e:
            self.log(f"Error parsing file references in {file_path}: {e}")
            return []
    
    def is_standard_library(self, module_name):
        """
        Check if a module is part of the standard library.
        
        Args:
            module_name: Name of the module to check
            
        Returns:
            bool: True if the module is in the standard library
        """
        # Remove relative import dots
        clean_name = module_name.lstrip('.')
        # Get the top-level module name
        top_module = clean_name.split('.')[0] if clean_name else ''
        
        return top_module in self.std_lib_modules
    
    def track_dependencies(self, file_path=None, is_root=False):
        """
        Recursively track dependencies of a file.
        
        Args:
            file_path: Path to the file to analyze
            is_root: Whether this is the root file
        """
        if file_path is None:
            file_path = self.root_file
            
        file_path = Path(file_path).resolve()
        
        # Skip if already processed to avoid circular imports
        if file_path in self.processed_files:
            return
            
        self.processed_files.add(file_path)
        
        # Add to dependencies if not excluded
        try:
            relative_path = file_path.relative_to(self.root_dir)
            rel_path_str = str(relative_path)
            
            # Skip excluded paths
            if any(excl in rel_path_str for excl in self.excluded_paths) or \
               file_path.name in self.excluded_paths:
                self.log(f"Skipping excluded path: {rel_path_str}")
                return
            
            # Add to dependencies (including root file)
            self.dependencies.add(rel_path_str)
        except ValueError:
            # If path can't be made relative, just use filename
            # Also check if it should be excluded
            if file_path.name in self.excluded_paths:
                self.log(f"Skipping excluded file: {file_path.name}")
                return
            self.dependencies.add(file_path.name)
        
        # Only parse Python files for imports and references
        if file_path.suffix != '.py':
            return
            
        # Get imported modules
        imported_modules = self.parse_imports(file_path)
        
        # Process each imported module
        for module_name in imported_modules:
            # Skip standard library modules
            if self.is_standard_library(module_name):
                continue
                
            # Find the file for this module
            module_file = self.find_file(module_name, file_path)
            
            if module_file:
                # Recursively process this module
                self.track_dependencies(module_file)
            else:
                self.log(f"Could not find module: {module_name}")
        
        # Get referenced files
        referenced_files = self.parse_file_references(file_path)
        
        self.log(f"Found {len(referenced_files)} potential file references in {file_path.name}")
        
        # Process each referenced file
        for file_name in referenced_files:
            # Check if this file should be excluded
            if any(excl in file_name for excl in self.excluded_paths) or \
               Path(file_name).name in self.excluded_paths:
                self.log(f"Skipping excluded referenced file: {file_name}")
                continue
                
            # Try to resolve the file path
            referenced_file = self.resolve_file_path(file_name, file_path)
            
            # If file was found, process it
            if referenced_file:
                # Check again if it should be excluded (using the resolved path)
                try:
                    rel_path = str(referenced_file.relative_to(self.root_dir))
                    if any(excl in rel_path for excl in self.excluded_paths) or \
                       referenced_file.name in self.excluded_paths:
                        self.log(f"Skipping excluded resolved file: {rel_path}")
                        continue
                except ValueError:
                    if referenced_file.name in self.excluded_paths:
                        self.log(f"Skipping excluded file: {referenced_file.name}")
                        continue
                
                self.log(f"  Found file: {referenced_file}")
                # If it's a Python file, recursively process it
                if referenced_file.suffix == '.py':
                    self.track_dependencies(referenced_file)
                # Otherwise just add it to dependencies
                elif referenced_file.suffix in self.tracked_extensions:
                    try:
                        relative_path = referenced_file.relative_to(self.root_dir)
                        rel_path_str = str(relative_path)
                        # Final exclusion check
                        if any(excl in rel_path_str for excl in self.excluded_paths):
                            self.log(f"Skipping excluded file: {rel_path_str}")
                            continue
                        self.dependencies.add(rel_path_str)
                    except ValueError:
                        self.dependencies.add(referenced_file.name)
            else:
                # Handle file not found but has a tracked extension
                file_obj = Path(file_name)
                if file_obj.suffix in self.tracked_extensions:
                    # Check if this not-found file should be excluded
                    if any(excl in file_name for excl in self.excluded_paths) or \
                       file_obj.name in self.excluded_paths:
                        self.log(f"Skipping excluded not-found file: {file_name}")
                        continue
                        
                    self.log(f"  Potential {file_obj.suffix} file referenced but not found: {file_name}")
                    # Add as a reference with a note
                    self.dependencies.add(f"{file_name} (referenced but not found)")
    
    def scan_directory_for_tracked_files(self):
        """
        Scan the project directory for files with tracked extensions.
        
        Returns:
            Dictionary mapping extensions to lists of file paths
        """
        result = {}
        for ext in self.tracked_extensions:
            result[ext] = []
            for file_path in self.root_dir.glob(f"**/*{ext}"):
                try:
                    rel_path = str(file_path.relative_to(self.root_dir))
                    
                    # Skip excluded paths
                    if any(excl in rel_path for excl in self.excluded_paths) or \
                       file_path.name in self.excluded_paths:
                        self.log(f"Skipping excluded file in scan: {rel_path}")
                        continue
                        
                    result[ext].append(rel_path)
                except ValueError:
                    # Skip files outside project directory
                    pass
        return result
    
    def generate_dependency_list(self, output_file="project_dependencies.txt", scan_dir=False):
        """
        Generate a list of all dependencies and save to a file.
        
        Args:
            output_file: Path to the output file
            scan_dir: Whether to scan the directory for tracked file types
            
        Returns:
            List of dependency file paths
        """
        self.track_dependencies(is_root=True)
        
        # Sort dependencies for consistency
        sorted_deps = sorted(self.dependencies)
        
        # Filter out "referenced but not found" entries
        clean_deps = [dep for dep in sorted_deps if "not found" not in dep]
        
        # Write to file - clean output format with just filenames
        with open(output_file, 'w', encoding='utf-8') as file:
            for dep in clean_deps:
                file.write(f"{dep}\n")
                
        # Print summary to console - always show the output filename
        print(f"Dependency analysis complete.")
        print(f"Found {len(clean_deps)} dependent files.")
        print(f"Results saved to {output_file}")
        
        # Additional verbose output if enabled
        if self.verbose:
            for dep in clean_deps:
                print(f"  {dep}")
        
        # If scan_dir is enabled, check for other files
        if scan_dir:
            if self.verbose:
                print("\nPerforming additional directory scan for tracked file types...")
            dir_scan = self.scan_directory_for_tracked_files()
            
            # Check which files weren't detected through dependencies
            all_missed_files = []
            for ext, files in dir_scan.items():
                if files:
                    # Check which ones were not detected through dependencies
                    detected_files = [dep for dep in clean_deps if dep.endswith(ext)]
                    detected_paths = set(detected_files)
                    
                    missed_files = [f for f in files if f not in detected_paths]
                    all_missed_files.extend(missed_files)
            
            # Add missed files to the dependency list if they were found in the directory scan
            if all_missed_files:
                # Sort the missed files
                all_missed_files.sort()
                
                # Append to the file
                with open(output_file, 'a', encoding='utf-8') as file:
                    for f in all_missed_files:
                        file.write(f"{f}\n")
                        
                print(f"Added {len(all_missed_files)} additional files found during directory scan.")
                if self.verbose:
                    for f in all_missed_files:
                        print(f"  {f}")
                    
                # Update the return value
                clean_deps.extend(all_missed_files)
            
        return clean_deps


def track_dependencies(root_file="main_qt.py", output_file="project_dependencies.txt", 
                      extensions=None, verbose=False, scan_dir=False, exclude=None):
    """
    Track project dependencies and save to a file.
    
    Args:
        root_file (str): Root Python file to analyze
        output_file (str): Output file for the dependency list
        extensions (list): List of additional file extensions to track
        verbose (bool): Enable verbose output
        scan_dir (bool): Scan directory for tracked file types
        exclude (list): List of files or directories to exclude
        
    Returns:
        list: List of dependency file paths
    """
    tracker = DependencyTracker(root_file)
    tracker.set_verbose(verbose)
    
    # Add custom extensions
    if extensions:
        for ext in extensions:
            if ext.startswith('.'):
                tracker.tracked_extensions.add(ext)
            else:
                tracker.tracked_extensions.add(f'.{ext}')
    
    # Add custom exclusions
    if exclude:
        for item in exclude:
            tracker.excluded_paths.add(item)
    
    return tracker.generate_dependency_list(output_file, scan_dir)


def main():
    """
    Main function to parse arguments and run the dependency tracker.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    parser = argparse.ArgumentParser(description='Generate a list of project file dependencies.')
    parser.add_argument('root_file', nargs='?', default='main_qt.py',
                        help='Root Python file to analyze (default: main_qt.py)')
    parser.add_argument('-o', '--output', default='project_dependencies.txt',
                        help='Output file name (default: project_dependencies.txt)')
    parser.add_argument('-e', '--extensions', default='.tex,.json',
                        help='Additional file extensions to track (comma-separated, default: .tex,.json)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose output for debugging')
    parser.add_argument('-s', '--scan-dir', action='store_true',
                        help='Scan the entire directory for tracked file types')
    parser.add_argument('-x', '--exclude', default='',
                        help='Comma-separated list of files or directories to exclude')
    args = parser.parse_args()
    
    # Check if root file exists
    if not os.path.isfile(args.root_file):
        print(f"Error: File '{args.root_file}' not found.")
        return 1
    
    print(f"Tracking dependencies with extensions: {args.extensions}")
    
    # Convert extensions string to list
    extension_list = []
    if args.extensions:
        extension_list = args.extensions.split(',')
    
    # Initialize tracker
    tracker = DependencyTracker(args.root_file)
    tracker.set_verbose(args.verbose)
    
    # Add custom extensions
    if extension_list:
        for ext in extension_list:
            if ext.startswith('.'):
                tracker.tracked_extensions.add(ext)
            else:
                tracker.tracked_extensions.add(f'.{ext}')
    
    # Add custom exclusions
    if args.exclude:
        for item in args.exclude.split(','):
            tracker.excluded_paths.add(item.strip())
            
    if args.verbose:
        print(f"Excluded paths: {tracker.excluded_paths}")
    
    # Track dependencies
    tracker.generate_dependency_list(args.output, args.scan_dir)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())