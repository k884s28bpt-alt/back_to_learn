
from database import get_db_connection
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password, last_grade):
    if not username or not password:
        return False, "Username and password are required"
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if not str(last_grade).isdigit():
        return False, "Grade must be a number"
    if int(last_grade) < 1 or int(last_grade) > 12:
        return False, "Grade must be between 1 and 12"
    hashed = hash_password(password)
    conn = get_db_connection()
    try:
        conn.execute(
            'INSERT INTO users (username, password, last_grade) VALUES (?, ?, ?)',
            (username.strip(), hashed, int(last_grade))
        )
        conn.commit()
        return True, "Success"
    except:
        return False, "Username already exists"
    finally:
        conn.close()

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
