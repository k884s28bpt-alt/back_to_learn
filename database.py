# Import Python's built-in database library
# No installation needed — comes with Python automatically
# Used to create and manage the database.db file
import sqlite3

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row  # lets you access columns by name
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            last_grade INTEGER NOT NULL
        )
    ''')

    # Topics table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            subject TEXT NOT NULL,
            topic_name TEXT NOT NULL,
            grade_level INTEGER NOT NULL,
            status TEXT DEFAULT 'not_started',
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()
