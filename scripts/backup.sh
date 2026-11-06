#!/bin/sh
# Back up the database (book Chapter 33). Copy the backups/ folder somewhere else too (3-2-1 rule),
# and practise restoring: see docs/runbook.md.
set -e
cd "$(dirname "$0")/.."
mkdir -p backups
STAMP=$(date -u +%Y%m%dT%H%M%SZ)
URL=$(grep -E '^DATABASE_URL=' backend/.env 2>/dev/null | cut -d= -f2-)
URL=${DATABASE_URL:-$URL}
case "$URL" in
  sqlite:///*)
    FILE="backend/${URL#sqlite:///./}"
    sqlite3 "$FILE" ".backup 'backups/taskboard-$STAMP.sqlite'" 2>/dev/null || cp "$FILE" "backups/taskboard-$STAMP.sqlite"
    echo "Backed up $FILE to backups/taskboard-$STAMP.sqlite" ;;
  postgresql*)
    pg_dump "$(echo "$URL" | sed 's/+psycopg//')" --format=custom --file="backups/taskboard-$STAMP.dump"
    echo "Backed up PostgreSQL to backups/taskboard-$STAMP.dump" ;;
  *) echo "Unknown DATABASE_URL; nothing backed up" >&2; exit 1 ;;
esac
