from fastapi import FastAPI
from pydantic import BaseModel, Field

from database import get_connection, init_db

app = FastAPI(title="Task Tracker API")

# Make sure the tasks table exists when the server starts.
init_db()


class TaskCreate(BaseModel):
    """The JSON body the client must send when creating a task."""

    title: str = Field(min_length=1, max_length=200)


def row_to_task(row) -> dict:
    """Turn a database row into the JSON shape the frontend will receive."""
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),  # 0/1 in SQLite -> false/true in JSON
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM tasks ORDER BY id").fetchall()
    return [row_to_task(r) for r in rows]


@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (title) VALUES (?)", (task.title,)
        )
        new_id = cursor.lastrowid
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
    return row_to_task(row)
