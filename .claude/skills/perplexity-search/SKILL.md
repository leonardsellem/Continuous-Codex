---
name: perplexity-search
description: AI-powered web search, research, and reasoning via Perplexity
allowed-tools: [Bash, Read]
---

# Perplexity AI Search

Web search with AI-powered answers, deep research, and reasoning capabilities.

## When to Use

- Search the web for current information
- Research topics with citations
- Get AI reasoning on complex questions
- Quick factual questions

## Usage

### Quick question
```bash
uv run python -m runtime.harness scripts/perplexity_search.py \
    --ask "What is the latest version of Python?"
```

### Web search
```bash
uv run python -m runtime.harness scripts/perplexity_search.py \
    --search "best practices async Python 2025"
```

### Deep research
```bash
uv run python -m runtime.harness scripts/perplexity_search.py \
    --research "compare FastAPI vs Django for microservices"
```

### Reasoning mode
```bash
uv run python -m runtime.harness scripts/perplexity_search.py \
    --reason "should I use MongoDB or PostgreSQL for a chat app?"
```

## Parameters

| Parameter | Description |
|-----------|-------------|
| `--ask` | Quick question/answer |
| `--search` | Web search query |
| `--research` | Deep research topic |
| `--reason` | Reasoning/analysis query |

## Modes

| Mode | Best For |
|------|----------|
| `--ask` | Quick factual questions |
| `--search` | Finding current information |
| `--research` | In-depth topic exploration |
| `--reason` | Decision-making, analysis |

## Examples

```bash
# Current events
uv run python -m runtime.harness scripts/perplexity_search.py \
    --search "MCP model context protocol latest updates"

# Technical research
uv run python -m runtime.harness scripts/perplexity_search.py \
    --research "WebSocket vs SSE for real-time updates"

# Architecture decision
uv run python -m runtime.harness scripts/perplexity_search.py \
    --reason "microservices vs monolith for startup MVP"
```

## MCP Server Required

Requires `perplexity` server in mcp_config.json with `PERPLEXITY_API_KEY`.
