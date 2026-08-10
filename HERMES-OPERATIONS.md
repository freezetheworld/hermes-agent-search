# Hermes Web Research Stack — Operations

## Live architecture

```text
Hermes
  └─ MCP agent-search (16 tools)
       └─ AgentSearch API 127.0.0.1:3939
            └─ private SearXNG 127.0.0.1:8888 / Docker network

Extraction escalation
  1. AgentSearch `read_url` / `search_extract`
  2. Crawl4AI `/home/hermes/services/web-research/extract.py`
  3. Hermes interactive browser
  4. agent-browser CLI with installed Chrome 151
  5. CloakBrowser + WARP SOCKS 127.0.0.1:2080
```

All HTTP and SOCKS listeners are bound to localhost. Nothing in this stack is publicly exposed.

## Installed locations

- AgentSearch checkout and Compose stack: `/home/hermes/services/agent-search`
- AgentSearch MCP virtualenv: `/home/hermes/services/agent-search/mcp-server/.venv`
- Deterministic fallback CLI: `/home/hermes/services/agent-search/scripts/web_stack.py`
- Crawl4AI extractor: `/home/hermes/services/web-research/extract.py`
- Crawl4AI virtualenv: `/home/hermes/services/web-research/.venv-crawl4ai`
- agent-browser Chrome: `/home/hermes/.agent-browser/browsers/chrome-151.0.7922.77`
- Hermes MCP config: `/home/hermes/.hermes/config.yaml`

## Research order

1. Search with `mcp__agent_search__search`, `search_strategy`, `source_search`, or `news`.
2. Open primary sources, not only snippets. Use `read_url`, `search_extract`, or `read_batch`.
3. Use Crawl4AI when clean Markdown or deterministic JavaScript rendering is needed.
4. Use the built-in Hermes browser for interaction, forms, and visual state.
5. Use CloakBrowser + WARP only for bot-sensitive pages.
6. Cross-check consequential claims across independent sources and label uncertainty.
7. Do not equate “page returned” with “requested source returned”; check URL, title, provenance, and challenge/consent text.

`deep_search` generates query variants and can drift. Use it for broad discovery, then validate results against the original question.

## Health

```bash
cd /home/hermes/services/agent-search

docker compose ps
curl -fsS http://127.0.0.1:3939/health | python3 -m json.tool
curl -fsS 'http://127.0.0.1:8888/search?q=healthcheck&format=json' >/dev/null
hermes mcp test agent-search
warp-cli --accept-tos status
ss -ltnp | grep -E ':(3939|8888|2080)\b'
```

Expected live state:

- `agent-search-api`: healthy/reachable on `127.0.0.1:3939`
- `agent-search-searxng`: running on `127.0.0.1:8888`
- MCP `agent-search`: connected with 16 tools
- `warp-svc`: enabled, active, proxy mode on `127.0.0.1:2080`

## Functional checks

Search:

```bash
cd /home/hermes/services/agent-search
python3 scripts/web_stack.py search 'Hermes Agent Nous Research GitHub' --count 3
```

Normal extraction:

```bash
python3 scripts/web_stack.py read \
  'https://hermes-agent.nousresearch.com/docs/reference/tools-reference' \
  --max-chars 2000
```

Clean Markdown extraction:

```bash
/home/hermes/services/web-research/extract.py 'https://example.com'
```

Stealth-browser escalation:

```bash
cd /home/hermes/services/agent-search
python3 scripts/web_stack.py cloak 'https://bot.sannysoft.com/' \
  --max-chars 2000 --timeout 90
```

## Lifecycle

Start or rebuild:

```bash
cd /home/hermes/services/agent-search
docker compose up -d --build
warp-cli --accept-tos mode proxy
warp-cli --accept-tos proxy port 2080
warp-cli --accept-tos connect
```

Stop only AgentSearch/SearXNG:

```bash
cd /home/hermes/services/agent-search
docker compose stop
```

Do not disconnect WARP unless no other workload uses its local proxy.

Restart and verify:

```bash
cd /home/hermes/services/agent-search
docker compose restart
./scripts/clear-cache.sh
hermes mcp test agent-search
```

Logs:

```bash
cd /home/hermes/services/agent-search
docker compose logs --tail=200 api searxng
journalctl -u warp-svc --since '1 hour ago' --no-pager
```

## Local reliability fixes

This checkout intentionally differs from upstream:

- Obsolete Google Cache fallback is disabled. Google removed public cache, and its endpoint returned unrelated consent/search pages as false source content.
- `scripts/clear-cache.sh` forwards its Python heredoc into Docker correctly and waits for API readiness.
- Regression coverage lives in `tests/test_killchain_regressions.py`.

Before pulling upstream changes:

```bash
cd /home/hermes/services/agent-search
git status --short
git log --oneline -5
python3 -m pytest tests -q
```

Reapply or retain those fixes if upstream still contains the obsolete fallback.

## Security and limitations

- URLs passed to the helper are restricted to public HTTP(S) targets; private/loopback destinations are rejected.
- Never paste proxy credentials into chat. Install secrets directly on the server if a residential proxy is later required.
- No browser can guarantee every page. Authentication, account authorization, hard paywalls, legal restrictions, CAPTCHAs, and IP reputation remain external controls.
- Direct Google and WARP-routed Google were blocked from this VPS during verification. SearXNG still returned real results through working engines such as Bing. A legitimate residential proxy or paid search API would be required for dependable exact-Google access.
