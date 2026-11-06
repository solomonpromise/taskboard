# ADR 001: Start as a responsive web application
Date: 2026-11-05 · Status: Accepted

**Context.** Users switch between laptop and phone; one builder; quick feedback wanted.
**Options.** Web app; native mobile apps; desktop app.
**Decision.** A responsive web app with an API, so a mobile app could reuse the API later.
**Consequences.** One codebase, instant updates; needs a connection; no push notifications yet.
**Revisit if.** Users need offline use or notifications.
