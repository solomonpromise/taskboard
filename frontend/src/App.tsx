import { useCallback, useEffect, useState } from "react";
import { api, type User } from "./api/client";
import { Header } from "./components/Header";
import { SignInPage } from "./pages/SignInPage";
import { SignUpPage } from "./pages/SignUpPage";
import { TasksPage } from "./pages/TasksPage";

// A tiny router: each screen has its own URL (book Chapter 6), with no extra dependency.
export type Route = "/" | "/completed" | "/sign-in" | "/sign-up";

function currentRoute(): Route {
  const path = window.location.pathname as Route;
  return ["/", "/completed", "/sign-in", "/sign-up"].includes(path) ? path : "/";
}

export default function App() {
  const [route, setRoute] = useState<Route>(currentRoute());
  const [user, setUser] = useState<User | null | undefined>(undefined); // undefined = still checking

  const navigate = useCallback((to: Route) => {
    window.history.pushState({}, "", to);
    setRoute(to);
  }, []);

  useEffect(() => {
    const onPop = () => setRoute(currentRoute());
    window.addEventListener("popstate", onPop);
    api<User>("GET", "/v1/me")
      .then(setUser)
      .catch(() => setUser(null)); // 401 (not signed in) or unreachable: show sign-in
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  useEffect(() => {
    if (user === null && (route === "/" || route === "/completed")) navigate("/sign-in");
    if (user && (route === "/sign-in" || route === "/sign-up")) navigate("/");
  }, [user, route, navigate]);

  if (user === undefined) {
    return <p className="page-loading" role="status">Loading Taskboard…</p>;
  }

  if (!user) {
    return (
      <main className="auth-page">
        {route === "/sign-up"
          ? <SignUpPage onSignedIn={setUser} navigate={navigate} />
          : <SignInPage onSignedIn={setUser} navigate={navigate} />}
      </main>
    );
  }

  return (
    <>
      <Header user={user} route={route} navigate={navigate} onSignedOut={() => setUser(null)} />
      <main className="page">
        <TasksPage key={route} user={user} status={route === "/completed" ? "done" : "open"} />
      </main>
    </>
  );
}
