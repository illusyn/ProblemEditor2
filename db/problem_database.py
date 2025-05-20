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

    def get_all_problems(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT problem_id, content, answer, notes FROM problems")
        rows = cur.fetchall()
        for row in rows:
            if row["problem_id"] == 4:
                print("[DEBUG] Row for problem_id=4:", dict(row))
        problems = [dict(row) for row in rows]
        # Fetch categories for each problem
        for p in problems:
            cur.execute("""
                SELECT c.category_id, c.name FROM math_categories c
                JOIN problem_math_categories pc ON c.category_id = pc.category_id
                WHERE pc.problem_id = ?
            """, (p['problem_id'],))
            p['categories'] = [{"category_id": row[0], "name": row[1]} for row in cur.fetchall()]
            # Fetch SAT types for each problem
            cur.execute("""
                SELECT s.name FROM sat_problem_types s
                JOIN problem_sat_types ps ON s.type_id = ps.type_id
                WHERE ps.problem_id = ?
            """, (p['problem_id'],))
            p['sat_types'] = [row['name'] for row in cur.fetchall()]
        conn.close()
        # Rename keys for UI compatibility
        for p in problems:
            p['id'] = p.pop('problem_id')
        return problems

    def get_all_categories(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT category_id, name FROM math_categories ORDER BY name ASC")
        categories = [{"category_id": row[0], "name": row[1]} for row in cur.fetchall()]
        conn.close()
        return categories 