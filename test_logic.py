import unittest
import sqlite3
from logic import (
    hash_password,
    register_user,
    login_user,
    add_topic,
    update_topic_status,
    delete_topic,
    get_user_topics
)

import database

def get_test_db():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            last_grade INTEGER NOT NULL
        )
    ''')
    conn.execute('''
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
    return conn

database.get_db_connection = get_test_db


class TestHashPassword(unittest.TestCase):

    def test_returns_string(self):
        result = hash_password("hello")
        self.assertIsInstance(result, str)

    def test_same_password_same_hash(self):
        self.assertEqual(hash_password("abc123"), hash_password("abc123"))

    def test_different_passwords_different_hash(self):
        self.assertNotEqual(hash_password("abc123"), hash_password("xyz789"))

    def test_hash_length(self):
        self.assertEqual(len(hash_password("any_password")), 64)


class TestRegisterUser(unittest.TestCase):

    def test_valid_registration(self):
        success, msg = register_user("newuser1", "pass123", "7")
        self.assertTrue(success)

    def test_empty_username_fails(self):
        success, msg = register_user("", "pass123", "7")
        self.assertFalse(success)
        self.assertIn("required", msg.lower())

    def test_empty_password_fails(self):
        success, msg = register_user("farah1", "", "7")
        self.assertFalse(success)
        self.assertIn("required", msg.lower())

    def test_username_too_short_fails(self):
        success, msg = register_user("ab", "pass123", "7")
        self.assertFalse(success)
        self.assertIn("3 characters", msg)

    def test_grade_not_a_number_fails(self):
        success, msg = register_user("layla1", "pass123", "abc")
        self.assertFalse(success)
        self.assertIn("number", msg.lower())

    def test_grade_below_1_fails(self):
        success, msg = register_user("layla2", "pass123", "0")
        self.assertFalse(success)
        self.assertIn("between 1 and 12", msg)

    def test_grade_above_12_fails(self):
        success, msg = register_user("layla3", "pass123", "13")
        self.assertFalse(success)
        self.assertIn("between 1 and 12", msg)

    def test_duplicate_username_fails(self):
        register_user("maria1", "pass123", "5")
        success, msg = register_user("maria1", "pass456", "6")
        self.assertFalse(success)
        self.assertIn("already exists", msg.lower())


class TestLoginUser(unittest.TestCase):

    def setUp(self):
        register_user("nadiatest1", "mypassword", "9")

    def test_correct_credentials_returns_user(self):
        user = login_user("nadiatest1", "mypassword")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "nadiatest1")

    def test_wrong_password_returns_none(self):
        user = login_user("nadiatest1", "wrongpass")
        self.assertIsNone(user)

    def test_wrong_username_returns_none(self):
        user = login_user("nobody", "mypassword")
        self.assertIsNone(user)

    def test_empty_credentials_returns_none(self):
        user = login_user("", "")
        self.assertIsNone(user)


class TestAddTopic(unittest.TestCase):

    def test_valid_topic_returns_true(self):
        result = add_topic(1, "Mathematics", "Fractions", "6")
        self.assertTrue(result)

    def test_empty_subject_returns_false(self):
        result = add_topic(1, "", "Fractions", "6")
        self.assertFalse(result)

    def test_empty_topic_name_returns_false(self):
        result = add_topic(1, "Mathematics", "", "6")
        self.assertFalse(result)

    def test_invalid_grade_string_returns_false(self):
        result = add_topic(1, "Science", "Cells", "abc")
        self.assertFalse(result)

    def test_grade_below_1_returns_false(self):
        result = add_topic(1, "Science", "Cells", "0")
        self.assertFalse(result)

    def test_grade_above_12_returns_false(self):
        result = add_topic(1, "Science", "Cells", "15")
        self.assertFalse(result)


class TestUpdateTopicStatus(unittest.TestCase):

    def test_valid_status_not_started(self):
        result = update_topic_status(1, 1, "not_started")
        self.assertTrue(result)

    def test_valid_status_in_progress(self):
        result = update_topic_status(1, 1, "in_progress")
        self.assertTrue(result)

    def test_valid_status_done(self):
        result = update_topic_status(1, 1, "done")
        self.assertTrue(result)

    def test_invalid_status_returns_false(self):
        result = update_topic_status(1, 1, "finished")
        self.assertFalse(result)

    def test_empty_status_returns_false(self):
        result = update_topic_status(1, 1, "")
        self.assertFalse(result)


class TestGetUserTopics(unittest.TestCase):

    def test_returns_only_own_topics(self):
        add_topic(991, "History", "World War II", "11")
        add_topic(992, "Biology", "Photosynthesis", "10")
        user_991_topics = get_user_topics(991)
        for topic in user_991_topics:
            self.assertEqual(topic["user_id"], 991)

    def test_empty_for_user_with_no_topics(self):
        topics = get_user_topics(9999)
        self.assertEqual(len(topics), 0)


class TestDeleteTopic(unittest.TestCase):

    def test_delete_returns_true(self):
        add_topic(501, "Physics", "Newton Laws", "11")
        topics = get_user_topics(501)
        topic_id = topics[0]["id"]
        result = delete_topic(topic_id, 501)
        self.assertTrue(result)

    def test_topic_removed_after_delete(self):
        add_topic(502, "Chemistry", "Atoms", "10")
        topics = get_user_topics(502)
        topic_id = topics[0]["id"]
        delete_topic(topic_id, 502)
        remaining = get_user_topics(502)
        self.assertEqual(len(remaining), 0)

    def test_cannot_delete_other_users_topic(self):
        add_topic(503, "Math", "Algebra", "9")
        topics = get_user_topics(503)
        topic_id = topics[0]["id"]
        delete_topic(topic_id, 504)
        remaining = get_user_topics(503)
        self.assertEqual(len(remaining), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)