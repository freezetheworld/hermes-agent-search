#!/usr/bin/env python3
"""Deterministic CLI for the local AgentSearch and CloakBrowser stack."""
from __future__ import annotations

import argparse
import ipaddress
import json
import socket
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import requests

API = "http://127.0.0.1:3939"


def emit(data, code: int = 0) -> None:
    print(json.dumps(data, ensure_ascii=False, indent=2))
    raise SystemExit(code)


def validate_public_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("URL must use http:// or https:// and include a hostname")
    host = parsed.hostname.lower().rstrip(".")
    if host in {"localhost", "localhost.localdomain"}:
        raise ValueError("Localhost targets are blocked")
    try:
        addresses = {item[4][0] for item in socket.getaddrinfo(host, parsed.port or 443)}
    except socket.gaierror as exc:
        raise ValueError(f"DNS resolution failed: {exc}") from exc
    for raw in addresses:
        ip = ipaddress.ip_address(raw)
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_multicast or ip.is_reserved:
            raise ValueError(f"Private or non-routable target blocked: {ip}")
    return value


def api_get(path: str, params: dict, timeout: int) -> dict:
    response = requests.get(API + path, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def warp_available() -> bool:
    try:
        with socket.create_connection(("127.0.0.1", 2080), timeout=1):
            return True
    except OSError:
        return False


def cloak_fetch(url: str, max_chars: int, timeout: int, screenshot: str | None) -> dict:
    from cloakbrowser import launch

    validate_public_url(url)
    proxy = "socks5://127.0.0.1:2080" if warp_available() else None
    browser = None
    started = time.monotonic()
    try:
        browser = launch(headless=True, proxy=proxy) if proxy else launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=timeout * 1000, wait_until="domcontentloaded")
        page.wait_for_timeout(1500)
        title = page.title()
        final_url = page.url
        text = page.locator("body").inner_text(timeout=10000).strip()
        links = page.locator("a[href]").evaluate_all(
            "els => els.slice(0, 100).map(a => ({text:(a.innerText||'').trim(), url:a.href}))"
        )
        html = page.content()
        if screenshot:
            destination = Path(screenshot).expanduser().resolve()
            destination.parent.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(destination), full_page=True)
        markers = ("captcha", "cf-chl", "cloudflare challenge", "unusual traffic", "/sorry/")
        challenge = any(marker in (final_url + "\n" + title + "\n" + html[:50000]).lower() for marker in markers)
        return {
            "success": bool(text) and not challenge,
            "strategy": "cloakbrowser-warp" if proxy else "cloakbrowser-direct",
            "requested_url": url,
            "final_url": final_url,
            "title": title,
            "challenge_detected": challenge,
            "chars": min(len(text), max_chars),
            "content": text[:max_chars],
            "links": links,
            "screenshot": str(Path(screenshot).expanduser().resolve()) if screenshot else None,
            "elapsed_ms": round((time.monotonic() - started) * 1000, 1),
        }
    finally:
        if browser is not None:
            browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("health")

    for name in ("search", "deep"):
        p = sub.add_parser(name)
        p.add_argument("query")
        p.add_argument("--count", type=int, default=8)
        p.add_argument("--mode", default="general")

    for name in ("read", "browser", "cloak"):
        p = sub.add_parser(name)
        p.add_argument("url")
        p.add_argument("--max-chars", type=int, default=12000)
        p.add_argument("--timeout", type=int, default=60)
        if name == "cloak":
            p.add_argument("--screenshot")

    args = parser.parse_args()
    try:
        if args.command == "health":
            data = api_get("/health", {}, 30)
            data["warp_socks_available"] = warp_available()
            emit(data)
        if args.command == "search":
            emit(api_get("/search", {"q": args.query, "count": args.count, "mode": args.mode}, 120))
        if args.command == "deep":
            emit(api_get("/search/deep", {"q": args.query, "count": args.count, "mode": args.mode}, 180))
        if args.command == "read":
            validate_public_url(args.url)
            emit(api_get("/read", {"url": args.url, "max_chars": args.max_chars}, args.timeout))
        if args.command == "browser":
            validate_public_url(args.url)
            emit(api_get("/providers/browser/fetch", {"url": args.url, "max_chars": args.max_chars}, args.timeout))
        if args.command == "cloak":
            emit(cloak_fetch(args.url, args.max_chars, args.timeout, args.screenshot))
    except Exception as exc:
        emit({"success": False, "error": f"{type(exc).__name__}: {exc}"}, 1)


if __name__ == "__main__":
    main()
