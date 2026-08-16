# Hermes Agent integration

Hermes is one optional MCP client for Agent Search Stack.

```bash
./scripts/install-mcp.sh
hermes mcp remove agent-search 2>/dev/null || true
hermes mcp add agent-search \
  --command "$PWD/mcp-server/.venv/bin/agent-search-mcp"
hermes mcp test agent-search
```

Alternatively, run the convenience wrapper:

```bash
./docs/integrations/install-hermes.sh
```

Use `/reload-mcp` or begin a new session after changing MCP configuration.
