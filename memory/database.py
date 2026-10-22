import sqlite3
from datetime import datetime
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(exist_ok=True)

DATABASE = DATA_DIR / "jarvis.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(
        str(DATABASE)
    )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # --------------------------------------------------------
    # Conversations
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT UNIQUE NOT NULL,

            title TEXT NOT NULL,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # Messages
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            session_id TEXT NOT NULL,

            role TEXT NOT NULL,

            content TEXT NOT NULL,

            timestamp TEXT NOT NULL
        )
    """)

    # --------------------------------------------------------
    # Long-term memories
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            memory TEXT NOT NULL,

            created_at TEXT NOT NULL
        )
    """)

    connection.commit()

    connection.close()


# ============================================================
# CONVERSATIONS
# ============================================================

def create_conversation(
    session_id,
    title="New Chat"
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT OR IGNORE INTO conversations
        (
            session_id,
            title,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        session_id,
        title,
        now,
        now
    ))

    connection.commit()

    connection.close()


def get_conversations():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            session_id,
            title,
            updated_at

        FROM conversations

        ORDER BY updated_at DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


def update_conversation_title(
    session_id,
    title
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE conversations

        SET title = ?

        WHERE session_id = ?
    """, (
        title,
        session_id
    ))

    connection.commit()

    connection.close()


# ============================================================
# MESSAGES
# ============================================================

def save_message(
    session_id,
    role,
    content
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO messages
        (
            session_id,
            role,
            content,
            timestamp
        )
        VALUES (?, ?, ?, ?)
    """, (
        session_id,
        role,
        content,
        now
    ))

    cursor.execute("""
        UPDATE conversations

        SET updated_at = ?

        WHERE session_id = ?
    """, (
        now,
        session_id
    ))

    connection.commit()

    connection.close()


def load_messages(
    session_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            role,
            content

        FROM messages

        WHERE session_id = ?

        ORDER BY id ASC
    """, (
        session_id,
    ))

    rows = cursor.fetchall()

    connection.close()

    return [
        {
            "role": role,
            "content": content
        }

        for role, content in rows
    ]


# ============================================================
# LONG-TERM MEMORY
# ============================================================

def save_memory(
    memory
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    cursor.execute("""
        INSERT INTO memories
        (
            memory,
            created_at
        )
        VALUES (?, ?)
    """, (
        memory,
        now
    ))

    connection.commit()

    connection.close()


def get_memories():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            memory

        FROM memories

        ORDER BY id ASC
    """)

    rows = cursor.fetchall()

    connection.close()

    return [
        row[0]
        for row in rows
    ]


# ============================================================
# SMART MEMORY RETRIEVAL
# ============================================================

def get_relevant_memories(
    query,
    limit=5
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory,
            created_at

        FROM memories

        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    if not rows:

        return []

    # --------------------------------------------------------
    # Prepare query words
    # --------------------------------------------------------

    query_words = set(
        query.lower().split()
    )

    # --------------------------------------------------------
    # Common words that don't help relevance
    # --------------------------------------------------------

    stop_words = {
        "a",
        "an",
        "the",
        "is",
        "are",
        "am",
        "i",
        "me",
        "my",
        "you",
        "your",
        "what",
        "where",
        "when",
        "who",
        "how",
        "why",
        "do",
        "does",
        "did",
        "can",
        "could",
        "would",
        "should",
        "please",
        "tell",
        "about",
        "for",
        "to",
        "of",
        "in",
        "on",
        "and",
        "or",
        "with",
        "this",
        "that",
    }

    query_words -= stop_words

    scored_memories = []

    # --------------------------------------------------------
    # Score memories
    # --------------------------------------------------------

    for (
        memory_id,
        memory,
        created_at
    ) in rows:

        memory_words = set(
            memory.lower().split()
        )

        memory_words -= stop_words

        common_words = (
            query_words & memory_words
        )

        score = len(
            common_words
        )

        # Exact phrase bonus

        if query.lower() in memory.lower():

            score += 5

        if score > 0:

            scored_memories.append(
                (
                    score,
                    memory_id,
                    memory
                )
            )

    # --------------------------------------------------------
    # Sort by relevance
    # --------------------------------------------------------

    scored_memories.sort(
        key=lambda item: (
            item[0],
            item[1]
        ),
        reverse=True
    )

    # --------------------------------------------------------
    # Return memory text
    # --------------------------------------------------------

    return [
        memory

        for (
            score,
            memory_id,
            memory
        )

        in scored_memories[:limit]
    ]


# ============================================================
# MEMORY MANAGEMENT
# ============================================================

def get_memories_with_ids():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory,
            created_at

        FROM memories

        ORDER BY id DESC
    """)

    rows = cursor.fetchall()

    connection.close()

    return rows


def find_memory(
    search_text
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            memory

        FROM memories

        WHERE memory LIKE ?

        ORDER BY id DESC
    """, (
        f"%{search_text}%",
    ))

    rows = cursor.fetchall()

    connection.close()

    return rows


def delete_memory(
    memory_id
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM memories

        WHERE id = ?
    """, (
        memory_id,
    ))

    connection.commit()

    connection.close()


# ============================================================
# INITIALIZE DATABASE AUTOMATICALLY
# ============================================================

initialize_database()