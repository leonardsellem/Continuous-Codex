#!/usr/bin/env python3
"""Nia Documentation Search - Search packages and indexed sources.

Use Cases:
- Search for library usage patterns across 3000+ packages
- Query indexed repositories and documentation
- Find code examples and best practices

Usage:
  # Search packages (no indexing required)
  uv run python -m runtime.harness scripts/nia_docs.py \
    --package fastapi --query "dependency injection"

  # Search with specific registry
  uv run python -m runtime.harness scripts/nia_docs.py \
    --package react --registry npm --query "hooks patterns"

  # Universal search across indexed sources
  uv run python -m runtime.harness scripts/nia_docs.py \
    --search "error handling middleware"

  # Grep search for specific patterns
  uv run python -m runtime.harness scripts/nia_docs.py \
    --package sqlalchemy --grep "session.execute"

Registries: npm, py_pi, crates, go_modules

Requires: NIA_API_KEY environment variable or nia server in mcp_config.json
"""

import argparse
import asyncio
import json
import os
import sys
from typing import Optional

# API base URL
NIA_API_URL = os.environ.get("NIA_API_URL", "https://apigcp.trynia.ai")
NIA_API_KEY = os.environ.get("NIA_API_KEY", "")


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Search docs via Nia API")
    parser.add_argument("--package", help="Package name to search in")
    parser.add_argument("--registry", choices=["npm", "py_pi", "crates", "go_modules"],
                        default="npm", help="Package registry (default: npm)")
    parser.add_argument("--query", help="Semantic search query")
    parser.add_argument("--grep", help="Regex pattern to search for")
    parser.add_argument("--search", help="Universal search across indexed sources")
    parser.add_argument("--limit", type=int, default=5, help="Max results (default: 5)")

    args_to_parse = [arg for arg in sys.argv[1:] if not arg.endswith(".py")]
    return parser.parse_args(args_to_parse)


async def package_search_hybrid(package: str, query: str, registry: str = "npm", limit: int = 5) -> dict:
    """Semantic search within a package."""
    import aiohttp

    url = f"{NIA_API_URL}/v2/package-search/hybrid"
    headers = {
        "Authorization": f"Bearer {NIA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "registry": registry,
        "package_name": package,
        "semantic_queries": [query],
        "limit": limit
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return {"error": f"API error {resp.status}: {error_text}"}
            return await resp.json()


async def package_search_grep(package: str, pattern: str, registry: str = "npm", limit: int = 5) -> dict:
    """Regex search within a package."""
    import aiohttp

    url = f"{NIA_API_URL}/v2/package-search/grep"
    headers = {
        "Authorization": f"Bearer {NIA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "registry": registry,
        "package_name": package,
        "pattern": pattern,
        "limit": limit
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return {"error": f"API error {resp.status}: {error_text}"}
            return await resp.json()


async def universal_search(query: str, limit: int = 5) -> dict:
    """Search across all indexed sources."""
    import aiohttp

    url = f"{NIA_API_URL}/v2/universal-search"
    headers = {
        "Authorization": f"Bearer {NIA_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "query": query,
        "search_mode": "unified",
        "limit": limit
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                return {"error": f"API error {resp.status}: {error_text}"}
            return await resp.json()


def format_results(result: dict, search_type: str) -> str:
    """Format results for display."""
    if "error" in result:
        return f"❌ Error: {result['error']}"

    output = [f"✓ {search_type} completed\n"]

    # Handle different response structures
    if "results" in result:
        for i, item in enumerate(result["results"][:10], 1):
            if isinstance(item, dict):
                title = item.get("title", item.get("path", f"Result {i}"))
                snippet = item.get("snippet", item.get("content", ""))[:200]
                output.append(f"\n{i}. {title}")
                if snippet:
                    output.append(f"   {snippet}...")
            else:
                output.append(f"\n{i}. {str(item)[:200]}")
    elif "matches" in result:
        for i, match in enumerate(result["matches"][:10], 1):
            path = match.get("path", "unknown")
            line = match.get("line", "")
            output.append(f"\n{i}. {path}")
            if line:
                output.append(f"   {line}")
    else:
        output.append(json.dumps(result, indent=2))

    return "\n".join(output)


async def main():
    args = parse_args()

    # Get API key from environment or try to load from mcp_config
    global NIA_API_KEY
    if not NIA_API_KEY:
        try:
            import pathlib
            config_path = pathlib.Path(__file__).parent.parent / "mcp_config.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    nia_config = config.get("mcpServers", {}).get("nia", {})
                    NIA_API_KEY = nia_config.get("env", {}).get("NIA_API_KEY", "")
        except Exception:
            pass

    if not NIA_API_KEY:
        print("Error: NIA_API_KEY not found. Set it in environment or mcp_config.json")
        return

    if not args.package and not args.search:
        print("Error: Either --package or --search is required")
        print("\nExamples:")
        print("  --package fastapi --query 'dependency injection'")
        print("  --package react --grep 'useState'")
        print("  --search 'authentication middleware'")
        return

    try:
        if args.search:
            print(f"🔍 Universal search: {args.search}")
            result = await universal_search(args.search, args.limit)
            print(format_results(result, "Universal search"))
        elif args.grep:
            print(f"🔍 Grep search in {args.package}: {args.grep}")
            result = await package_search_grep(args.package, args.grep, args.registry, args.limit)
            print(format_results(result, "Grep search"))
        elif args.query:
            print(f"🔍 Semantic search in {args.package}: {args.query}")
            result = await package_search_hybrid(args.package, args.query, args.registry, args.limit)
            print(format_results(result, "Semantic search"))
        else:
            print("Error: --query, --grep, or --search is required")

    except ImportError:
        print("Error: aiohttp not installed. Run: pip install aiohttp")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
