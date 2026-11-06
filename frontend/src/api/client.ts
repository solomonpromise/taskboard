// Every call to the backend goes through here (book Chapter 8).
// - Cookies are sent by the browser automatically; JavaScript never sees the HttpOnly session cookie.
// - Requests that change data send the CSRF token from the readable csrf_token cookie (Chapter 11).
// - Requests time out instead of waiting forever, and errors arrive in one shape.

export class ApiError extends Error {
  constructor(public status: number, public code: string, message: string) {
    super(message);
  }
}

const TIMEOUT_MS = 10_000;

function csrfToken(): string {
  const match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/);
  return match ? decodeURIComponent(match[1]) : "";
}

export async function api<T>(
  method: "GET" | "POST" | "PATCH" | "DELETE",
  path: string,
  body?: unknown,
  options: { idempotencyKey?: string } = {},
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  const headers: Record<string, string> = { Accept: "application/json" };
  if (body !== undefined) headers["Content-Type"] = "application/json";
  if (method !== "GET") headers["X-CSRF-Token"] = csrfToken();
  if (options.idempotencyKey) headers["Idempotency-Key"] = options.idempotencyKey;

  let response: Response;
  try {
    response = await fetch(path, {
      method,
      headers,
      body: body === undefined ? undefined : JSON.stringify(body),
      credentials: "same-origin",
      signal: controller.signal,
    });
  } catch {
    throw new ApiError(0, "network_error", "Couldn't reach Taskboard. Check your connection and try again.");
  } finally {
    clearTimeout(timer);
  }

  if (response.status === 204) return undefined as T;
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = data?.error ?? {};
    throw new ApiError(response.status, error.code ?? "error", error.message ?? "Something went wrong.");
  }
  return data as T;
}

export type User = { id: number; name: string; email: string; time_zone: string };
export type Label = { id: number; name: string };
export type Task = {
  id: number;
  title: string;
  due_date: string | null;
  is_done: boolean;
  is_overdue: boolean;
  created_at: string;
  completed_at: string | null;
  labels: Label[];
};
export type Page<T> = { items: T[]; next_cursor: number | null };
