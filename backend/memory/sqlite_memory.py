import os
import sqlite3
from datetime import datetime

# Calculate absolute path relative to this file
current_dir = os.path.dirname(os.path.abspath(__file__))
# Navigate up one level to backend, then into data
DB_DIR = os.path.join(current_dir, "../../data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "chat_memory.db")


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user TEXT,
        role TEXT,
        message TEXT,
        created_at TEXT
    )
    """)

    conn.commit()
    conn.close()


def add_message(user, role, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO chat_history (user, role, message, created_at)
    VALUES (?, ?, ?, ?)
    """, (user, role, content, datetime.utcnow().isoformat()))

    conn.commit()
    conn.close()


def get_conversation(user, limit=6):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, message
    FROM chat_history
    WHERE user = ?
    ORDER BY id DESC
    LIMIT ?
    """, (user, limit))

    rows = cursor.fetchall()
    conn.close()

    # Reverse so oldest → newest
    rows.reverse()

    history = []

    for role, message in rows:
        history.append({
            "role": role,
            "content": message
        })

    return history

def get_recent_conversation(user, limit=4):
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    SELECT role, message
    FROM chat_history
    WHERE user = ?
    ORDER BY id DESC
    LIMIT ?
    """, (user, limit))

    rows = cursor.fetchall()
    conn.close()

    rows.reverse()

    history = []

    for role, message in rows:
        history.append({
            "role": role,
            "content": message
        })

    return history


def clear_conversation(user):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    DELETE FROM chat_history WHERE user = ?
    """, (user,))

    conn.commit()
    conn.close()