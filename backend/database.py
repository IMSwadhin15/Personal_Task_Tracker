import sqlite3
from pathlib import Path

# The database is a single file that lives next to this script.
DB_PATH = Path(__file__).parent / "tasks.db"


def get_connection() -> sqlite3.Connection:
    """Open a connection to the SQLite file (created automatically if missing)."""
    conn = sqlite3.connect(DB_PATH)
    # Let us read columns by name (row["title"]) instead of by position.
    conn.row_factory = sqlite3.Row
    return conn


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
