import sqlite3

class ProblemSetDB:
    def __init__(self, db_path='db/math_problems.db'):
        self.conn = sqlite3.connect(db_path)
        self.cur = self.conn.cursor()
        self._ensure_table()
        self._ensure_problem_types()

    def _ensure_table(self):
        # Drop existing tables if they exist to ensure clean schema
        self.cur.execute('DROP TABLE IF EXISTS problem_set_member')
        self.cur.execute('DROP TABLE IF EXISTS problem_sets')
        
        # Create problem_sets table
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problem_sets (
                set_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                is_ordered INTEGER DEFAULT 0
            )
        ''')
        
        # Create problem_set_member table
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problem_set_member (
                set_id INTEGER,
                problem_id INTEGER,
                order_index INTEGER,
                PRIMARY KEY (set_id, problem_id),
                FOREIGN KEY (set_id) REFERENCES problem_sets(set_id),
                FOREIGN KEY (problem_id) REFERENCES problems(problem_id)
            )
        ''')
        
        # Add some default sets if none exist
        self.cur.execute('SELECT COUNT(*) FROM problem_sets')
        if self.cur.fetchone()[0] == 0:
            default_sets = [
                ('Basic Problems', 'Basic math problems for beginners'),
                ('Advanced Problems', 'More challenging math problems'),
                ('Practice Set 1', 'First practice set'),
                ('Practice Set 2', 'Second practice set'),
                ('Review Problems', 'Problems for review')
            ]
            for name, desc in default_sets:
                self.cur.execute('INSERT INTO problem_sets (name, description) VALUES (?, ?)', (name, desc))
        
        self.conn.commit()

    def _ensure_problem_types(self):
        # Create problem_types table if it doesn't exist
        self.cur.execute('''
            CREATE TABLE IF NOT EXISTS problem_types (
                type_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        # Add default types if table is empty
        self.cur.execute('SELECT COUNT(*) FROM problem_types')
        if self.cur.fetchone()[0] == 0:
            default_types = [
                ('Intro',),
                ('Efficiency',),
                ('SAT-Problem',)
            ]
            self.cur.executemany('INSERT INTO problem_types (name) VALUES (?)', default_types)
            self.conn.commit()

    def get_all_sets(self):
        self.cur.execute('SELECT set_id, name, description, is_ordered FROM problem_sets ORDER BY name COLLATE NOCASE')
        return self.cur.fetchall()

    def add_set(self, name, description='', ordered=False):
        self.cur.execute('INSERT INTO problem_sets (name, description, is_ordered) VALUES (?, ?, ?)', (name, description, int(ordered)))
        self.conn.commit()
        return self.cur.lastrowid

    def rename_set(self, set_id, new_name):
        self.cur.execute('UPDATE problem_sets SET name=? WHERE set_id=?', (new_name, set_id))
        self.conn.commit()

    def delete_set(self, set_id):
        self.cur.execute('DELETE FROM problem_sets WHERE set_id=?', (set_id,))
        self.conn.commit()

    def update_set_details(self, set_id, name, description, ordered):
        self.cur.execute('UPDATE problem_sets SET name=?, description=?, is_ordered=? WHERE set_id=?', (name, description, int(ordered), set_id))
        self.conn.commit()

    def add_problem_to_set(self, set_id, problem_id, order_index=None):
        if order_index is None:
            self.cur.execute('SELECT MAX(order_index) FROM problem_set_member WHERE set_id=?', (set_id,))
            max_index = self.cur.fetchone()[0]
            order_index = (max_index + 1) if max_index is not None else 0
        try:
            self.cur.execute('INSERT INTO problem_set_member (set_id, problem_id, order_index) VALUES (?, ?, ?)', (set_id, problem_id, order_index))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Already in set

    def remove_problem_from_set(self, set_id, problem_id):
        self.cur.execute('DELETE FROM problem_set_member WHERE set_id=? AND problem_id=?', (set_id, problem_id))
        self.conn.commit()

    def get_problems_in_set(self, set_id):
        self.cur.execute('SELECT problem_id, order_index FROM problem_set_member WHERE set_id=? ORDER BY order_index', (set_id,))
        return self.cur.fetchall()

    def close(self):
        self.conn.close() 