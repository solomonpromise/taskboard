import { useRef, useState, type FormEvent } from "react";
import { api, ApiError, type Task } from "../api/client";
import { localToday } from "../lib/dates";

type Props = { timeZone: string; onCreated: (task: Task) => void };

const newKey = () => crypto.randomUUID();

// The "new task" form (book Figure 6.1, marker 4): labelled inputs, a quick client-side check
// for convenience (the backend checks again), "Saving…" while busy, and input kept if saving fails.
export function TaskForm({ timeZone, onCreated }: Props) {
  const [title, setTitle] = useState("");
  const [dueDate, setDueDate] = useState("");
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const idempotencyKey = useRef(newKey()); // one key per task being added: a double submit creates one task
  const titleInput = useRef<HTMLInputElement>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!title.trim()) {
      setError("Please add a title.");
      titleInput.current?.focus();
      return;
    }
    setSaving(true);
    setError(null);
    try {
      const task = await api<Task>("POST", "/v1/tasks", { title, due_date: dueDate || null },
        { idempotencyKey: idempotencyKey.current });
      onCreated(task);
      setTitle("");
      setDueDate("");
      idempotencyKey.current = newKey();
      titleInput.current?.focus();
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't save the task. Please try again.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <form className="task-form" onSubmit={submit} noValidate>
      <div className="field grow">
        <label htmlFor="task-title">Task title</label>
        <input
          id="task-title"
          ref={titleInput}
          value={title}
          maxLength={200}
          placeholder="e.g. Submit invoice"
          aria-invalid={error ? true : undefined}
          aria-describedby={error ? "task-form-error" : undefined}
          onChange={(e) => setTitle(e.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="task-due">Due date (optional)</label>
        <input id="task-due" type="date" min={localToday(timeZone)} value={dueDate}
          onChange={(e) => setDueDate(e.target.value)} />
      </div>
      <button className="button" type="submit" disabled={saving}>{saving ? "Saving…" : "+ Add task"}</button>
      {error && <p id="task-form-error" className="form-error" role="alert">{error}</p>}
    </form>
  );
}
