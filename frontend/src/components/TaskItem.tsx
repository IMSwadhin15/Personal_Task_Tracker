import type { Task } from '../api'

type Props = {
  task: Task
  busy: boolean // true while a request for this task is in flight
  onToggle: (task: Task) => void
  onDelete: (task: Task) => void
}

export default function TaskItem({ task, busy, onToggle, onDelete }: Props) {
  return (
    <li className={task.completed ? 'task done' : 'task'}>
      <label>
        <input
          type="checkbox"
          checked={task.completed}
          disabled={busy}
          onChange={() => onToggle(task)}
        />
        <span>{task.title}</span>
      </label>
      <button
        type="button"
        className="delete"
        disabled={busy}
        onClick={() => onDelete(task)}
        aria-label={`Delete "${task.title}"`}
      >
        Delete
      </button>
    </li>
  )
}
