import os

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from database import fetch_all, fetch_one, init_db

app = FastAPI(title="Task Tracker API")

# CORS: browsers block a page from calling an API on a different address
# unless the API says it's allowed. The Vite dev server is always allowed;
# on Render, FRONTEND_URL adds the deployed frontend's address.
allowed_origins = ["http://localhost:5173"]
if os.environ.get("FRONTEND_URL"):
    allowed_origins.append(os.environ["FRONTEND_URL"].rstrip("/"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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


def row_to_task(row: dict) -> dict:
    """Turn a database row into the JSON shape the frontend will receive."""
    return {
        "id": row["id"],
        "title": row["title"],
        "completed": bool(row["completed"]),  # SQLite stores 0/1 -> false/true
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/tasks")
def list_tasks():
    rows = fetch_all("SELECT * FROM tasks ORDER BY id")
    return [row_to_task(r) for r in rows]


# "RETURNING *" makes the database hand back the row it just wrote, so we
# don't need a second query. Both SQLite and Postgres support it.
@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    row = fetch_one("INSERT INTO tasks (title) VALUES (?) RETURNING *", (task.title,))
    return row_to_task(row)


@app.patch("/tasks/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    row = fetch_one(
        "UPDATE tasks SET completed = ? WHERE id = ? RETURNING *",
        (update.completed, task_id),
    )
    if row is None:  # no row matched that id
        raise HTTPException(status_code=404, detail="Task not found")
    return row_to_task(row)


@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    row = fetch_one("DELETE FROM tasks WHERE id = ? RETURNING id", (task_id,))
    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)
