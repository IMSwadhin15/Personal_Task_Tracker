# Personal Task Tracker

A small to-do app: add tasks, mark them complete, delete them.

**Live app:** <https://task-tracker-web-0kcx.onrender.com>
(API: <https://task-tracker-api-v4c3.onrender.com>, docs at
[`/docs`](https://task-tracker-api-v4c3.onrender.com/docs))

> The free backend sleeps after 15 minutes without visits, so the first load
> can take up to a minute.

- **Backend:** FastAPI (Python 3.11), in [`backend/`](backend)
- **Frontend:** React + TypeScript + Vite, in [`frontend/`](frontend)
- **Database:** SQLite on your computer, PostgreSQL ([Neon](https://neon.com)) when deployed
- **Hosting:** [Render](https://render.com), both parts on the free plan

## Run it locally (Windows, PowerShell)

You need Python 3.11 and Node.js (LTS).

**1. Backend** (first terminal):

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs: <http://localhost:8000/docs>. Tasks are saved in `backend/tasks.db`
(created automatically, never committed).

**2. Frontend** (second terminal):

```powershell
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>.

## API

| Method | Path | Body | Success | Errors |
|---|---|---|---|---|
| GET | `/health` | none | 200 `{"status": "ok"}` | none |
| GET | `/tasks` | none | 200, list of tasks | none |
| POST | `/tasks` | `{"title": "..."}` | 201, new task | 422 empty/too long title |
| PATCH | `/tasks/{id}` | `{"completed": true}` | 200, updated task | 404, 422 |
| DELETE | `/tasks/{id}` | none | 204 | 404 |

A task looks like `{"id": 1, "title": "Buy milk", "completed": false}`.

## Settings (environment variables)

| Name | Where | What it does |
|---|---|---|
| `DATABASE_URL` | backend | Postgres connection string. If missing, SQLite is used. |
| `FRONTEND_URL` | backend | Deployed frontend address, allowed by CORS. |
| `VITE_API_URL` | frontend (build time) | Backend address. Defaults to `http://localhost:8000`. |

## Deploy (Render + Neon, free)

1. **Neon:** create a free project and copy its connection string
   (`postgresql://...`). Keep it secret.
2. **Render:** New > Blueprint > pick this GitHub repo. Render reads
   [`render.yaml`](render.yaml) and creates two services:
   - `task-tracker-api` (backend). Set `DATABASE_URL` to the Neon string.
   - `task-tracker-web` (frontend).
3. After the first deploy, copy each service's `.onrender.com` address and set:
   - `FRONTEND_URL` on the backend = the frontend address
   - `VITE_API_URL` on the frontend = the backend address

   Then redeploy both (the frontend must be rebuilt to pick up `VITE_API_URL`).

Every push to `main` redeploys automatically.

**Free plan notes:** the backend sleeps after 15 minutes without visits, so the
first request afterwards can take up to a minute. Data is safe in Neon because
Render's free disk is wiped on every restart.
