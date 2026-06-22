#!/usr/bin/env python3
"""User-friendly CLI for sample, live, and MCP competitive-intelligence flows."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import live_demo_check
import local_intel


def focus_to_event_query(focus: str | None) -> str | None:
    if not focus:
        return None
    terms = [term.strip() for term in focus.split(",") if term.strip()]
    if not terms:
        return None
    return "(" + " OR ".join(terms) + ")"


def print_artifacts(result: dict[str, Any]) -> None:
    paths = result.get("paths", {})
    if paths:
        for label, path in paths.items():
            print(f"{label.replace('_', ' ').title()}: {path}")
        return

    for label in ("brief", "dashboard"):
        artifact = result.get(label, {})
        path = artifact.get("path")
        if path:
            print(f"{label.title()}: {path}")


def run_sample(args: argparse.Namespace) -> int:
    result = local_intel.analyze_saved_articles(
        config_path=args.config,
        input_path=args.input,
        output_dir=args.output_dir,
        slug=args.slug,
        dashboard=args.dashboard,
    )
    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    print("Mode: sample")
    print(f"Articles analyzed: {result['article_count']}")
    print(f"Events found: {result['event_count']}")
    print_artifacts(result)
    return 0


def run_live(args: argparse.Namespace) -> int:
    event_query = args.event_query or focus_to_event_query(args.focus)
    result = live_demo_check.run_check(
        slug=args.slug,
        output_dir=args.output_dir,
        competitors=args.competitors,
        event_query=event_query,
        max_results=args.max_results,
        search_days_back=args.search_days_back,
    )
    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result.get("ok") else 1

    print("Mode: live CocoIndex")
    update = result.get("update", {})
    effective_config = update.get("effective_config", {})
    if effective_config:
        print(f"Competitors: {effective_config.get('competitors') or 'env default'}")
        print(f"Event query: {effective_config.get('event_query') or 'env default'}")
        print(f"Max results per competitor: {effective_config.get('max_results_per_competitor')}")

    if not result.get("ok"):
        print(f"Status: failed at {result.get('stage', 'unknown')}")
        if "missing_env" in result:
            print("Missing env: " + ", ".join(result["missing_env"]))
        elif update:
            stderr = update.get("stderr", "").strip()
            if stderr:
                print(stderr[-1200:])
        return 1

    trends = result.get("trends", {}).get("results", [])
    search = result.get("search", {})
    print(f"Indexed events returned: {search.get('matched_events', 0)}")
    if trends:
        print("Trending competitors:")
        for row in trends[:5]:
            print(f"- {row['competitor']}: {row['total_events']} events")
    print_artifacts(result)
    return 0


def run_mcp(_: argparse.Namespace) -> int:
    import mcp_server

    mcp_server.mcp.run()
    return 0


def add_common_output_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--slug", help="Output filename slug")
    parser.add_argument("--output-dir", help="Directory for generated reports")
    parser.add_argument("--json", action="store_true", help="Print full structured JSON output")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run competitive intelligence in sample, live CocoIndex, or MCP mode."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    sample = subparsers.add_parser("sample", help="Run the no-credential sample workflow")
    sample.add_argument("--config", type=Path, default=local_intel.DEFAULT_CONFIG)
    sample.add_argument("--input", type=Path, default=local_intel.DEFAULT_INPUT)
    sample.add_argument("--dashboard", action="store_true", help="Generate a static dashboard")
    add_common_output_args(sample)
    sample.set_defaults(func=run_sample)

    live = subparsers.add_parser("live", help="Run live Tavily/OpenRouter/CocoIndex ingestion")
    live.add_argument(
        "--competitors",
        help='Comma-separated competitors for this run, e.g. "Apple,Microsoft"',
    )
    live.add_argument(
        "--focus",
        help='Comma-separated focus areas, e.g. "funding, partnerships, product launches"',
    )
    live.add_argument("--event-query", help="Advanced Tavily query expression; overrides --focus")
    live.add_argument("--max-results", type=int, default=1, help="Max results per competitor")
    live.add_argument("--search-days-back", type=int, default=7, help="Search recency window")
    add_common_output_args(live)
    live.set_defaults(func=run_live)

    mcp = subparsers.add_parser("mcp", help="Start the MCP tool server for agents")
    mcp.set_defaults(func=run_mcp)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
