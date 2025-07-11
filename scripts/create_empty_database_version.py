#!/usr/bin/env python3
"""
Script to create an empty version of the math databases with the same structure.

Usage:
    python create_empty_database_version.py <version_name>
    
Example:
    python create_empty_database_version.py secondary
"""

import sys
import sqlite3
from pathlib import Path

# Add parent directory to path to import modules
sys.path.append(str(Path(__file__).parent.parent))

from db.db_config import DatabaseConfig
from db.math_db import MathProblemDB
from db.math_image_db import MathImageDB

def copy_table_structure(source_conn, dest_conn, table_name):
    """Copy table structure from source to destination database without data."""
    # Get CREATE statement for the table
    cursor = source_conn.cursor()
    cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    create_statement = cursor.fetchone()
    
    if create_statement:
        dest_conn.execute(create_statement[0])
        print(f"Created table: {table_name}")

def copy_index_structure(source_conn, dest_conn):
    """Copy all indexes from source to destination database."""
    cursor = source_conn.cursor()
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='index' AND sql IS NOT NULL")
    indexes = cursor.fetchall()
    
    for index in indexes:
        try:
            dest_conn.execute(index[0])
            print(f"Created index")
        except sqlite3.OperationalError as e:
            # Skip if index already exists
            if "already exists" not in str(e):
                raise

def create_empty_database_version(version_name):
    """Create an empty version of the databases with the same structure."""
    
    print(f"Creating empty database version: {version_name}")
    
    # Get paths for the new version
    db_config = DatabaseConfig(version_name)
    db_config.ensure_directories()
    new_problems_db, new_images_db = db_config.get_database_paths()
    
    # Get paths for the main database
    main_config = DatabaseConfig("main")
    main_problems_db, main_images_db = main_config.get_database_paths()
    
    # Check if main databases exist
    if not main_problems_db.exists():
        print(f"Error: Main problems database not found at {main_problems_db}")
        print("Please ensure the main database exists before creating a new version.")
        return False
        
    if not main_images_db.exists():
        print(f"Error: Main images database not found at {main_images_db}")
        print("Please ensure the main database exists before creating a new version.")
        return False
    
    # Copy problems database structure
    print(f"\nCopying structure from {main_problems_db} to {new_problems_db}")
    source_conn = sqlite3.connect(str(main_problems_db))
    dest_conn = sqlite3.connect(str(new_problems_db))
    
    # Enable foreign keys
    dest_conn.execute("PRAGMA foreign_keys = ON")
    
    # Get all table names
    cursor = source_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    for table in tables:
        copy_table_structure(source_conn, dest_conn, table[0])
    
    # Copy indexes
    copy_index_structure(source_conn, dest_conn)
    
    dest_conn.commit()
    source_conn.close()
    dest_conn.close()
    
    # Copy images database structure
    print(f"\nCopying structure from {main_images_db} to {new_images_db}")
    source_conn = sqlite3.connect(str(main_images_db))
    dest_conn = sqlite3.connect(str(new_images_db))
    
    # Get all table names
    cursor = source_conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    for table in tables:
        copy_table_structure(source_conn, dest_conn, table[0])
    
    # Copy indexes
    copy_index_structure(source_conn, dest_conn)
    
    dest_conn.commit()
    source_conn.close()
    dest_conn.close()
    
    print(f"\nSuccessfully created empty database version: {version_name}")
    print(f"Problems database: {new_problems_db}")
    print(f"Images database: {new_images_db}")
    
    return True

def main():
    if len(sys.argv) != 2:
        print("Usage: python create_empty_database_version.py <version_name>")
        print("Example: python create_empty_database_version.py secondary")
        sys.exit(1)
    
    version_name = sys.argv[1]
    
    # Validate version name
    if not version_name.replace("_", "").isalnum():
        print("Error: Version name must contain only alphanumeric characters and underscores")
        sys.exit(1)
    
    if version_name == "main":
        print("Error: Cannot overwrite main database")
        sys.exit(1)
    
    # Create the empty database version
    success = create_empty_database_version(version_name)
    
    if success:
        print(f"\nTo use this database version, run the application with:")
        print(f"python main_qt.py --db-version={version_name}")
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()