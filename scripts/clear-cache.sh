#!/usr/bin/env bash
# Clear all persistent cache and learned state for agent-search.
# Usage: ./scripts/clear-cache.sh [--tor]
#   default: clears the production data volume (agent-search-data)
#   --tor:   clears the Tor-mode data volume (agent-search-data-tor)

set -euo pipefail

MODE="${1:-default}"
case "$MODE" in
  --tor) CONTAINER="agent-search-api-tor" ; LABEL="Tor-mode" ;;
  default|"") CONTAINER="agent-search-api" ; LABEL="default" ;;
  *) echo "usage: $0 [--tor]" >&2 ; exit 2 ;;
esac

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "container $CONTAINER not running — start the stack first" >&2
  exit 1
fi

echo "Clearing $LABEL cache via $CONTAINER..."

docker exec -i "$CONTAINER" python3 - <<'PY'
import sqlite3, os, time
data = "/app/data"
for db, tables in [
    ("content_cache.db", ["content_cache", "fetch_log"]),
    ("query_log.db",     ["query_log"]),
]:
    p = os.path.join(data, db)
    if not os.path.exists(p):
        print(f"  skip (missing): {db}")
        continue
    c = sqlite3.connect(p)
    for t in tables:
        try:
            n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            c.execute(f"DELETE FROM {t}")
            c.execute(f"DELETE FROM sqlite_sequence WHERE name='{t}'")
            print(f"  cleared {db}:{t} ({n} rows)")
        except sqlite3.OperationalError as e:
            print(f"  skip {db}:{t} — {e}")
    c.commit()
    c.execute("VACUUM")
    c.close()

bl = os.path.join(data, "blocked_domains.txt")
if os.path.exists(bl):
    size = os.path.getsize(bl)
    open(bl, "w").close()
    print(f"  cleared blocked_domains.txt ({size} bytes)")
PY

echo "Restarting $CONTAINER to flush in-memory cache..."
docker restart "$CONTAINER" >/dev/null

# Health probe: wait for the recreated API process instead of assuming a fixed sleep is enough.
PORT=$(docker port "$CONTAINER" 3939/tcp 2>/dev/null | head -1 | cut -d: -f2)
if [ -n "$PORT" ]; then
  for attempt in {1..30}; do
    if curl -fsS "http://localhost:${PORT}/health"; then
      echo
      echo "Done."
      exit 0
    fi
    sleep 1
  done
  echo "API did not become healthy within 30 seconds" >&2
  exit 1
fi

echo "API port mapping not found after restart" >&2
exit 1
