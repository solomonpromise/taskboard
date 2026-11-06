# Maintenance guide

## Monitoring
- Uptime check on `/health` every minute (a free monitoring tier, or a script calling it).
- Structured JSON logs with request IDs; no passwords, tokens or request bodies.
- Alert when the error rate is above 1% for 5 minutes, or health fails twice in a row.

## Routine
- **Weekly:** triage new issues and errors; review dependency updates (CI audits run on every PR).
- **Monthly:** restore drill from a backup (time it); review hosting costs and capacity; repay one
  item from [`debt.md`](debt.md); check README, `AGENTS.md` and docs are still true.
- **Quarterly:** review ADR "revisit if" conditions; rotate long-lived credentials; review access.

## Backups
`make backup` locally; in production, the managed database's point-in-time recovery plus a weekly
export to separate storage. Targets: RPO 5 minutes, RTO 1 hour.
