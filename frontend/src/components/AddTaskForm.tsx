import { useState, type FormEvent } from 'react'

type Props = {
  // Called with the trimmed title. Resolves when the task is saved.
  onAdd: (title: string) => Promise<void>
}

export default function AddTaskForm({ onAdd }: Props) {
  const [title, setTitle] = useState('')
  const [saving, setSaving] = useState(false)

  async function handleSubmit(event: FormEvent) {
    event.preventDefault() // stop the browser from reloading the page
    const trimmed = title.trim()
    if (!trimmed) return

    setSaving(true)
    try {
      await onAdd(trimmed)
      setTitle('') // only clear the box if saving worked
    } catch {
      // The parent (App) already shows the error message; keep the text.
    } finally {
      setSaving(false)
    }
  }

  return (
    <form className="add-form" onSubmit={handleSubmit}>
      <input
        type="text"
        placeholder="What do you need to do?"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        maxLength={200}
        disabled={saving}
        aria-label="New task title"
      />
      <button type="submit" disabled={saving || !title.trim()}>
        {saving ? 'Adding…' : 'Add'}
      </button>
    </form>
  )
}
