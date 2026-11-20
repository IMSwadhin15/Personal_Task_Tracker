// A small typed client for the Task Tracker API.
// Every function returns a Promise and throws an Error with a readable
// message if the server answers with an error status.

export type Task = {
  id: number
  title: string
  completed: boolean
}

// In development the backend runs on port 8000. When deployed, set
// VITE_API_URL to the backend's public address at build time.
// (A trailing "/" is removed so "https://x.com/" + "/tasks" doesn't become "//tasks".)
const API_URL: string = (import.meta.env.VITE_API_URL ?? 'http://localhost:8000').replace(/\/$/, '')

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response
  try {
    response = await fetch(API_URL + path, {
      ...options,
      headers: { 'Content-Type': 'application/json' },
    })
  } catch {
    // fetch only throws when the server can't be reached at all.
    throw new Error('Cannot reach the server. Is the backend running?')
  }

  if (!response.ok) {
    throw new Error(await errorMessage(response))
  }

  // 204 No Content (used by DELETE) has no body to read.
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

// FastAPI sends errors as {"detail": "..."} or, for validation errors,
// {"detail": [{"msg": "..."}, ...]}. Turn either into one sentence.
async function errorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json()
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) {
      return body.detail.map((d: { msg: string }) => d.msg).join(', ')
    }
  } catch {
    // The body wasn't JSON; fall through to the generic message.
  }
  return `Request failed (${response.status})`
}

export function listTasks(): Promise<Task[]> {
  return request<Task[]>('/tasks')
}

export function createTask(title: string): Promise<Task> {
  return request<Task>('/tasks', {
    method: 'POST',
    body: JSON.stringify({ title }),
  })
}

export function setTaskCompleted(id: number, completed: boolean): Promise<Task> {
  return request<Task>(`/tasks/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ completed }),
  })
}

export function deleteTask(id: number): Promise<void> {
  return request<void>(`/tasks/${id}`, { method: 'DELETE' })
}
