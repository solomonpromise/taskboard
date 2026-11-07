# Architecture

## Components (C4 container view)

```mermaid
flowchart LR
  user((User)) -->|HTTPS| web[Web app<br/>React]
  web -->|JSON + cookie + CSRF header| api[API<br/>FastAPI]
  api -->|SQL, owner-filtered| db[(Database)]
  job[Reminder job] --> db
  job --> email[Email adapter] -->|SMTP| provider[Email provider]
```

**Trust boundary:** everything arriving at the API from the browser or a webhook is untrusted:
it is authenticated (session), checked (CSRF on changes), validated, and authorised (owner)
before anything touches the database.

## Creating a task

```mermaid
sequenceDiagram
  participant B as Browser
  participant A as API
  participant D as Database
  B->>B: check title not empty (convenience)
  B->>A: POST /v1/tasks (cookie added by browser, X-CSRF-Token, Idempotency-Key)
  A->>A: session → user · CSRF check · validate title and due date
  A->>D: INSERT task with owner_id = session user (parameterised)
  D-->>A: new row (constraints checked)
  A-->>B: 201 task JSON
  B->>B: show task, "Task added"
```

## Signing in

```mermaid
sequenceDiagram
  participant B as Browser
  participant A as API
  participant D as Database
  B->>A: POST /v1/auth/sign-in {email, password} over HTTPS
  A->>A: sign-in guess limit for this email
  A->>D: find user by email
  A->>A: verify password against the Argon2 hash
  alt wrong email or password
    A-->>B: 401 "Email or password is incorrect" (same message either way)
  else correct
    A->>D: store a hash of a new random session token
    A-->>B: 200 user JSON + Set-Cookie: session (HttpOnly, SameSite=Lax) and CSRF cookie
    B->>A: GET /v1/tasks (cookie added by browser)
  end
```

## Retrieving tasks later

```mermaid
sequenceDiagram
  participant B as Browser
  participant A as API
  participant D as Database
  B->>B: show loading rows
  B->>A: GET /v1/tasks?status=open (session cookie)
  A->>D: look up the session by token hash → user
  A->>D: SELECT … WHERE owner_id = user AND is_done = false (index on owner_id, is_done, due_date)
  D-->>A: rows, soonest due first, undated last
  A-->>B: 200 {items, next_cursor}
  B->>B: show the list; overdue tasks marked with icon and text
```
