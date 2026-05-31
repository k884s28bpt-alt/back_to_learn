# Import get_db_connection from database.py
# We need this in every function to talk to the database
from database import get_db_connection

# Import Python's built-in hashing library
# We use this to hash passwords before saving them
import hashlib

# US1 — Hash password function
# Takes a real password and returns a hashed version
# We NEVER save the real password — only the hash
# SHA-256 is a one way algorithm — cannot be reversed
def hash_password(password):
    # Step 1 — encode() converts text to bytes (SHA-256 needs bytes not text)
    # Step 2 — sha256() runs the hashing algorithm
    # Step 3 — hexdigest() converts result to readable string of letters and numbers
    return hashlib.sha256(password.encode()).hexdigest()
# US1 — Student Registration with Grade Placement
# This function validates and saves a new user to the database
def register_user(username, password, last_grade):
    # Check if username and password are not empty
    if not username or not password:
        return False, "Username and password are required"
    # Check if username is at least 3 characters (US1 acceptance criteria)
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    # Check if grade is a number and not letters (US1 acceptance criteria)
    if not str(last_grade).isdigit():
        return False, "Grade must be a number"
    # Check if grade is between 1 and 12 (US1 acceptance criteria)
    # 0 or 13 or anything outside range is rejected
    if int(last_grade) < 1 or int(last_grade) > 12:
        return False, "Grade must be between 1 and 12"
    # Hash the password using SHA-256 before saving
    # We never save the real password — only the hashed version
    hashed = hash_password(password)
    # Connect to database and save the new user
    conn = get_db_connection()
    try:
        conn.execute(
             # Insert new user into users table
            # username is UNIQUE so duplicate usernames are rejected automatically
            'INSERT INTO users (username, password, last_grade) VALUES (?, ?, ?)',
            (username.strip(), hashed, int(last_grade))
        )
        conn.commit()# save the changes
        return True, "Success"
    except:
        # If username already exists database throws an error
        # We catch it and return a friendly message (US1 acceptance criteria)
        return False, "Username already exists"
    finally:
        conn.close() #always close the connection 

def login_user(username, password):
    if not username or not password:
        return None
    hashed = hash_password(password)
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE username = ? AND password = ?',
        (username.strip(), hashed)
    ).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute(
        'SELECT * FROM users WHERE id = ?', (user_id,)
    ).fetchone()
    conn.close()
    return user

def get_user_topics(user_id):
    conn = get_db_connection()
    topics = conn.execute(
        'SELECT * FROM topics WHERE user_id = ? ORDER BY grade_level, subject',
        (user_id,)
    ).fetchall()
    conn.close()
    return topics

def add_topic(user_id, subject, topic_name, grade_level):
    if not subject or not topic_name:
        return False
    if not str(grade_level).isdigit():
        return False
    if int(grade_level) < 1 or int(grade_level) > 12:
        return False
    conn = get_db_connection()
    conn.execute(
        'INSERT INTO topics (user_id, subject, topic_name, grade_level) VALUES (?, ?, ?, ?)',
        (user_id, subject.strip(), topic_name.strip(), int(grade_level))
    )
    conn.commit()
    conn.close()
    return True

def update_topic_status(topic_id, user_id, new_status):
    allowed = ['not_started', 'in_progress', 'done']
    if new_status not in allowed:
        return False
    conn = get_db_connection()
    conn.execute(
        'UPDATE topics SET status = ? WHERE id = ? AND user_id = ?',
        (new_status, topic_id, user_id)
    )
    conn.commit()
    conn.close()
    return True

def delete_topic(topic_id, user_id):
    conn = get_db_connection()
    conn.execute(
        'DELETE FROM topics WHERE id = ? AND user_id = ?',
        (topic_id, user_id)
    )
    conn.commit()
    conn.close()
    return True
