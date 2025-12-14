"""SQLite-backed storage for conversations."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import DB_PATH


def _ensure_data_dir():
    """Ensure the directory for the SQLite file exists."""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


def _get_connection() -> sqlite3.Connection:
    """Get a SQLite connection with row factory and FK support."""
    _ensure_data_dir()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def _init_db():
    """Create tables if they do not exist."""
    with _get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                title TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT,
                stage1 TEXT,
                stage2 TEXT,
                stage3 TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
            );
            """
        )


_init_db()


def _serialize_assistant_payload(stage1, stage2, stage3):
    return (
        json.dumps(stage1),
        json.dumps(stage2),
        json.dumps(stage3),
    )


def _deserialize_message(row: sqlite3.Row) -> Dict[str, Any]:
    if row["role"] == "user":
        return {
            "role": "user",
            "content": row["content"],
        }

    return {
        "role": "assistant",
        "stage1": json.loads(row["stage1"]) if row["stage1"] else None,
        "stage2": json.loads(row["stage2"]) if row["stage2"] else None,
        "stage3": json.loads(row["stage3"]) if row["stage3"] else None,
    }


def create_conversation(conversation_id: str) -> Dict[str, Any]:
    """Create a new conversation record."""
    created_at = datetime.utcnow().isoformat()
    title = "New Conversation"
    with _get_connection() as conn:
        conn.execute(
            "INSERT INTO conversations (id, created_at, title) VALUES (?, ?, ?)",
            (conversation_id, created_at, title),
        )

    return {
        "id": conversation_id,
        "created_at": created_at,
        "title": title,
        "messages": [],
    }


def get_conversation(conversation_id: str) -> Optional[Dict[str, Any]]:
    """Load a conversation with its messages."""
    with _get_connection() as conn:
        convo = conn.execute(
            "SELECT id, created_at, title FROM conversations WHERE id = ?",
            (conversation_id,),
        ).fetchone()

        if convo is None:
            return None

        messages = conn.execute(
            """
            SELECT role, content, stage1, stage2, stage3
            FROM messages
            WHERE conversation_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (conversation_id,),
        ).fetchall()

    return {
        "id": convo["id"],
        "created_at": convo["created_at"],
        "title": convo["title"],
        "messages": [_deserialize_message(m) for m in messages],
    }


def list_conversations() -> List[Dict[str, Any]]:
    """List all conversations with metadata and message counts."""
    with _get_connection() as conn:
        rows = conn.execute(
            """
            SELECT
                c.id,
                c.created_at,
                c.title,
                COUNT(m.id) AS message_count
            FROM conversations c
            LEFT JOIN messages m ON m.conversation_id = c.id
            GROUP BY c.id
            ORDER BY c.created_at DESC
            """
        ).fetchall()

    return [
        {
            "id": row["id"],
            "created_at": row["created_at"],
            "title": row["title"],
            "message_count": row["message_count"],
        }
        for row in rows
    ]


def _ensure_conversation_exists(conversation_id: str):
    if get_conversation(conversation_id) is None:
        raise ValueError(f"Conversation {conversation_id} not found")


def add_user_message(conversation_id: str, content: str):
    """Persist a user message."""
    _ensure_conversation_exists(conversation_id)
    created_at = datetime.utcnow().isoformat()
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO messages (conversation_id, role, content, created_at)
            VALUES (?, 'user', ?, ?)
            """,
            (conversation_id, content, created_at),
        )


def add_assistant_message(
    conversation_id: str,
    stage1: List[Dict[str, Any]],
    stage2: List[Dict[str, Any]],
    stage3: Dict[str, Any],
):
    """Persist an assistant message with all stages."""
    _ensure_conversation_exists(conversation_id)
    created_at = datetime.utcnow().isoformat()
    s1, s2, s3 = _serialize_assistant_payload(stage1, stage2, stage3)
    with _get_connection() as conn:
        conn.execute(
            """
            INSERT INTO messages (conversation_id, role, stage1, stage2, stage3, created_at)
            VALUES (?, 'assistant', ?, ?, ?, ?)
            """,
            (conversation_id, s1, s2, s3, created_at),
        )


def update_conversation_title(conversation_id: str, title: str):
    """Update the stored title for a conversation."""
    _ensure_conversation_exists(conversation_id)
    with _get_connection() as conn:
        conn.execute(
            "UPDATE conversations SET title = ? WHERE id = ?",
            (title, conversation_id),
        )
