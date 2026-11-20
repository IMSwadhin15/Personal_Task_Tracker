import { useEffect, useState } from 'react'
import { createTask, deleteTask, listTasks, setTaskCompleted, type Task } from './api'
import AddTaskForm from './components/AddTaskForm'
import TaskItem from './components/TaskItem'

export default function App() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true) // true until the first load finishes
  const [error, setError] = useState<string | null>(null)
  const [busyId, setBusyId] = useState<number | null>(null) // task being updated

  // Load the tasks once, when the page first opens.
  useEffect(() => {
    listTasks()
      .then(setTasks)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  async function handleAdd(title: string) {
    setError(null)
    try {
      const task = await createTask(title)
      setTasks((current) => [...current, task])
    } catch (e) {
      setError((e as Error).message)
      throw e // let the form know it failed, so it keeps the typed text
    }
  }

  async function handleToggle(task: Task) {
    setError(null)
    setBusyId(task.id)
    try {
      const updated = await setTaskCompleted(task.id, !task.completed)
      setTasks((current) => current.map((t) => (t.id === updated.id ? updated : t)))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusyId(null)
    }
  }

  async function handleDelete(task: Task) {
    setError(null)
    setBusyId(task.id)
    try {
      await deleteTask(task.id)
      setTasks((current) => current.filter((t) => t.id !== task.id))
    } catch (e) {
      setError((e as Error).message)
    } finally {
      setBusyId(null)
    }
  }

  const remaining = tasks.filter((t) => !t.completed).length

  return (
    <main className="app">
      <h1>My Tasks</h1>

      <AddTaskForm onAdd={handleAdd} />

      {error && (
        <p className="error" role="alert">
          {error}
          <button type="button" onClick={() => setError(null)} aria-label="Dismiss error">
            ×
          </button>
        </p>
      )}

      {loading ? (
        <p className="muted">Loading tasks…</p>
      ) : tasks.length === 0 ? (
        // If loading failed, the error above explains it; don't claim "no tasks".
        !error && <p className="muted">No tasks yet. Add one above.</p>
      ) : (
        <>
          <ul className="task-list">
            {tasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                busy={busyId === task.id}
                onToggle={handleToggle}
                onDelete={handleDelete}
              />
            ))}
          </ul>
          <p className="muted">
            {remaining} of {tasks.length} left
          </p>
        </>
      )}
    </main>
  )
}
