import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

# The database is a single file that lives next to this script.
DB_PATH = Path(__file__).parent / "tasks.db"


@contextmanager
def get_connection() -> Iterator[sqlite3.Connection]:
    """Open a connection to the SQLite file (created automatically if missing).

    Use it as `with get_connection() as conn:`. When the block ends it saves
    the changes (or undoes them if an error happened) and always closes the
    connection, so the database file is never left locked.
    """
    conn = sqlite3.connect(DB_PATH)
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


def init_db() -> None:
    """Create the tasks table if it doesn't exist yet."""
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                title     TEXT    NOT NULL,
                completed INTEGER NOT NULL DEFAULT 0
            )
            """
        )
