"""
Database interface components for the Simplified Math Editor.

This module provides UI components and functionality to integrate
the math problem database with the editor interface.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import re
from db.math_db import MathProblemDB


class DatabaseInterface:
    """UI components for database integration with the editor"""
    
    def __init__(self, editor):
        """
        Initialize the database interface
        
        Args:
            editor: Reference to the MathEditor instance
        """
        self.editor = editor
        self.db = MathProblemDB()
        
        # The menu will be created later when setup_menu is called
    
    def setup_menu(self):
        """Create database menu in the main menubar"""
        # This method should be called after the editor's menubar is created
        self.create_database_menu()
    
    def create_database_menu(self):
        """Create database menu in the main menubar"""
        # Get the menubar from the editor
        menubar = self.editor.menubar
        
        # Create database menu
        self.db_menu = tk.Menu(menubar, tearoff=0)
        self.db_menu.add_command(label="Save Problem to Database...", command=self.save_problem_dialog)
        self.db_menu.add_command(label="Load Problem from Database...", command=self.load_problem_dialog)
        self.db_menu.add_separator()
        self.db_menu.add_command(label="Manage Categories...", command=self.manage_categories_dialog)
        self.db_menu.add_separator()
        self.db_menu.add_command(label="Search Problems...", command=self.search_problems_dialog)
        
        # Add the database menu to the menubar
        menubar.add_cascade(label="Database", menu=self.db_menu)
    
    def save_problem_dialog(self):
        """Show dialog to save current problem to database"""
        # Create a dialog
        dialog = tk.Toplevel(self.editor.root)
        dialog.title("Save Problem to Database")
        dialog.geometry("500x850")
        dialog.transient(self.editor.root)
        dialog.grab_set()
        
        # Create the dialog content
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Variables for form fields
        title_var = tk.StringVar()
        source_var = tk.StringVar()
        solution_var = tk.StringVar()
        latex_solution_var = tk.BooleanVar(value=False)
        
        # Title
        ttk.Label(frame, text="Title:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=title_var, width=40).grid(row=0, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Source
        ttk.Label(frame, text="Source:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        ttk.Entry(frame, textvariable=source_var, width=40).grid(row=1, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Categories
        ttk.Label(frame, text="Categories:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        
        # Categories frame with checkboxes
        categories_frame = ttk.Frame(frame)
        categories_frame.grid(row=2, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Get all categories from database
        success, categories = self.db.get_categories()
        if not success:
            categories = []
        
        # Category variables and checkboxes
        category_vars = {}
        for i, category in enumerate(categories):
            var = tk.BooleanVar(value=False)
            category_vars[category["category_id"]] = (var, category["name"])
            ttk.Checkbutton(categories_frame, text=category["name"], variable=var).grid(
                row=i // 2, column=i % 2, sticky=tk.W, padx=5, pady=2)
        
        # New category button
        ttk.Button(
            categories_frame, 
            text="Add New Category", 
            command=lambda: self.add_new_category_dialog(categories_frame, category_vars)
        ).grid(row=(len(categories) // 2) + 1, column=0, columnspan=2, pady=5)
        
        # Notes
        ttk.Label(frame, text="Notes:").grid(row=3, column=0, sticky=tk.W+tk.N, padx=5, pady=5)
        notes_text = tk.Text(frame, height=4, width=40)
        notes_text.grid(row=3, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # Solution
        ttk.Label(frame, text="Solution:").grid(row=4, column=0, sticky=tk.W+tk.N, padx=5, pady=5)
        solution_text = tk.Text(frame, height=8, width=40)
        solution_text.grid(row=4, column=1, sticky=tk.W+tk.E, padx=5, pady=5)
        
        # LaTeX solution checkbox
        ttk.Checkbutton(
            frame, 
            text="Solution contains LaTeX formatting", 
            variable=latex_solution_var
        ).grid(row=5, column=1, sticky=tk.W, padx=5, pady=2)
        
        # Preview of content
        ttk.Label(frame, text="Problem Preview:").grid(row=6, column=0, columnspan=2, sticky=tk.W, padx=5, pady=5)
        
        # Get the current content from editor
        content = self.editor.editor.get_content()
        
        # Create a read-only text widget to show content preview
        preview_text = tk.Text(frame, height=10, width=50)
        preview_text.grid(row=7, column=0, columnspan=2, sticky=tk.W+tk.E, padx=5, pady=5)
        preview_text.insert(tk.END, content[:500] + ("..." if len(content) > 500 else ""))
        preview_text.config(state=tk.DISABLED)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.grid(row=8, column=0, columnspan=2, pady=10)
        
        # Save button
        ttk.Button(
            button_frame, 
            text="Save", 
            command=lambda: self.save_problem_to_db(
                dialog,
                title_var.get(),
                content,
                solution_text.get("1.0", tk.END),
                latex_solution_var.get(),
                source_var.get(),
                notes_text.get("1.0", tk.END),
                category_vars
            )
        ).pack(side=tk.RIGHT, padx=5)
        
        # Cancel button
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Configure grid
        frame.columnconfigure(1, weight=1)
        
        # Center the dialog on the screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def add_new_category_dialog(self, parent_frame, category_vars):
        """Show dialog to add a new category"""
        new_category = simpledialog.askstring("New Category", "Enter a new category name:")
        
        if new_category and new_category.strip():
            # Add the category to the database
            success, category_id = self.db.add_category(new_category.strip())
            
            if success:
                # Add a new checkbox for this category
                var = tk.BooleanVar(value=True)
                category_vars[category_id] = (var, new_category.strip())
                
                # Determine row and column for the new checkbox
                num_existing = len(category_vars) - 1  # -1 because we just added one
                row = num_existing // 2
                col = num_existing % 2
                
                # Add the new checkbox
                ttk.Checkbutton(parent_frame, text=new_category.strip(), variable=var).grid(
                    row=row, column=col, sticky=tk.W, padx=5, pady=2)
                
                # Update the position of the "Add New Category" button
                for widget in parent_frame.winfo_children():
                    if widget.winfo_class() == 'TButton':
                        widget.grid_forget()
                        widget.grid(row=(len(category_vars) // 2) + 1, column=0, columnspan=2, pady=5)
            else:
                messagebox.showerror("Error", f"Failed to add category: {category_id}")
    
    def save_problem_to_db(self, dialog, title, content, solution, has_latex_solution, 
                          source, notes, category_vars):
        """Save problem to database"""
        # Validate required fields
        if not title:
            messagebox.showerror("Error", "Title is required")
            return
        
        if not content:
            messagebox.showerror("Error", "Problem content is empty")
            return
        
        try:
            # Extract selected categories
            selected_categories = []
            for category_id, (var, name) in category_vars.items():
                if var.get():
                    selected_categories.append(name)
            
            # Convert has_latex_solution to integer
            latex_solution_int = 1 if has_latex_solution else 0
            
            # First, add the problem to get the problem_id
            success, problem_id = self.db.add_problem(
                title=title,
                content=content,
                solution=solution,
                has_latex_solution=latex_solution_int,
                source=source,
                notes=notes,
                categories=selected_categories
            )
            
            if not success:
                messagebox.showerror("Error", f"Failed to save problem: {problem_id}")
                return
            
            # Next, handle images in the content
            image_pattern = r'\\includegraphics(?:\[.*?\])?\{([^{}]+)\}'
            image_names = re.findall(image_pattern, content)
            
            if image_names:
                messagebox.showinfo("Images Found", 
                                   f"Found {len(image_names)} image references in the problem.\n"
                                   f"Image handling will be implemented in a future update.")
            
            # Close the dialog
            dialog.destroy()
            
            # Show success message
            messagebox.showinfo("Success", f"Problem '{title}' saved to database")
            
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def load_problem_dialog(self):
        """Show dialog to load a problem from database"""
        # Create dialog
        dialog = tk.Toplevel(self.editor.root)
        dialog.title("Load Problem from Database")
        dialog.geometry("700x500")
        dialog.transient(self.editor.root)
        dialog.grab_set()
        
        # Create the dialog content
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Search frame
        search_frame = ttk.Frame(frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Category filter
        ttk.Label(search_frame, text="Category:").pack(side=tk.LEFT, padx=5)
        category_var = tk.StringVar()
        
        # Get categories
        success, categories = self.db.get_categories()
        if not success:
            categories = []
        
        # Add "All Categories" option
        category_options = [("All Categories", None)]
        category_options.extend([(cat["name"], cat["category_id"]) for cat in categories])
        
        category_menu = ttk.Combobox(search_frame, textvariable=category_var, width=20)
        category_menu['values'] = [cat[0] for cat in category_options]
        category_menu.current(0)
        category_menu.pack(side=tk.LEFT, padx=5)
        
        # Search button
        ttk.Button(
            search_frame, 
            text="Search", 
            command=lambda: self.search_problems(
                search_var.get(), 
                dict(category_options)[category_var.get()],
                problem_tree
            )
        ).pack(side=tk.LEFT, padx=5)
        
        # Problems list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create treeview for problems
        columns = ("ID", "Title", "Source", "Date")
        problem_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        # Configure columns
        problem_tree.heading("ID", text="#")
        problem_tree.heading("Title", text="Title")
        problem_tree.heading("Source", text="Source")
        problem_tree.heading("Date", text="Modified")
        
        problem_tree.column("ID", width=50)
        problem_tree.column("Title", width=300)
        problem_tree.column("Source", width=150)
        problem_tree.column("Date", width=150)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=problem_tree.yview)
        problem_tree.configure(yscrollcommand=y_scrollbar.set)
        
        # Pack the treeview and scrollbar
        problem_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        
        # Problem preview frame
        preview_frame = ttk.LabelFrame(frame, text="Problem Preview")
        preview_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Preview text widget
        preview_text = tk.Text(preview_frame, height=5, width=80, wrap=tk.WORD)
        preview_text.pack(fill=tk.X, padx=5, pady=5)
        preview_text.config(state=tk.DISABLED)
        
        # Bind selection event to show preview
        problem_tree.bind("<<TreeviewSelect>>", 
                         lambda event: self.show_problem_preview(event, problem_tree, preview_text))
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Load button
        ttk.Button(
            button_frame, 
            text="Load", 
            command=lambda: self.load_problem(dialog, problem_tree)
        ).pack(side=tk.RIGHT, padx=5)
        
        # Cancel button
        ttk.Button(
            button_frame, 
            text="Cancel", 
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
        
        # Initial search to populate the list
        self.search_problems("", None, problem_tree)
        
        # Center the dialog on the screen
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    
    def search_problems(self, search_term, category_id, tree_widget):
        """Search problems and populate the tree view"""
        # Clear the current tree
        for item in tree_widget.get_children():
            tree_widget.delete(item)
            
        # Search problems
        success, problems = self.db.get_problems_list(category_id, search_term)
        
        if not success:
            messagebox.showerror("Error", f"Failed to search problems: {problems}")
            return
        
        # Add problems to tree
        for problem in problems:
            # Format the date
            date_str = problem["last_modified"].split("T")[0] if "T" in problem["last_modified"] else problem["last_modified"]
            
            tree_widget.insert(
                "", 
                tk.END, 
                values=(
                    problem["problem_id"],
                    problem["title"],
                    problem["source"] or "",
                    date_str
                ),
                tags=(str(problem["problem_id"]),)
            )
    
    def show_problem_preview(self, event, tree_widget, preview_text):
        """Show preview of the selected problem"""
        # Get the selected item
        selection = tree_widget.selection()
        if not selection:
            return
            
        # Get the problem ID
        problem_id = tree_widget.item(selection[0])["values"][0]
        
        # Get the problem from the database
        success, problem = self.db.get_problem(problem_id)
        
        if not success:
            return
        
        # Update the preview
        preview_text.config(state=tk.NORMAL)
        preview_text.delete("1.0", tk.END)
        
        # Add preview content
        preview_content = problem["content"]
        # Limit to first 200 characters
        if len(preview_content) > 200:
            preview_content = preview_content[:200] + "..."
            
        preview_text.insert(tk.END, preview_content)
        preview_text.config(state=tk.DISABLED)
    
    def load_problem(self, dialog, tree_widget):
        """Load the selected problem into the editor"""
        # Get the selected item
        selection = tree_widget.selection()
        if not selection:
            messagebox.showinfo("Selection Required", "Please select a problem to load")
            return
            
        # Get the problem ID
        problem_id = tree_widget.item(selection[0])["values"][0]
        
        # Get the problem from database
        success, problem = self.db.get_problem(problem_id)
        
        if not success:
            messagebox.showerror("Error", f"Failed to load problem: {problem}")
            return
        
        # Ask for confirmation if there is content in the editor
        current_content = self.editor.editor.get_content().strip()
        if current_content:
            if not messagebox.askyesno("Confirm", "Current content will be replaced. Continue?"):
                return
        
        # Check for images in the problem
        image_pattern = r'\\includegraphics(?:\[.*?\])?\{([^{}]+)\}'
        image_names = re.findall(image_pattern, problem["content"])
        
        if image_names:
            messagebox.showinfo("Images", 
                               f"The problem contains {len(image_names)} image references.\n"
                               f"Image handling will be implemented in a future update.")
        
        # Load content into editor
        self.editor.editor.set_content(problem["content"])
        
        # Close the dialog
        dialog.destroy()
        
        # Update preview
        self.editor.update_preview()
        
        # Show success message
        messagebox.showinfo("Success", f"Problem '{problem['title']}' loaded from database")
    
    def manage_categories_dialog(self):
        """Show dialog to manage categories"""
        # Create dialog
        dialog = tk.Toplevel(self.editor.root)
        dialog.title("Manage Categories")
        dialog.geometry("400x400")
        dialog.transient(self.editor.root)
        dialog.grab_set()
        
        # Create the dialog content
        frame = ttk.Frame(dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(frame, text="Math Problem Categories", font=("", 12, "bold")).pack(pady=10)
        
        # Categories list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create listbox with scrollbar
        categories_listbox = tk.Listbox(list_frame, height=15)
        categories_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=categories_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        categories_listbox.config(yscrollcommand=scrollbar.set)
        
        # Populate the listbox
        self.update_categories_listbox(categories_listbox)
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X, padx=5, pady=10)
        
        # Add button
        ttk.Button(
            button_frame, 
            text="Add Category", 
            command=lambda: self.add_category_dialog(categories_listbox)
        ).pack(side=tk.LEFT, padx=5)
        
        # Edit button
        ttk.Button(
            button_frame, 
            text="Edit", 
            command=lambda: self.edit_category_dialog(categories_listbox)
        ).pack(side=tk.LEFT, padx=5)
        
        # Delete button
        ttk.Button(
            button_frame, 
            text="Delete", 
            command=lambda: self.delete_category_dialog(categories_listbox)
        ).pack(side=tk.LEFT, padx=5)
        
        # Close button
        ttk.Button(
            button_frame, 
            text="Close", 
            command=dialog.destroy
        ).pack(side=tk.RIGHT, padx=5)
    
    def update_categories_listbox(self, listbox):
        """Update the categories listbox"""
        # Clear the listbox
        listbox.delete(0, tk.END)
        
        # Get all categories
        success, categories = self.db.get_categories()
        
        if not success:
            messagebox.showerror("Error", f"Failed to get categories: {categories}")
            return
        
        # Store categories for reference
        self.categories_cache = categories
        
        # Add categories to listbox
        for category in categories:
            listbox.insert(tk.END, category["name"])
            
        # Set the first item as selected if there are any categories
        if categories:
            listbox.selection_set(0)
    
    def add_category_dialog(self, listbox):
        """Show dialog to add a new category"""
        # Ask for new category name
        new_category = simpledialog.askstring("New Category", "Enter a new category name:")
        
        if new_category and new_category.strip():
            # Add to database
            success, result = self.db.add_category(new_category.strip())
            
            if success:
                # Update the listbox
                self.update_categories_listbox(listbox)
            else:
                messagebox.showerror("Error", f"Failed to add category: {result}")
    
    def edit_category_dialog(self, listbox):
        """Show dialog to edit a category"""
        # Get the selected category
        selection = listbox.curselection()
        if not selection:
            messagebox.showinfo("Selection Required", "Please select a category to edit")
            return
            
        # Get the category name and ID
        category_name = listbox.get(selection[0])
        category_id = None
        
        # Find the category ID
        for category in self.categories_cache:
            if category["name"] == category_name:
                category_id = category["category_id"]
                break
                
        if not category_id:
            messagebox.showerror("Error", "Category not found")
            return
            
        # Ask for new name
        new_name = simpledialog.askstring("Edit Category", "Enter new category name:", initialvalue=category_name)
        
        if new_name and new_name.strip():
            # Update in database
            success, result = self.db.update_category(category_id, new_name.strip())
            
            if success:
                # Update the listbox
                self.update_categories_listbox(listbox)
            else:
                messagebox.showerror("Error", f"Failed to update category: {result}")
    
    def delete_category_dialog(self, listbox):
        """Show dialog to delete a category"""
        # Get the selected category
        selection = listbox.curselection()
        if not selection:
            messagebox.showinfo("Selection Required", "Please select a category to delete")
            return
            
        # Get the category name and ID
        category_name = listbox.get(selection[0])
        category_id = None
        
        # Find the category ID
        for category in self.categories_cache:
            if category["name"] == category_name:
                category_id = category["category_id"]
                break
                
        if not category_id:
            messagebox.showerror("Error", "Category not found")
            return
        
        # Confirm deletion
        if not messagebox.askyesno("Confirm Delete", 
                                 f"Are you sure you want to delete the category '{category_name}'?\n\n"
                                 f"This will remove this category from all problems but will not delete the problems."):
            return
            
        # Delete from database
        success, result = self.db.delete_category(category_id)
        
        if success:
            # Update the listbox
            self.update_categories_listbox(listbox)
        else:
            messagebox.showerror("Error", f"Failed to delete category: {result}")
    
    def search_problems_dialog(self):
        """Show dialog to search problems"""
        # This is already implemented as part of the load_problem_dialog
        # Just call that method as it includes search functionality
        self.load_problem_dialog()