# Generic MCP clients

Install the MCP package:

```bash
./scripts/install-mcp.sh
```

Copy the executable path printed by the installer into your client's stdio MCP
configuration:

```json
{
  "mcpServers": {
    "agent-search": {
      "command": "/absolute/path/to/agent-search-stack/mcp-server/.venv/bin/agent-search-mcp"
    }
  }
}
```

This shape works with clients such as Claude Desktop, Cursor, Windsurf, and other
applications that support stdio MCP servers. Restart or reload the client after
changing its configuration.

The command connects to the AgentSearch API at `http://localhost:3939` by
default. Use `--host` and `--port` in the client's `args` array for another
address.
