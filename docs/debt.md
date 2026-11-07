# Technical debt

Known compromises, why they were made, and what repaying them takes (book Chapter 23).

| Item | Why | Repay by |
|---|---|---|
| Sign-in guess limiting is in memory, per process | Simple for one server | Store attempt counts in the database or a cache when running several servers |
| Breached-password check uses a small built-in list | No external dependency | Add a k-anonymity breached-password service check at sign-up |
| No password reset or email verification yet | Out of scope for v1 | Add verified email first, then single-use, time-limited reset links |
| Reminder window is 07:00–07:14 local time | Job runs every 15 minutes | Fine unless users ask for custom times |
| Open-task limit counts rows in Python | Simple and correct at current scale | Use a COUNT query if the limit grows |
| If the same task field is edited on two devices at once, the last edit wins | One person per account makes it rare; updates send only changed fields | Add a `version` column and return 409 on a stale update before adding shared tasks |
| No account export or deletion yet | Outside the v1 brief | Before a public launch: let users download their data and delete their account, including from backups as they expire |
| No end-to-end tests yet | Unit, API and permission tests came first | Add three browser tests (sign up and add a task; complete a task; a second user cannot see it) with Playwright |
| Tests use `httpx` with Starlette's test client, which now recommends a newer client package | Verify the recommended package's origin and maintainers before adopting it (book Chapter 16) | Switch `requirements-dev.txt` once verified; remove the warning filter in `pytest.ini` |
