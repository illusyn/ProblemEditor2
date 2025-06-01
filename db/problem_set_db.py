import sqlite3

class ProblemSetDB:
    def __init__(self, db_path='math_problems.db'):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self._ensure_table()

    def _ensure_table(self):
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problem_sets (
                set_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                ordered INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def get_all_sets(self):
        self.cur.execute('SELECT set_id, name, description, ordered FROM problem_sets ORDER BY name COLLATE NOCASE')
        return self.cur.fetchall()

    def add_set(self, name, description='', ordered=False):
        self.cur.execute('INSERT INTO problem_sets (name, description, ordered) VALUES (?, ?, ?)', (name, description, int(ordered)))
        self.conn.commit()
        return self.cur.lastrowid

    def rename_set(self, set_id, new_name):
        self.cur.execute('UPDATE problem_sets SET name=? WHERE set_id=?', (new_name, set_id))
        self.conn.commit()

    def delete_set(self, set_id):
        self.cur.execute('DELETE FROM problem_sets WHERE set_id=?', (set_id,))
        self.conn.commit()

    def update_set_details(self, set_id, name, description, ordered):
        self.cur.execute('UPDATE problem_sets SET name=?, description=?, ordered=? WHERE set_id=?', (name, description, int(ordered), set_id))
        self.conn.commit()

    def add_problem_to_set(self, set_id, problem_id, position=None):
        if position is None:
            self.cur.execute('SELECT MAX(position) FROM problem_set_member WHERE set_id=?', (set_id,))
            max_pos = self.cur.fetchone()[0]
            position = (max_pos + 1) if max_pos is not None else 0
        try:
            self.cur.execute('INSERT INTO problem_set_member (set_id, problem_id, position) VALUES (?, ?, ?)', (set_id, problem_id, position))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Already in set

    def remove_problem_from_set(self, set_id, problem_id):
        self.cur.execute('DELETE FROM problem_set_member WHERE set_id=? AND problem_id=?', (set_id, problem_id))
        self.conn.commit()

    def get_problems_in_set(self, set_id):
        self.cur.execute('SELECT problem_id, position FROM problem_set_member WHERE set_id=? ORDER BY position', (set_id,))
        return self.cur.fetchall()

    def close(self):
        self.conn.close() 