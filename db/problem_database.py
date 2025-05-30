"""
Database access for math problems and images.
"""

import sqlite3
from pathlib import Path

class ProblemDatabase:
    def __init__(self, db_path=None):
        if db_path is None:
            db_path = Path(__file__).parent.parent / "db" / "math_problems.db"
        self.db_path = str(db_path)

    def get_all_categories(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT category_id, name FROM math_categories ORDER BY name ASC")
        categories = [{"category_id": row[0], "name": row[1]} for row in cur.fetchall()]
        conn.close()
        return categories

    # Removed delete_problem method. Use MathProblemDB.delete_problem instead. 