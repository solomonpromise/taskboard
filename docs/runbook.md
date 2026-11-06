# Runbook

Short, numbered steps for when things go wrong (book Chapters 31–33). Keep this file true.

## Deploy
1. Merge a reviewed pull request with passing CI.
2. Build and release the Docker image (or push to your platform); migrations run before the server starts.
3. Smoke-test: `make smoke URL=https://your-staging-or-production-url`.

## Roll back a release
1. Use the hosting platform's "roll back" to the previous release.
2. Confirm `/health` and the smoke test pass. Investigate afterwards.
3. Database changes are expand-and-contract, so the previous release works with the current schema.

## Restore the database
1. Stop further damage (revoke access, maintenance mode).
2. Restore the most recent good backup into a **new** database:
   - SQLite: `cp backups/taskboard-<stamp>.sqlite backend/restored.db`
   - PostgreSQL: `pg_restore --dbname=<new database url> backups/taskboard-<stamp>.dump`
3. Verify counts and a few known records; then point `DATABASE_URL` at it and restart.
4. Record what happened in a blameless review.

## Rotate a secret
1. Create the new value (database password, SMTP credentials).
2. Set it in the platform's secret settings; redeploy; confirm health.
3. Revoke the old value. If it leaked, check the provider's logs for misuse.

## Incident response
Detect → assess → **mitigate first (roll back)** → communicate → resolve → learn.
