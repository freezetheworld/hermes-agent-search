#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
VENV="${AGENT_SEARCH_MCP_VENV:-$ROOT/mcp-server/.venv}"
NAME="${AGENT_SEARCH_MCP_NAME:-agent-search}"
PYTHON="${PYTHON:-python3}"

command -v hermes >/dev/null 2>&1 || {
  echo "Hermes Agent is required: https://hermes-agent.nousresearch.com/docs" >&2
  exit 1
}

AGENT_SEARCH_MCP_VENV="$VENV" PYTHON="$PYTHON" "$ROOT/scripts/install-mcp.sh" >/dev/null

hermes mcp remove "$NAME" >/dev/null 2>&1 || true
hermes mcp add "$NAME" --command "$VENV/bin/agent-search-mcp"

cat <<EOF
Hermes MCP server registered as: $NAME
Command: $VENV/bin/agent-search-mcp

Start the search API, then verify:
  cd "$ROOT"
  ./scripts/prepare-searxng.sh
  docker compose up -d --build
  hermes mcp test "$NAME"
EOF
