#!/usr/bin/env python3
"""Perplexity AI Search - Web search, research, and reasoning via Perplexity API.

Use Cases:
- Web search with AI-powered answers
- Deep research on topics
- Reasoning through complex problems
- Quick questions with citations

Usage:
  # Quick question/search
  uv run python -m runtime.harness scripts/perplexity_search.py \
    --ask "What is the latest version of Python?"

  # Web search
  uv run python -m runtime.harness scripts/perplexity_search.py \
    --search "best practices for async Python 2025"

  # Deep research
  uv run python -m runtime.harness scripts/perplexity_search.py \
    --research "compare FastAPI vs Django for microservices"

  # Reasoning mode
  uv run python -m runtime.harness scripts/perplexity_search.py \
    --reason "should I use MongoDB or PostgreSQL for a chat app?"

Requires: perplexity server in mcp_config.json with PERPLEXITY_API_KEY
"""

import argparse
import asyncio
import json
import sys


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="AI search via Perplexity")

    # Modes (mutually exclusive)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--ask", help="Quick question/answer")
    group.add_argument("--search", help="Web search query")
    group.add_argument("--research", help="Deep research topic")
    group.add_argument("--reason", help="Reasoning/analysis query")

    args_to_parse = [arg for arg in sys.argv[1:] if not arg.endswith(".py")]
    return parser.parse_args(args_to_parse)


async def main():
    from runtime.mcp_client import call_mcp_tool

    args = parse_args()

    if args.ask:
        print(f"Asking: {args.ask}")
        result = await call_mcp_tool("perplexity__perplexity_ask", {
            "messages": [{"role": "user", "content": args.ask}]
        })
        mode = "Ask"

    elif args.search:
        print(f"Searching: {args.search}")
        result = await call_mcp_tool("perplexity__perplexity_search", {
            "query": args.search
        })
        mode = "Search"

    elif args.research:
        print(f"Researching: {args.research}")
        result = await call_mcp_tool("perplexity__perplexity_research", {
            "messages": [{"role": "user", "content": args.research}]
        })
        mode = "Research"

    elif args.reason:
        print(f"Reasoning: {args.reason}")
        result = await call_mcp_tool("perplexity__perplexity_reason", {
            "messages": [{"role": "user", "content": args.reason}]
        })
        mode = "Reason"

    print(f"\n✓ {mode} complete\n")

    # Format output nicely
    if isinstance(result, dict):
        # Try to extract main content
        if "answer" in result:
            print(result["answer"])
        elif "content" in result:
            print(result["content"])
        elif "response" in result:
            print(result["response"])
        else:
            print(json.dumps(result, indent=2))

        # Print citations if available
        if "citations" in result and result["citations"]:
            print("\n📚 Sources:")
            for i, cite in enumerate(result["citations"][:5], 1):
                if isinstance(cite, dict):
                    print(f"  {i}. {cite.get('url', cite.get('title', cite))}")
                else:
                    print(f"  {i}. {cite}")
    else:
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
