from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import get_connection, init_db

app = FastAPI(title="Task Tracker API")

# CORS: browsers block a page from calling an API on a different address
# unless the API says it's allowed. This lets the Vite dev server call us.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type"],
)

# Make sure the tasks table exists when the server starts.
init_db()


class TaskCreate(BaseModel):
    """The JSON body the client must send when creating a task."""

    title: str = Field(min_length=1, max_length=200)


class TaskUpdate(BaseModel):
    """The JSON body the client sends to mark a task complete or active."""

    completed: bool


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


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET completed = ? WHERE id = ?",
            (int(update.completed), task_id),
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
        row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    return row_to_task(row)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    with get_connection() as conn:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)
