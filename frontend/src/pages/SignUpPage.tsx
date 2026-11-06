import { useState, type FormEvent } from "react";
import { api, ApiError, type User } from "../api/client";
import type { Route } from "../App";
import { browserTimeZone } from "../lib/dates";

type Props = { onSignedIn: (user: User) => void; navigate: (to: Route) => void };

export function SignUpPage({ onSignedIn, navigate }: Props) {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const timeZone = browserTimeZone(); // "today" is always the user's local date (book Chapter 10)

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      onSignedIn(await api<User>("POST", "/v1/auth/sign-up", { name, email, password, time_zone: timeZone }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't create your account. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="auth-card" onSubmit={submit}>
      <h1>Create your Taskboard account</h1>
      <label htmlFor="name">Name</label>
      <input id="name" autoComplete="name" required value={name} onChange={(e) => setName(e.target.value)} />
      <label htmlFor="email">Email</label>
      <input id="email" type="email" autoComplete="email" required value={email}
        onChange={(e) => setEmail(e.target.value)} />
      <label htmlFor="password">Password</label>
      <input id="password" type="password" autoComplete="new-password" required minLength={15}
        aria-describedby="password-hint" value={password} onChange={(e) => setPassword(e.target.value)} />
      <p id="password-hint" className="hint">At least 15 characters. A short phrase of a few words works well.</p>
      <p className="hint">Time zone: {timeZone}</p>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="button wide" type="submit" disabled={busy}>{busy ? "Creating…" : "Create account"}</button>
      <p className="switch">
        Already have an account?{" "}
        <a href="/sign-in" onClick={(e) => { e.preventDefault(); navigate("/sign-in"); }}>Sign in</a>
      </p>
    </form>
  );
}
