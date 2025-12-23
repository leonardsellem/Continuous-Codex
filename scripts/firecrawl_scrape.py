#!/usr/bin/env python3
"""Firecrawl Scrape via MCP - Scrape URLs or search the web."""

import argparse
import asyncio
import json
import sys


def parse_args():
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Scrape web via Firecrawl MCP")
    parser.add_argument("--url", help="URL to scrape")
    parser.add_argument("--search", help="Search query (alternative to URL)")
    parser.add_argument("--format", choices=["markdown", "html", "text"],
                        default="markdown", help="Output format")
    parser.add_argument("--limit", type=int, default=5, help="Max results for search")

    args_to_parse = [arg for arg in sys.argv[1:] if not arg.endswith(".py")]
    return parser.parse_args(args_to_parse)


async def main():
    from runtime.mcp_client import call_mcp_tool

    args = parse_args()

    if not args.url and not args.search:
        print("Error: Either --url or --search is required")
        return

    if args.url:
        print(f"Scraping: {args.url}")
        result = await call_mcp_tool("firecrawl__firecrawl_scrape", {
            "url": args.url,
            "formats": [args.format]
        })
    else:
        print(f"Searching: {args.search}")
        result = await call_mcp_tool("firecrawl__firecrawl_search", {
            "query": args.search,
            "limit": args.limit
        })

    print(f"✓ Complete")
    print(json.dumps(result, indent=2) if isinstance(result, dict) else result)


if __name__ == "__main__":
    asyncio.run(main())
