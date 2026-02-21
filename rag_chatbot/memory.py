# memory.py  —  Session persistence via SQLite
# ─────────────────────────────────────────────────────
# PRODUCTION CHANGE: replaced in-memory dict with SQLite.
# Sessions now survive server restarts, deployments, and crashes.
# Uses Python's built-in sqlite3 — zero new dependencies.
# ─────────────────────────────────────────────────────

import sqlite3
import logging
from contextlib import contextmanager
from datetime import datetime

from config import DB_PATH, MEMORY_WINDOW

logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════
# Database initialisation
# ══════════════════════════════════════════════════════

def _get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")   # concurrent reads + writes
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


@contextmanager
def _db():
    conn = _get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create tables if they don't exist. Called once on app startup."""
    with _db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id  TEXT PRIMARY KEY,
                title       TEXT,
                created_at  TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS messages (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id  TEXT NOT NULL REFERENCES sessions(session_id) ON DELETE CASCADE,
                role        TEXT NOT NULL,
                content     TEXT NOT NULL,
                timestamp   TEXT NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_messages_session
                ON messages(session_id);
        """)
    logger.info("[DB] SQLite initialised at %s", DB_PATH)


# ══════════════════════════════════════════════════════
# Public API  (same signatures as the old in-memory version)
# ══════════════════════════════════════════════════════

def register_session(session_id: str) -> None:
    """Register a new empty session (called when user clicks New Chat)."""
    with _db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO sessions (session_id, title, created_at) VALUES (?, ?, ?)",
            (session_id, None, datetime.utcnow().isoformat()),
        )


def add_message(session_id: str, role: str, content: str) -> None:
    """Append a message and update the session title from the first user message."""
    with _db() as conn:
        # Ensure the session row exists
        conn.execute(
            "INSERT OR IGNORE INTO sessions (session_id, title, created_at) VALUES (?, ?, ?)",
            (session_id, None, datetime.utcnow().isoformat()),
        )
        # Set title from the first user message
        if role == "user":
            conn.execute(
                "UPDATE sessions SET title = ? WHERE session_id = ? AND title IS NULL",
                (content[:80], session_id),
            )
        conn.execute(
            "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.utcnow().isoformat()),
        )


def get_history(session_id: str) -> list[dict]:
    """Return the full conversation history for a session."""
    with _db() as conn:
        rows = conn.execute(
            "SELECT role, content, timestamp FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()
    return [dict(r) for r in rows]


def get_recent(session_id: str) -> list[dict]:
    """
    Return the last MEMORY_WINDOW user+assistant pairs for LLM context.
    """
    history = get_history(session_id)
    pairs: list[dict] = []
    i = len(history) - 1
    while i >= 1 and len(pairs) < MEMORY_WINDOW * 2:
        if history[i]["role"] == "assistant" and history[i - 1]["role"] == "user":
            pairs = [history[i - 1], history[i]] + pairs
            i -= 2
        else:
            i -= 1
    return pairs


def delete_session(session_id: str) -> None:
    """Remove a session and all its messages (CASCADE handles messages)."""
    with _db() as conn:
        conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))


def get_all_sessions() -> list[dict]:
    """Return all sessions sorted newest-first for the sidebar."""
    with _db() as conn:
        rows = conn.execute("""
            SELECT s.session_id,
                   COALESCE(s.title, 'New Chat') AS title,
                   s.created_at,
                   COUNT(m.id) AS message_count
            FROM sessions s
            LEFT JOIN messages m ON m.session_id = s.session_id
            GROUP BY s.session_id
            ORDER BY s.created_at DESC
        """).fetchall()
    return [dict(r) for r in rows]
