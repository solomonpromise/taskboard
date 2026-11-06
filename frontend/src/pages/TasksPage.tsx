import { useCallback, useEffect, useState, type FormEvent } from "react";
import { api, ApiError, type Label, type Page, type Task, type User } from "../api/client";
import { TaskForm } from "../components/TaskForm";
import { TaskRow } from "../components/TaskRow";
import { Toast } from "../components/Toast";

type Props = { user: User; status: "open" | "done" };
type LoadState = "loading" | "ready" | "error";

// "My tasks" and "Completed". Every data screen has four states: loading, empty, success, error (Chapter 6).
export function TasksPage({ user, status }: Props) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [labels, setLabels] = useState<Label[]>([]);
  const [state, setState] = useState<LoadState>("loading");
  const [error, setError] = useState<string>("");
  const [busyId, setBusyId] = useState<number | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [newLabel, setNewLabel] = useState("");

  const load = useCallback(async () => {
    setState("loading");
    try {
      const [page, labelPage] = await Promise.all([
        api<Page<Task>>("GET", `/v1/tasks?status=${status}&limit=100`),
        api<Page<Label>>("GET", "/v1/labels"),
      ]);
      setTasks(page.items);
      setLabels(labelPage.items);
      setState("ready");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't load your tasks.");
      setState("error");
    }
  }, [status]);

  useEffect(() => {
    load();
  }, [load]);

  const clearToast = useCallback(() => setToast(null), []);

  async function run(task: Task, action: () => Promise<void>, failure: string) {
    setBusyId(task.id);
    try {
      await action();
    } catch (err) {
      setToast(err instanceof ApiError ? err.message : failure);
    } finally {
      setBusyId(null);
    }
  }

  const toggle = (task: Task) =>
    run(task, async () => {
      await api<Task>("PATCH", `/v1/tasks/${task.id}`, { is_done: !task.is_done });
      setTasks((current) => current.filter((t) => t.id !== task.id));
      setToast(task.is_done ? "Moved back to My tasks" : "Task completed");
    }, "Couldn't update the task.");

  const remove = (task: Task) =>
    run(task, async () => {
      await api("DELETE", `/v1/tasks/${task.id}`);
      setTasks((current) => current.filter((t) => t.id !== task.id));
      setToast("Task deleted");
    }, "Couldn't delete the task.");

  const attach = (task: Task, labelId: number) =>
    run(task, async () => {
      await api("POST", `/v1/tasks/${task.id}/labels`, { label_id: labelId });
      const label = labels.find((l) => l.id === labelId)!;
      setTasks((current) => current.map((t) => (t.id === task.id ? { ...t, labels: [...t.labels, label] } : t)));
    }, "Couldn't add the label.");

  async function createLabel(event: FormEvent) {
    event.preventDefault();
    if (!newLabel.trim()) return;
    try {
      const label = await api<Label>("POST", "/v1/labels", { name: newLabel });
      setLabels((current) => [...current, label].sort((a, b) => a.name.localeCompare(b.name)));
      setNewLabel("");
      setToast(`Label "${label.name}" created`);
    } catch (err) {
      setToast(err instanceof ApiError ? err.message : "Couldn't create the label.");
    }
  }

  const overdue = tasks.filter((t) => t.is_overdue).length;
  const heading = status === "open" ? "My tasks" : "Completed";

  return (
    <section aria-labelledby="page-heading">
      <h1 id="page-heading">{heading}</h1>
      {state === "ready" && (
        <p className="summary">
          {tasks.length} {status === "open" ? "open" : "completed"}
          {status === "open" && overdue > 0 ? ` · ${overdue} overdue` : ""}
        </p>
      )}

      {status === "open" && (
        <TaskForm timeZone={user.time_zone} onCreated={(task) => {
          setTasks((current) => [...current, task].sort(byDueDate));
          setToast("Task added");
        }} />
      )}

      {state === "loading" && (
        <ul className="task-list" aria-busy="true" aria-label="Loading tasks">
          {[1, 2, 3].map((i) => <li key={i} className="task-row skeleton" />)}
        </ul>
      )}

      {state === "error" && (
        <div className="error-panel" role="alert">
          <p><strong>Couldn't load tasks.</strong> {error}</p>
          <button className="button" type="button" onClick={load}>Try again</button>
        </div>
      )}

      {state === "ready" && tasks.length === 0 && (
        <div className="empty">
          <p className="empty-title">{status === "open" ? "No tasks yet" : "Nothing completed yet"}</p>
          <p>{status === "open" ? "Add your first task above." : "Tick a task in My tasks and it will appear here."}</p>
        </div>
      )}

      {state === "ready" && tasks.length > 0 && (
        <ul className="task-list">
          {tasks.map((task) => (
            <TaskRow key={task.id} task={task} labels={labels} busy={busyId === task.id}
              onToggle={toggle} onDelete={remove} onAttach={attach} />
          ))}
        </ul>
      )}

      {status === "open" && state === "ready" && (
        <form className="label-form" onSubmit={createLabel}>
          <label htmlFor="new-label">New label</label>
          <input id="new-label" value={newLabel} maxLength={40} placeholder="e.g. work"
            onChange={(e) => setNewLabel(e.target.value)} />
          <button className="button ghost" type="submit">Create label</button>
        </form>
      )}

      {toast && <Toast message={toast} onDone={clearToast} />}
    </section>
  );
}

// Same order as the backend: soonest due first, undated last.
function byDueDate(a: Task, b: Task): number {
  if (a.due_date === b.due_date) return a.id - b.id;
  if (!a.due_date) return 1;
  if (!b.due_date) return -1;
  return a.due_date < b.due_date ? -1 : 1;
}
