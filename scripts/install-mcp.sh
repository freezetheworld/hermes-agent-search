#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV="${AGENT_SEARCH_MCP_VENV:-$ROOT/mcp-server/.venv}"
PYTHON="${PYTHON:-python3}"

command -v "$PYTHON" >/dev/null 2>&1 || {
  echo "Python 3 is required." >&2
  exit 1
}

"$PYTHON" -m venv "$VENV"
"$VENV/bin/python" -m pip install --upgrade pip
"$VENV/bin/python" -m pip install -e "$ROOT/mcp-server"

COMMAND="$VENV/bin/agent-search-mcp"
cat <<EOF
AgentSearch MCP server installed.

Executable:
  $COMMAND

Generic stdio MCP configuration:
{
  "mcpServers": {
    "agent-search": {
      "command": "$COMMAND"
    }
  }
}

Start the API before connecting your agent:
  cd "$ROOT"
  ./scripts/prepare-searxng.sh
  docker compose up -d --build
EOF
