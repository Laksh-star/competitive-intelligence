#!/usr/bin/env python3
"""Check the live CocoIndex/Postgres demo path and generate live artifacts."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any

import env_utils
import mcp_server


REQUIRED_ENV = ("COCOINDEX_DATABASE_URL", "TAVILY_API_KEY", "OPENAI_API_KEY")


def run_check(
    slug: str = "live-cocoindex",
    output_dir: str | None = None,
    competitors: str | None = None,
    event_query: str | None = None,
    max_results: int | None = None,
    search_days_back: int | None = None,
) -> dict[str, Any]:
    env_utils.load_env()
    missing = [key for key in REQUIRED_ENV if not os.getenv(key)]
    if missing:
        return {
            "ok": False,
            "stage": "env",
            "missing_env": missing,
            "message": "Add missing values to .env before running live mode.",
        }

    update = mcp_server.run_cocoindex_update(
        live=True,
        force=True,
        competitors=competitors,
        event_query=event_query,
        max_results=max_results,
        search_days_back=search_days_back,
    )
    if not update["ok"]:
        return {"ok": False, "stage": "cocoindex_update", "update": update}

    trends = mcp_server.get_trending_competitors(mode="cocoindex", limit=10)
    search = mcp_server.search_events(mode="cocoindex", limit=10)
    brief = mcp_server.create_brief(mode="cocoindex", output_dir=output_dir, slug=f"{slug}-brief")
    dashboard = mcp_server.create_dashboard(
        mode="cocoindex", output_dir=output_dir, slug=f"{slug}-dashboard"
    )
    return {
        "ok": True,
        "stage": "complete",
        "update": update,
        "trends": trends,
        "search": search,
        "brief": brief,
        "dashboard": dashboard,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run live CocoIndex demo checks.")
    parser.add_argument("--slug", default="live-cocoindex")
    parser.add_argument("--output-dir")
    parser.add_argument("--competitors", help="Comma-separated competitors for this live run.")
    parser.add_argument("--event-query", help="Tavily query fragment for this live run.")
    parser.add_argument("--max-results", type=int, help="Max Tavily results per competitor.")
    parser.add_argument("--search-days-back", type=int, help="Limit Tavily recency window.")
    args = parser.parse_args()
    result = run_check(
        slug=args.slug,
        output_dir=args.output_dir,
        competitors=args.competitors,
        event_query=args.event_query,
        max_results=args.max_results,
        search_days_back=args.search_days_back,
    )
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
