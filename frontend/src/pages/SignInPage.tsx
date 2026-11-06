import { useState, type FormEvent } from "react";
import { api, ApiError, type User } from "../api/client";
import type { Route } from "../App";

type Props = { onSignedIn: (user: User) => void; navigate: (to: Route) => void };

// Taskboard's sign-in screen (book Figure 11.2).
export function SignInPage({ onSignedIn, navigate }: Props) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      onSignedIn(await api<User>("POST", "/v1/auth/sign-in", { email, password }));
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Couldn't sign in. Please try again.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="auth-card" onSubmit={submit}>
      <h1>Sign in to Taskboard</h1>
      <label htmlFor="email">Email</label>
      <input id="email" type="email" autoComplete="email" required value={email}
        onChange={(e) => setEmail(e.target.value)} />
      <label htmlFor="password">Password</label>
      <div className="password-field">
        <input id="password" type={showPassword ? "text" : "password"} autoComplete="current-password"
          required value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="button" className="link-button" aria-pressed={showPassword}
          onClick={() => setShowPassword((s) => !s)}>{showPassword ? "Hide" : "Show"}</button>
      </div>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="button wide" type="submit" disabled={busy}>{busy ? "Signing in…" : "Sign in"}</button>
      <p className="switch">
        New to Taskboard?{" "}
        <a href="/sign-up" onClick={(e) => { e.preventDefault(); navigate("/sign-up"); }}>Create an account</a>
      </p>
    </form>
  );
}
