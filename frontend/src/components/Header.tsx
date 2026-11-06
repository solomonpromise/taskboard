import { api, type User } from "../api/client";
import type { Route } from "../App";

type Props = { user: User; route: Route; navigate: (to: Route) => void; onSignedOut: () => void };

export function Header({ user, route, navigate, onSignedOut }: Props) {
  const link = (to: Route, label: string) => (
    <a
      href={to}
      aria-current={route === to ? "page" : undefined}
      onClick={(event) => {
        event.preventDefault();
        navigate(to);
      }}
    >
      {label}
    </a>
  );

  async function signOut() {
    await api("POST", "/v1/auth/sign-out").catch(() => undefined);
    onSignedOut();
  }

  return (
    <header className="site-header">
      <div className="brand" aria-label="Taskboard">☑ Taskboard</div>
      <nav aria-label="Main">
        {link("/", "My tasks")}
        {link("/completed", "Completed")}
      </nav>
      <div className="account">
        <span className="avatar" aria-hidden="true">{user.name.charAt(0).toUpperCase()}</span>
        <span className="sr-only">Signed in as {user.name}</span>
        <button type="button" className="button ghost" onClick={signOut}>Sign out</button>
      </div>
    </header>
  );
}
