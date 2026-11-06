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
