---
name: web-research-stack
description: Use when researching current web information with the self-hosted AgentSearch MCP server. Provides an evidence-first search, extraction, and browser-escalation workflow for any compatible agent.
version: 1.0.0
author: Agent Search Stack Contributors
license: MIT
metadata:
  tags: [web-search, research, mcp, searxng, source-verification]
---

# Web Research Stack

## Overview

Use the local `agent-search` MCP tools for current facts, online research, source
verification, URL extraction, and crawling. The stack is self-hosted and backed
by SearXNG plus AgentSearch's extraction chain.

## When to use

- The task depends on current web facts, news, documentation, or primary sources.
- A URL needs readable extraction or JavaScript rendering.
- Several query variants or source types must be fused.

Do not use search snippets alone as evidence, and do not claim unrestricted web
access when a source requires login, payment, CAPTCHA, or authorization.

## Workflow

1. If the user supplied a URL, inspect that source before doing general search.
2. Discover sources with normal or strategy search.
3. Open promising results with URL or batch extraction.
4. Use browser rendering when ordinary extraction is incomplete.
5. Verify requested URL, final URL, title, provenance, and challenge indicators.
6. Cross-check consequential claims across independent sources.
7. Cite URLs and label uncertainty or access barriers explicitly.

## Useful operations

```bash
python3 scripts/web_stack.py health
python3 scripts/web_stack.py search 'query' --count 10
python3 scripts/web_stack.py deep 'complex question' --count 10
python3 scripts/web_stack.py read 'https://example.org' --max-chars 12000
python3 scripts/web_stack.py browser 'https://example.org' --max-chars 12000
```

## Common pitfalls

1. Treating snippets as source evidence instead of opening the page.
2. Reporting consent or challenge text as the requested article.
3. Allowing deep-search query variants to drift away from the original question.
4. Assuming every engine works continuously; upstream engines can rate-limit or
   return CAPTCHA pages.
5. Fabricating missing values instead of reporting an access limitation.

## Verification checklist

- [ ] Current claims came from live sources.
- [ ] Important sources were opened and read.
- [ ] URLs and provenance were checked.
- [ ] Consequential claims were cross-checked.
- [ ] Uncertainty and access failures were stated honestly.
