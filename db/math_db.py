"""
Math problem database for the Simplified Math Editor.

This module provides functionality to store and retrieve math problems,
their solutions, associated images, and categories in an SQLite database.
"""

import sqlite3
import os
import datetime
import io
from pathlib import Path
import tempfile
from PIL import Image

class MathProblemDB:
    """Database manager for math problems and related data"""
    
    def __init__(self, db_path=None):
        """
        Initialize the math problem database
        
        Args:
            db_path (str, optional): Path to the SQLite database file.
                                    If None, a default path will be used.
        """
        if db_path is None:
            # Use a default location in the /db folder
            db_dir = Path("db")
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / "math_problems.db"
            
        self.db_path = str(db_path)
        self.conn = sqlite3.connect(self.db_path)
        
        # Enable foreign key constraints
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Create cursor
        self.cur = self.conn.cursor()
        
        # Create tables if they don't exist
        self._create_tables()
    
    def _create_tables(self):
        """Create the necessary database tables if they don't exist"""
        # Problems table - Modified schema: removed title, source; added answer
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problems (
                problem_id INTEGER PRIMARY KEY,
                content TEXT NOT NULL,
                solution TEXT,
                has_latex_solution INTEGER DEFAULT 0,
                answer TEXT,
                notes TEXT,
                earmark INTEGER DEFAULT 0,
                creation_date TEXT NOT NULL,
                last_modified TEXT NOT NULL
            )
        ''')
        
        # Check if answer column exists, add it if it doesn't
        self.cur.execute("PRAGMA table_info(problems)")
        columns = [col[1] for col in self.cur.fetchall()]
        if 'answer' not in columns:
            self.cur.execute('ALTER TABLE problems ADD COLUMN answer TEXT')
            self.conn.commit()
            print("Added 'answer' column to problems table")
        
        # Problem images table
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problem_images (
                image_id INTEGER PRIMARY KEY,
                problem_id INTEGER NOT NULL,
                image_data BLOB NOT NULL,
                image_name TEXT NOT NULL,
                format TEXT,
                width INTEGER,
                height INTEGER,
                FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE
            )
        ''')
        
        # Math categories table
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS math_categories (
                category_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Problem sets table
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problem_sets (
                set_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                is_ordered INTEGER DEFAULT 0
            )
        ''')
        
        # Problem set members table
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problem_set_member (
                set_id INTEGER NOT NULL REFERENCES problem_sets(set_id) ON DELETE CASCADE,
                problem_id INTEGER NOT NULL REFERENCES problems(problem_id) ON DELETE CASCADE,
                order_index INTEGER,
                PRIMARY KEY (set_id, problem_id)
            )
        ''')
        
        # Problem types table
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problem_types (
                type_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            )
        ''')
        
        # Problem-problem_types join table
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problem_problem_types (
                problem_id INTEGER NOT NULL,
                type_id INTEGER NOT NULL,
                PRIMARY KEY (problem_id, type_id),
                FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE,
                FOREIGN KEY (type_id) REFERENCES problem_types(type_id) ON DELETE CASCADE
            )
        ''')
        
        # Problem-image mapping table
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problem_image_map (
                problem_id INTEGER NOT NULL,
                image_name TEXT NOT NULL,
                PRIMARY KEY (problem_id, image_name),
                FOREIGN KEY (problem_id) REFERENCES problems(problem_id) ON DELETE CASCADE
            )
        ''')
        
        # Create indices for faster querying
        self.cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_problem_images_problem_id 
            ON problem_images(problem_id)
        ''')
        
        self.cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_problem_math_categories_problem_id 
            ON problem_math_categories(problem_id)
        ''')
        
        self.cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_problem_math_categories_category_id 
            ON problem_math_categories(category_id)
        ''')
        
        self.conn.commit()
    
    def add_problem(self, content, solution=None, has_latex_solution=0, 
                   answer=None, notes=None, earmark=0, categories=None):
        """
        Add a new math problem to the database
        
        Args:
            content (str): LaTeX content of the problem
            solution (str, optional): Solution to the problem
            has_latex_solution (int, optional): 1 if solution contains LaTeX, 0 otherwise
            answer (str, optional): Plain text answer (no LaTeX)
            notes (str, optional): Additional notes about the problem
            earmark (int, optional): Earmark value for the problem
            categories (list, optional): List of category names to associate with the problem
            
        Returns:
            tuple: (success, problem_id or error_message)
        """
        try:
            # Get current date and time
            now = datetime.datetime.now().isoformat()
            
            # Insert problem
            self.cur.execute('''
                INSERT INTO problems 
                (content, solution, has_latex_solution, answer, notes, earmark, creation_date, last_modified)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (content, solution, has_latex_solution, answer, notes, earmark, now, now))
            
            # Get the problem_id of the inserted problem
            problem_id = self.cur.lastrowid
            
            # Add categories if provided
            if categories:
                for category_name in categories:
                    self.add_problem_to_category(problem_id, category_name)
            
            self.conn.commit()
            return (True, problem_id)
            
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))
    
    def update_problem(self, problem_id, content=None, solution=None, 
                      has_latex_solution=None, answer=None, notes=None, earmark=None):
        """
        Update an existing math problem
        
        Args:
            problem_id (int): ID of the problem to update
            content (str, optional): Updated LaTeX content
            solution (str, optional): Updated solution
            has_latex_solution (int, optional): Updated solution type flag
            answer (str, optional): Updated plain text answer
            notes (str, optional): Updated notes
            earmark (int, optional): Updated earmark value
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Get the current problem data
            self.cur.execute("SELECT * FROM problems WHERE problem_id = ?", (problem_id,))
            problem = self.cur.fetchone()
            
            if not problem:
                return (False, f"Problem with ID {problem_id} not found")
            
            # Create column names and updated values lists
            columns = []
            values = []
            
            # Update only provided fields
            if content is not None:
                columns.append("content = ?")
                values.append(content)
            
            if solution is not None:
                columns.append("solution = ?")
                values.append(solution)
            
            if has_latex_solution is not None:
                columns.append("has_latex_solution = ?")
                values.append(has_latex_solution)
            
            if answer is not None:
                columns.append("answer = ?")
                values.append(answer)
            
            if notes is not None:
                columns.append("notes = ?")
                values.append(notes)
            
            if earmark is not None:
                columns.append("earmark = ?")
                values.append(earmark)
            
            # Add last modified timestamp
            columns.append("last_modified = ?")
            values.append(datetime.datetime.now().isoformat())
            
            # Add problem_id to values
            values.append(problem_id)
            
            # If no updates, return early
            if not columns:
                return (True, "No changes to update")
            
            # Build and execute update query
            query = f"UPDATE problems SET {', '.join(columns)} WHERE problem_id = ?"
            self.cur.execute(query, values)
            
            self.conn.commit()
            return (True, "Problem updated successfully")
            
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))
    
    def delete_problem(self, problem_id):
        """
        Delete a math problem and all associated data
        
        Args:
            problem_id (int): ID of the problem to delete
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Check if problem exists
            self.cur.execute("SELECT problem_id FROM problems WHERE problem_id = ?", (problem_id,))
            if not self.cur.fetchone():
                return (False, f"Problem with ID {problem_id} not found")
            
            # Delete the problem (cascade will delete associated images and category relationships)
            self.cur.execute("DELETE FROM problems WHERE problem_id = ?", (problem_id,))
            
            self.conn.commit()
            return (True, f"Problem with ID {problem_id} deleted successfully")
            
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))
    
    def get_problem(self, problem_id, with_images=True, with_categories=True):
        """
        Get a math problem by ID
        
        Args:
            problem_id (int): ID of the problem to retrieve
            with_images (bool): Whether to include image data
            with_categories (bool): Whether to include category data
            
        Returns:
            tuple: (success, problem_data or error_message)
        """
        try:
            # Get problem data
            self.cur.execute("""
                SELECT problem_id, content, solution, has_latex_solution, 
                       answer, notes, earmark, creation_date, last_modified 
                FROM problems WHERE problem_id = ?
            """, (problem_id,))
            
            problem = self.cur.fetchone()
            if not problem:
                return (False, f"Problem with ID {problem_id} not found")
            
            # Convert to dictionary
            problem_dict = {
                "problem_id": problem[0],
                "content": problem[1],
                "solution": problem[2],
                "has_latex_solution": problem[3],
                "answer": problem[4],
                "notes": problem[5],
                "earmark": problem[6],
                "creation_date": problem[7],
                "last_modified": problem[8]
            }
            
            # Get associated images
            if with_images:
                self.cur.execute("""
                    SELECT image_id, image_name, format, width, height 
                    FROM problem_images 
                    WHERE problem_id = ?
                """, (problem_id,))
                
                images = []
                for img in self.cur.fetchall():
                    images.append({
                        "image_id": img[0],
                        "image_name": img[1],
                        "format": img[2],
                        "width": img[3],
                        "height": img[4]
                        # Note: image_data blob is not included here to keep response size manageable
                    })
                
                problem_dict["images"] = images
            
            # Get associated categories
            if with_categories:
                self.cur.execute("""
                    SELECT c.category_id, c.name 
                    FROM math_categories c
                    JOIN problem_math_categories pc ON c.category_id = pc.category_id
                    WHERE pc.problem_id = ?
                """, (problem_id,))
                
                categories = []
                for cat in self.cur.fetchall():
                    categories.append({
                        "category_id": cat[0],
                        "name": cat[1]
                    })
                
                problem_dict["categories"] = categories
            
            return (True, problem_dict)
            
        except Exception as e:
            return (False, str(e))
    
    def get_problems_list(self, category_id=None, search_term=None, limit=100, offset=0):
        """
        Get a list of problems, optionally filtered by category or search term
        
        Args:
            category_id (int, optional): Filter by category ID
            search_term (str, optional): Search in content, answer, and notes
            limit (int, optional): Maximum number of results to return
            offset (int, optional): Offset for pagination
            
        Returns:
            tuple: (success, list_of_problems or error_message)
        """
        try:
            # First get the problems
            query = """
                SELECT DISTINCT p.problem_id, p.content, p.answer, p.earmark, p.creation_date, p.last_modified
                FROM problems p
            """
            
            params = []
            
            # Add category filter if provided
            if category_id is not None:
                query += """
                    JOIN problem_math_categories pc ON p.problem_id = pc.problem_id
                    WHERE pc.category_id = ?
                """
                params.append(category_id)
            
            # Add search filter if provided
            if search_term is not None:
                if category_id is not None:
                    query += " AND "
                else:
                    query += " WHERE "
                
                query += """
                    (p.content LIKE ? OR p.answer LIKE ? OR p.notes LIKE ?)
                """
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_pattern])
            
            # Add ordering, limit and offset
            query += " ORDER BY p.problem_id ASC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            # Execute query
            self.cur.execute(query, params)
            
            # Build result list
            problems = []
            for row in self.cur.fetchall():
                problem_id = row[0]
                problem = {
                    "problem_id": problem_id,
                    "content": row[1],
                    "answer": row[2],
                    "earmark": row[3],
                    "creation_date": row[4],
                    "last_modified": row[5],
                    "categories": []
                }
                
                # Get categories for this problem
                self.cur.execute("""
                    SELECT c.category_id, c.name
                    FROM math_categories c
                    JOIN problem_math_categories pc ON c.category_id = pc.category_id
                    WHERE pc.problem_id = ?
                """, (problem_id,))
                
                problem["categories"] = [
                    {"category_id": cat[0], "name": cat[1]}
                    for cat in self.cur.fetchall()
                ]

                # Get types for this problem
                self.cur.execute("""
                    SELECT t.type_id, t.name
                    FROM problem_types t
                    JOIN problem_problem_types ppt ON t.type_id = ppt.type_id
                    WHERE ppt.problem_id = ?
                """, (problem_id,))
                problem["types"] = [
                    {"type_id": t[0], "name": t[1]}
                    for t in self.cur.fetchall()
                ]
                
                problems.append(problem)
            
            return (True, problems)
            
        except Exception as e:
            return (False, str(e))
    
    def add_image_to_problem(self, problem_id, image_data, image_name, format=None, width=None, height=None):
        """
        Add an image to a problem
        
        Args:
            problem_id (int): ID of the problem
            image_data: PIL Image object or binary image data
            image_name (str): Name for the image reference in LaTeX
            format (str, optional): Image format
            width (int, optional): Image width
            height (int, optional): Image height
            
        Returns:
            tuple: (success, image_id or error_message)
        """
        try:
            # Convert PIL Image to binary if needed
            if hasattr(image_data, 'save'):
                # It's a PIL Image
                img_bytes = io.BytesIO()
                image_format = format or image_data.format or 'PNG'
                image_data.save(img_bytes, format=image_format)
                binary_data = img_bytes.getvalue()
                
                # Get dimensions if not provided
                if width is None or height is None:
                    width, height = image_data.size
            else:
                # Assume it's already binary data
                binary_data = image_data
                
                # Try to get dimensions from binary data if not provided
                if (width is None or height is None) and format is not None:
                    try:
                        img = Image.open(io.BytesIO(binary_data))
                        width, height = img.size
                    except:
                        pass
            
            # Check if problem exists
            self.cur.execute("SELECT problem_id FROM problems WHERE problem_id = ?", (problem_id,))
            if not self.cur.fetchone():
                return (False, f"Problem with ID {problem_id} not found")
            
            # Insert image
            self.cur.execute('''
                INSERT INTO problem_images 
                (problem_id, image_data, image_name, format, width, height)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (problem_id, binary_data, image_name, format, width, height))
            
            image_id = self.cur.lastrowid
            self.conn.commit()
            
            return (True, image_id)
            
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))
    
    def get_image(self, image_id=None, image_name=None, problem_id=None):
        """
        Get an image from the database
        
        Args:
            image_id (int, optional): ID of the image to retrieve
            image_name (str, optional): Name of the image to retrieve
            problem_id (int, optional): If provided with image_name, restricts search to this problem
            
        Returns:
            tuple: (success, image_data or error_message)
        """
        try:
            # Build query based on provided parameters
            if image_id is not None:
                query = "SELECT image_data, image_name, format, width, height FROM problem_images WHERE image_id = ?"
                params = (image_id,)
            elif image_name is not None:
                if problem_id is not None:
                    query = """
                        SELECT image_data, image_name, format, width, height 
                        FROM problem_images 
                        WHERE image_name = ? AND problem_id = ?
                    """
                    params = (image_name, problem_id)
                else:
                    query = "SELECT image_data, image_name, format, width, height FROM problem_images WHERE image_name = ?"
                    params = (image_name,)
            else:
                return (False, "Either image_id or image_name must be provided")
            
            # Execute query
            self.cur.execute(query, params)
            result = self.cur.fetchone()
            
            if not result:
                return (False, "Image not found")
            
            # Convert binary data to PIL Image
            img_data, name, format, width, height = result
            image = Image.open(io.BytesIO(img_data))
            
            # Store original format and dimensions
            if format and not image.format:
                image.format = format
            
            return (True, {
                "image": image,
                "name": name,
                "format": format,
                "width": width,
                "height": height
            })
            
        except Exception as e:
            return (False, str(e))
    
    def export_image(self, image_id=None, image_name=None, problem_id=None, output_path=None):
        """
        Export an image from the database to a file
        
        Args:
            image_id (int, optional): ID of the image to export
            image_name (str, optional): Name of the image to export
            problem_id (int, optional): If provided with image_name, restricts search to this problem
            output_path (str): Path to save the image
            
        Returns:
            tuple: (success, file_path or error_message)
        """
        try:
            print(f"[DEBUG] Attempting to get image: {image_name}")
            success, result = self.get_image(image_id, image_name, problem_id)
            print(f"[DEBUG] get_image success: {success}, result: {result}")
            if not success:
                return (False, result)
            image = result["image"]
            format = result["format"]
            # If no output path provided, create one in temp_images directory
            if not output_path:
                temp_dir = Path("temp_images")
                temp_dir.mkdir(parents=True, exist_ok=True)
                # Use image name or create one from ID
                filename = result["name"] or f"image_{image_id}.{format.lower() if format else 'png'}"
                output_path = temp_dir / filename
            # Ensure parent directory exists
            output_dir = os.path.dirname(output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            print(f"[DEBUG] Saving image {image_name} to {output_path}")
            # Save image to file
            format_to_use = format or image.format or 'PNG'
            
            # If it's DIB/BMP format but the output path expects PNG, convert it
            if format_to_use in ['DIB', 'BMP'] and str(output_path).endswith('.png'):
                format_to_use = 'PNG'
                print(f"[DEBUG] Converting DIB/BMP to PNG for {output_path}")
            
            image.save(output_path, format=format_to_use)
            return (True, str(output_path))
            
        except Exception as e:
            return (False, str(e))
    
    def add_category(self, name):
        """
        Add a new math category
        
        Args:
            name (str): Category name
            
        Returns:
            tuple: (success, category_id or error_message)
        """
        try:
            # Check if category already exists
            self.cur.execute("SELECT category_id FROM math_categories WHERE name = ?", (name,))
            existing = self.cur.fetchone()
            
            if existing:
                return (True, existing[0])  # Return existing ID if found
            
            # Insert new category
            self.cur.execute("INSERT INTO math_categories (name) VALUES (?)", (name,))
            
            category_id = self.cur.lastrowid
            self.conn.commit()
            
            return (True, category_id)
            
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))
    
    def update_category(self, category_id, name):
        """
        Update a math category
        
        Args:
            category_id (int): ID of the category to update
            name (str): New category name
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Check if category exists
            self.cur.execute("SELECT category_id FROM math_categories WHERE category_id = ?", (category_id,))
            if not self.cur.fetchone():
                return (False, f"Category with ID {category_id} not found")
            
            # Update category
            self.cur.execute("UPDATE math_categories SET name = ? WHERE category_id = ?", (name, category_id))
            
            self.conn.commit()
            return (True, f"Category with ID {category_id} updated successfully")
            
        except sqlite3.IntegrityError:
            self.conn.rollback()
            return (False, f"Category name '{name}' already exists")
            
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))
    
    def delete_category(self, category_id):
        """
        Delete a math category
        
        Args:
            category_id (int): ID of the category to delete
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Check if category exists
            self.cur.execute("SELECT category_id FROM math_categories WHERE category_id = ?", (category_id,))
            if not self.cur.fetchone():
                return (False, f"Category with ID {category_id} not found")
            
            # Delete the category
            self.cur.execute("DELETE FROM math_categories WHERE category_id = ?", (category_id,))
            
            self.conn.commit()
            return (True, f"Category with ID {category_id} deleted successfully")
            
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))
    
    def get_categories(self):
        """
        Get all math categories
        
        Returns:
            tuple: (success, list_of_categories or error_message)
        """
        try:
            self.cur.execute("SELECT category_id, name FROM math_categories ORDER BY name")
            
            categories = []
            for row in self.cur.fetchall():
                categories.append({
                    "category_id": row[0],
                    "name": row[1]
                })
            
            return (True, categories)
            
        except Exception as e:
            return (False, str(e))
    
    def add_problem_to_category(self, problem_id, category_name):
        """
        Add a problem to a category (creating the category if it doesn't exist)
        
        Args:
            problem_id (int): ID of the problem
            category_name (str): Name of the category
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Add or get the category
            success, result = self.add_category(category_name)
            
            if not success:
                return (False, result)
            
            category_id = result
            
            # Check if problem exists
            self.cur.execute("SELECT problem_id FROM problems WHERE problem_id = ?", (problem_id,))
            if not self.cur.fetchone():
                return (False, f"Problem with ID {problem_id} not found")
            
            # Check if relationship already exists
            self.cur.execute("""
                SELECT 1 FROM problem_math_categories 
                WHERE problem_id = ? AND category_id = ?
            """, (problem_id, category_id))
            
            if self.cur.fetchone():
                return (True, f"Problem already in category '{category_name}'")
            
            # Add the relationship
            self.cur.execute("""
                INSERT INTO problem_math_categories (problem_id, category_id)
                VALUES (?, ?)
            """, (problem_id, category_id))
            
            self.conn.commit()
            return (True, f"Problem added to category '{category_name}'")
            
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))
    
    def remove_problem_from_category(self, problem_id, category_id):
        """
        Remove a problem from a category
        
        Args:
            problem_id (int): ID of the problem
            category_id (int): ID of the category
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Check if the relationship exists
            self.cur.execute("""
                SELECT 1 FROM problem_math_categories 
                WHERE problem_id = ? AND category_id = ?
            """, (problem_id, category_id))
            
            if not self.cur.fetchone():
                return (False, "Problem is not in this category")
            
            # Remove the relationship
            self.cur.execute("""
                DELETE FROM problem_math_categories
                WHERE problem_id = ? AND category_id = ?
            """, (problem_id, category_id))
            
            self.conn.commit()
            return (True, "Problem removed from category")
            
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))
    
    def export_images_for_problem(self, problem_id, output_dir):
        """
        Export all images associated with a problem to a directory
        
        Args:
            problem_id (int): ID of the problem
            output_dir (str): Directory to save the images
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Always use temp_images as the output directory
            output_path = Path("temp_images")
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Get all images for the problem
            self.cur.execute("""
                SELECT image_id, image_name, format 
                FROM problem_images 
                WHERE problem_id = ?
            """, (problem_id,))
            
            images = self.cur.fetchall()
            
            if not images:
                return (True, "No images found for this problem")
            
            # Export each image
            exported_count = 0
            failed_count = 0
            
            for image_id, image_name, format in images:
                output_file = output_path / image_name
                success, result = self.export_image(image_id=image_id, output_path=str(output_file))
                
                if success:
                    exported_count += 1
                else:
                    failed_count += 1
                    print(f"Failed to export image {image_id}: {result}")
            
            message = f"Exported {exported_count} images to temp_images"
            if failed_count > 0:
                message += f" ({failed_count} failed)"
                
            return (True, message)
            
        except Exception as e:
            return (False, str(e))
    
    def get_problem_count(self, category_id=None):
        """
        Get the count of problems, optionally filtered by category
        
        Args:
            category_id (int, optional): Filter by category ID
            
        Returns:
            tuple: (success, count or error_message)
        """
        try:
            if category_id is not None:
                query = """
                    SELECT COUNT(DISTINCT p.problem_id) 
                    FROM problems p
                    JOIN problem_math_categories pc ON p.problem_id = pc.problem_id
                    WHERE pc.category_id = ?
                """
                self.cur.execute(query, (category_id,))
            else:
                query = "SELECT COUNT(*) FROM problems"
                self.cur.execute(query)
                
            count = self.cur.fetchone()[0]
            return (True, count)
            
        except Exception as e:
            return (False, str(e))
    
    def close(self):
        """Close the database connection"""
        if hasattr(self, 'conn') and self.conn:
            self.conn.close()

    def create_problem_set(self, name, description=None, is_ordered=0):
        """Create a new problem set."""
        try:
            self.cur.execute('''
                INSERT INTO problem_sets (name, description, is_ordered)
                VALUES (?, ?, ?)
            ''', (name, description, is_ordered))
            self.conn.commit()
            return (True, self.cur.lastrowid)
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def update_problem_set(self, set_id, name=None, description=None, is_ordered=None):
        """Update an existing problem set."""
        try:
            columns = []
            values = []
            if name is not None:
                columns.append("name = ?")
                values.append(name)
            if description is not None:
                columns.append("description = ?")
                values.append(description)
            if is_ordered is not None:
                columns.append("is_ordered = ?")
                values.append(is_ordered)
            if not columns:
                return (True, "No changes to update")
            values.append(set_id)
            query = f"UPDATE problem_sets SET {', '.join(columns)} WHERE set_id = ?"
            self.cur.execute(query, values)
            self.conn.commit()
            return (True, "Problem set updated successfully")
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def delete_problem_set(self, set_id):
        """Delete a problem set and its members."""
        try:
            self.cur.execute("DELETE FROM problem_sets WHERE set_id = ?", (set_id,))
            self.conn.commit()
            return (True, f"Problem set {set_id} deleted")
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def list_problem_sets(self):
        """List all problem sets."""
        self.cur.execute("SELECT set_id, name, description, is_ordered FROM problem_sets ORDER BY name")
        return self.cur.fetchall()

    def add_problem_to_set(self, set_id, problem_id, order_index=None):
        """Add a problem to a set, optionally with order."""
        try:
            self.cur.execute('''
                INSERT OR REPLACE INTO problem_set_member (set_id, problem_id, order_index)
                VALUES (?, ?, ?)
            ''', (set_id, problem_id, order_index))
            self.conn.commit()
            return (True, "Problem added to set")
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def remove_problem_from_set(self, set_id, problem_id):
        """Remove a problem from a set."""
        try:
            self.cur.execute('''
                DELETE FROM problem_set_member WHERE set_id = ? AND problem_id = ?
            ''', (set_id, problem_id))
            self.conn.commit()
            return (True, "Problem removed from set")
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def list_problems_in_set(self, set_id, ordered=True):
        if ordered:
            print(f"-------------------ordered={ordered}")
            self.cur.execute('''
                SELECT p.problem_id, p.content, p.answer, p.earmark, p.creation_date, p.last_modified
                FROM problems p
                JOIN problem_set_member m ON p.problem_id = m.problem_id
                WHERE m.set_id = ?
                ORDER BY m.order_index ASC
            ''', (set_id,))
        else:
            self.cur.execute('''
                SELECT p.problem_id, p.content, p.answer, p.earmark, p.creation_date, p.last_modified
                FROM problems p
                JOIN problem_set_member m ON p.problem_id = m.problem_id
                WHERE m.set_id = ?
            ''', (set_id,))
        rows = self.cur.fetchall()
        print(f"----------rows={rows}")
        problems = []
        for row in rows:
            problem_id = row[0]
            problem = {
                "problem_id": problem_id,
                "content": row[1],
                "answer": row[2],
                "earmark": row[3],
                "creation_date": row[4],
                "last_modified": row[5],
                "categories": []
            }
            # Get categories for this problem
            self.cur.execute("""
                SELECT c.category_id, c.name
                FROM math_categories c
                JOIN problem_math_categories pc ON c.category_id = pc.category_id
                WHERE pc.problem_id = ?
            """, (problem_id,))
            problem["categories"] = [
                {"category_id": cat[0], "name": cat[1]}
                for cat in self.cur.fetchall()
            ]
            # Get types for this problem
            self.cur.execute("""
                SELECT t.type_id, t.name
                FROM problem_types t
                JOIN problem_problem_types ppt ON t.type_id = ppt.type_id
                WHERE ppt.problem_id = ?
            """, (problem_id,))
            problem["types"] = [
                {"type_id": t[0], "name": t[1]}
                for t in self.cur.fetchall()
            ]
            problems.append(problem)
        print(f"[DEBUG] Returning {len(problems)} problems from list_problems_in_set: {[p['problem_id'] for p in problems]}")
        return problems

    def add_type(self, name):
        """
        Add a new problem type
        Args:
            name (str): Type name
        Returns:
            tuple: (success, type_id or error_message)
        """
        try:
            self.cur.execute("SELECT type_id FROM problem_types WHERE name = ?", (name,))
            existing = self.cur.fetchone()
            if existing:
                return (True, existing[0])
            self.cur.execute("INSERT INTO problem_types (name) VALUES (?)", (name,))
            type_id = self.cur.lastrowid
            self.conn.commit()
            return (True, type_id)
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def add_problem_to_type(self, problem_id, type_name):
        """
        Add a problem to a type (creating the type if it doesn't exist)
        Args:
            problem_id (int): ID of the problem
            type_name (str): Name of the type
        Returns:
            tuple: (success, message)
        """
        try:
            success, result = self.add_type(type_name)
            if not success:
                return (False, result)
            type_id = result
            self.cur.execute("SELECT problem_id FROM problems WHERE problem_id = ?", (problem_id,))
            if not self.cur.fetchone():
                return (False, f"Problem with ID {problem_id} not found")
            self.cur.execute("SELECT 1 FROM problem_problem_types WHERE problem_id = ? AND type_id = ?", (problem_id, type_id))
            if self.cur.fetchone():
                return (True, f"Problem already in type '{type_name}'")
            self.cur.execute("INSERT INTO problem_problem_types (problem_id, type_id) VALUES (?, ?)", (problem_id, type_id))
            self.conn.commit()
            return (True, f"Problem added to type '{type_name}'")
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def remove_problem_from_type(self, problem_id, type_id):
        """
        Remove a problem from a type
        Args:
            problem_id (int): ID of the problem
            type_id (int): ID of the type
        Returns:
            tuple: (success, message)
        """
        try:
            self.cur.execute("SELECT 1 FROM problem_problem_types WHERE problem_id = ? AND type_id = ?", (problem_id, type_id))
            if not self.cur.fetchone():
                return (False, "Problem is not in this type")
            self.cur.execute("DELETE FROM problem_problem_types WHERE problem_id = ? AND type_id = ?", (problem_id, type_id))
            self.conn.commit()
            return (True, "Problem removed from type")
        except Exception as e:
            self.conn.rollback()
            return (False, str(e))

    def get_types_for_problem(self, problem_id):
        """
        Get all types for a problem
        Args:
            problem_id (int): ID of the problem
        Returns:
            tuple: (success, list_of_types or error_message)
        """
        try:
            self.cur.execute("""
                SELECT t.type_id, t.name FROM problem_types t
                JOIN problem_problem_types ppt ON t.type_id = ppt.type_id
                WHERE ppt.problem_id = ?
            """, (problem_id,))
            types = [{"type_id": row[0], "name": row[1]} for row in self.cur.fetchall()]
            return (True, types)
        except Exception as e:
            return (False, str(e))