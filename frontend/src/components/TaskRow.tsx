import type { Label, Task } from "../api/client";
import { formatDueDate } from "../lib/dates";

type Props = {
  task: Task;
  labels: Label[];
  busy: boolean;
  onToggle: (task: Task) => void;
  onDelete: (task: Task) => void;
  onAttach: (task: Task, labelId: number) => void;
};

function DueBadge({ task }: { task: Task }) {
  if (task.is_done) return null;
  if (!task.due_date) return <span className="badge muted">No date</span>;
  // Overdue is shown with an icon AND words, never colour alone (book Chapter 6).
  if (task.is_overdue) return <span className="badge danger">⚠ Overdue · {formatDueDate(task.due_date)}</span>;
  return <span className="badge info">Due {formatDueDate(task.due_date)}</span>;
}

// One component for every task row (book Figure 6.1, marker 6).
export function TaskRow({ task, labels, busy, onToggle, onDelete, onAttach }: Props) {
  const checkboxId = `task-${task.id}-done`;
  const available = labels.filter((l) => !task.labels.some((tl) => tl.id === l.id));
  return (
    <li className={`task-row${task.is_overdue ? " overdue" : ""}`}>
      <input id={checkboxId} type="checkbox" checked={task.is_done} disabled={busy}
        onChange={() => onToggle(task)} />
      <label htmlFor={checkboxId} className={task.is_done ? "done" : undefined}>{task.title}</label>
      <span className="meta">
        <span className="chips">
          {task.labels.map((l) => <span key={l.id} className="chip">{l.name}</span>)}
        </span>
        {!task.is_done && available.length > 0 && (
          <select aria-label={`Add a label to ${task.title}`} value=""
            onChange={(e) => e.target.value && onAttach(task, Number(e.target.value))}>
            <option value="">+ label</option>
            {available.map((l) => <option key={l.id} value={l.id}>{l.name}</option>)}
          </select>
        )}
        <DueBadge task={task} />
      </span>
      <button type="button" className="icon-button" aria-label={`Delete task: ${task.title}`}
        disabled={busy} onClick={() => onDelete(task)}>✕</button>
    </li>
  );
}
