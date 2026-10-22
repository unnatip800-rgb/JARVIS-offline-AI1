import sqlite3
from datetime import datetime


DATABASE = "jarvis_memory.db"


def get_connection():
    return sqlite3.connect(DATABASE)


def initialize_database():
    connection = get_connection()
    cursor = connection.cursor()

    # Stores individual messages
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)

    # Stores conversations/chats
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Stores long-term memories
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def create_conversation(session_id, title="New Chat"):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT OR IGNORE INTO conversations
        (session_id, title, created_at, updated_at)
        VALUES (?, ?, ?, ?)
    """, (session_id, title, now, now))

    connection.commit()
    connection.close()


def save_message(session_id, role, content):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO messages
        (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, content, now))

    cursor.execute("""
        UPDATE conversations
        SET updated_at = ?
        WHERE session_id = ?
    """, (now, session_id))

    connection.commit()
    connection.close()


def load_messages(session_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT role, content
        FROM messages
        WHERE session_id = ?
        ORDER BY id ASC
    """, (session_id,))

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "role": role,
            "content": content
        }
        for role, content in rows
    ]


def get_conversations():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT session_id, title, updated_at
        FROM conversations
        ORDER BY updated_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


def update_conversation_title(session_id, title):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        UPDATE conversations
        SET title = ?
        WHERE session_id = ?
    """, (title, session_id))

    connection.commit()
    connection.close()


def save_memory(memory):
    connection = get_connection()
    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO memories
        (memory, created_at)
        VALUES (?, ?)
    """, (memory, now))

    connection.commit()
    connection.close()


def get_memories():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT memory
        FROM memories
        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [row[0] for row in rows]


def delete_memory(memory_id):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM memories
        WHERE id = ?
    """, (memory_id,))

    connection.commit()
    connection.close()


# Create database/tables when this file is imported
initialize_database()