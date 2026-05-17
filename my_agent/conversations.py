"""SQLite-based conversation storage for the AI agent."""

import sqlite3
import json
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path(__file__).parent / "conversations.db"


def _connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def _init_db():
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                title TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
            CREATE INDEX IF NOT EXISTS idx_msg_conv ON messages(conversation_id, id);
        """)


_init_db()


def list_conversations(limit=50):
    rows = []
    with _connect() as conn:
        cur = conn.execute(
            "SELECT id, title, created_at, updated_at FROM conversations "
            "ORDER BY updated_at DESC LIMIT ?",
            (limit,),
        )
        for r in cur:
            rows.append(dict(r))
    return rows


def get_conversation(conv_id):
    with _connect() as conn:
        row = conn.execute(
            "SELECT id, title, created_at, updated_at FROM conversations WHERE id=?",
            (conv_id,),
        ).fetchone()
        if not row:
            return None
        conv = dict(row)
        msgs = conn.execute(
            "SELECT role, content FROM messages WHERE conversation_id=? ORDER BY id",
            (conv_id,),
        ).fetchall()
        conv["messages"] = [dict(m) for m in msgs]
        return conv


def create_conversation(conv_id=None, title=""):
    conv_id = conv_id or str(int(datetime.now(timezone.utc).timestamp() * 1000))
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        conn.execute(
            "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?,?,?,?)",
            (conv_id, title or "新对话", now, now),
        )
    return conv_id


def save_message(conv_id, role, content):
    now = datetime.now(timezone.utc).isoformat()
    with _connect() as conn:
        exists = conn.execute(
            "SELECT COUNT(*) FROM conversations WHERE id=?", (conv_id,)
        ).fetchone()[0]
        if not exists:
            conn.execute(
                "INSERT INTO conversations (id, title, created_at, updated_at) VALUES (?,?,?,?)",
                (conv_id, "新对话", now, now),
            )
        else:
            conn.execute(
                "UPDATE conversations SET updated_at=? WHERE id=?", (now, conv_id)
            )
        conn.execute(
            "INSERT INTO messages (conversation_id, role, content, created_at) VALUES (?,?,?,?)",
            (conv_id, role, content, now),
        )
        # Auto-update title from first user message
        conn.execute(
            "UPDATE conversations SET title = ("
            "  SELECT substr(content,1,30) || CASE WHEN length(content)>30 THEN '...' ELSE '' END "
            "  FROM messages WHERE conversation_id=? AND role='user' ORDER BY id LIMIT 1"
            ") WHERE id=? AND title='新对话'",
            (conv_id, conv_id),
        )


def get_history(conv_id):
    """Return messages as list of (role, content) tuples for LangGraph."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE conversation_id=? ORDER BY id",
            (conv_id,),
        ).fetchall()
        return [(r["role"], r["content"]) for r in rows]


def delete_conversation(conv_id):
    with _connect() as conn:
        conn.execute("DELETE FROM messages WHERE conversation_id=?", (conv_id,))
        conn.execute("DELETE FROM conversations WHERE id=?", (conv_id,))
