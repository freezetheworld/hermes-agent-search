# Hermes AgentSearch — operations

## Architecture

```text
Hermes
  └─ MCP agent-search (stdio)
       └─ AgentSearch API 127.0.0.1:3939
            └─ SearXNG 127.0.0.1:8888 / private Docker network

Extraction escalation
  1. Direct fetch and readability extraction
  2. User-agent rotation
  3. Ephemeral browser rendering
  4. Wayback/search-about fallbacks
  5. Site adapters, PDF extraction, and YouTube transcripts
```

All bundled listeners bind to loopback by default. The API is not publicly
exposed unless an operator deliberately changes the Compose port mappings.

## Install

Requirements:

- Linux or macOS with Python 3.11+
- Docker with Compose v2
- [Hermes Agent](https://hermes-agent.nousresearch.com/docs)

```bash
git clone https://github.com/freezetheworld/hermes-agent-search.git
cd hermes-agent-search
./scripts/prepare-searxng.sh
docker compose up -d --build
./scripts/install-hermes.sh
hermes mcp test agent-search
```

The installer creates `mcp-server/.venv`, installs the packaged MCP server, and
registers its absolute executable path with Hermes. Use `/reload-mcp` or start a
new Hermes session after changing MCP configuration.

## Health and functional checks

Run these from the repository root:

```bash
docker compose ps
curl -fsS http://127.0.0.1:3939/health | python3 -m json.tool
curl -fsS 'http://127.0.0.1:8888/search?q=healthcheck&format=json' >/dev/null
hermes mcp test agent-search

python3 scripts/web_stack.py search 'Hermes Agent Nous Research GitHub' --count 3
python3 scripts/web_stack.py read 'https://example.com' --max-chars 2000
```

## Lifecycle

```bash
# Start or rebuild
./scripts/prepare-searxng.sh
docker compose up -d --build

# Logs
docker compose logs --tail=200 api searxng

# Restart and clear local result caches
docker compose restart
./scripts/clear-cache.sh

# Stop this stack only
docker compose stop
```

## Optional CloakBrowser/WARP escalation

`scripts/web_stack.py cloak URL` can use CloakBrowser when installed. If a SOCKS
listener is available at `127.0.0.1:2080`, the command routes the browser through
it; otherwise it launches directly. Neither CloakBrowser nor Cloudflare WARP is
installed automatically by this repository.

```bash
python3 scripts/web_stack.py cloak 'https://example.com' \
  --max-chars 2000 --timeout 90 --screenshot /tmp/example.png
```

This is a rendering fallback, not a promise to bypass access controls. Login,
paywalls, CAPTCHA, robots rules, authorization, and IP reputation remain external
controls. Do not use the software to evade legal or contractual restrictions.

## Secrets

Bearer authentication is optional. Store a token outside Git:

```bash
install -d -m 700 ~/.config/agent-search
python3 - <<'PY'
from pathlib import Path
import secrets
p = Path.home() / '.config/agent-search/token'
p.write_text(secrets.token_urlsafe(48) + '\n')
p.chmod(0o600)
print(f'Created {p}')
PY
```

Export that value locally as `AGENT_SEARCH_TOKEN` before starting Compose. Never
paste credentials into prompts, issues, logs, or committed files. See
[`docs/secrets.md`](docs/secrets.md).

## Research discipline

1. Search for candidate sources.
2. Open and read primary sources; snippets are leads, not proof.
3. Check requested URL, final URL, title, provenance, and challenge indicators.
4. Cross-check consequential claims across independent sources.
5. Report access failures honestly instead of fabricating missing content.

`deep_search` generates query variants and may drift. Validate merged results
against the original question.

## Verification before updates

```bash
git status --short --branch
python3 -m pytest tests -q
python3 -m compileall app adapters mcp-server/agent_search_mcp scripts sdk -q
docker compose config --quiet
```