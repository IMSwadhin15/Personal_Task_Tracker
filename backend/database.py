"""Database access for the Task Tracker.

Two modes, picked automatically:
- If the DATABASE_URL environment variable is set (on Render, pointing to
  Neon), we use PostgreSQL.
- Otherwise we use a local SQLite file, tasks.db, next to this script.

The rest of the app only uses fetch_all() and fetch_one(), so it doesn't need
to know which database is behind them.
"""

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

DATABASE_URL = os.environ.get("DATABASE_URL")
USE_POSTGRES = bool(DATABASE_URL)

SQLITE_PATH = Path(__file__).parent / "tasks.db"


@contextmanager
def get_connection() -> Iterator[Any]:
    """Open a connection, then save (commit) or undo (rollback) and always close it."""
    if USE_POSTGRES:
        import psycopg  # only needed in Postgres mode
        from psycopg.rows import dict_row

        conn = psycopg.connect(DATABASE_URL, row_factory=dict_row)
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        # Let us read columns by name (row["title"]) instead of by position.
        conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def _run(sql: str, params: tuple) -> list[dict]:
    """Run one SQL statement and return every row it produced as a dict.

    Write queries with "?" placeholders; Postgres wants "%s", so we swap them.
    """
    if USE_POSTGRES:
        sql = sql.replace("?", "%s")
    with get_connection() as conn:
        cursor = conn.execute(sql, params)
        rows = cursor.fetchall() if cursor.description else []
    return [dict(row) for row in rows]


def fetch_all(sql: str, params: tuple = ()) -> list[dict]:
    return _run(sql, params)


def fetch_one(sql: str, params: tuple = ()) -> dict | None:
    """Return the first row, or None if the query produced no rows."""
    rows = _run(sql, params)
    return rows[0] if rows else None


def init_db() -> None:
    """Create the tasks table if it doesn't exist yet."""
    if USE_POSTGRES:
        sql = """
            CREATE TABLE IF NOT EXISTS tasks (
                id        SERIAL  PRIMARY KEY,
                title     TEXT    NOT NULL,
                completed BOOLEAN NOT NULL DEFAULT FALSE
            )
        """
    else:
        sql = """
            CREATE TABLE IF NOT EXISTS tasks (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT    NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
        """
    _run(sql, ())
