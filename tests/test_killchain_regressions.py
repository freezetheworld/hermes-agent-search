import asyncio
from pathlib import Path

import httpx

from app import killchain


ROOT = Path(__file__).resolve().parents[1]


def test_clear_cache_forwards_heredoc_to_container_stdin():
    script = (ROOT / "scripts" / "clear-cache.sh").read_text()
    assert 'docker exec -i "$CONTAINER" python3 -' in script


def test_clear_cache_waits_until_api_is_ready():
    script = (ROOT / "scripts" / "clear-cache.sh").read_text()
    assert "for attempt in {1..30}" in script
    assert "API did not become healthy" in script


def test_kill_chain_does_not_use_obsolete_google_cache(monkeypatch):
    """Google Cache now serves unrelated Google pages and must not be trusted."""
    google_cache_called = False

    async def empty(*args, **kwargs):
        return None

    async def obsolete_google_cache(*args, **kwargs):
        nonlocal google_cache_called
        google_cache_called = True
        return "Google consent page masquerading as cached source" * 10

    monkeypatch.setattr(killchain, "strategy_direct", empty)
    monkeypatch.setattr(killchain, "strategy_readability", empty)
    monkeypatch.setattr(killchain, "strategy_ua_rotation", empty)
    monkeypatch.setattr(killchain, "strategy_browser_render", empty)
    monkeypatch.setattr(killchain, "strategy_wayback", empty)
    monkeypatch.setattr(killchain, "strategy_google_cache", obsolete_google_cache)
    monkeypatch.setattr(killchain, "strategy_search_about", empty)
    monkeypatch.setattr(killchain, "strategy_adapter", empty)
    monkeypatch.setattr(killchain, "_load_cloudflare_adapter", lambda: None)

    async def run_case():
        async with httpx.AsyncClient() as client:
            return await killchain.kill_chain(
                client,
                "https://example.com/short-page",
                skip_cache=True,
            )

    result = asyncio.run(run_case())

    assert google_cache_called is False
    assert "google-cache" not in result.strategies_tried
