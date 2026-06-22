#!/usr/bin/env python3
"""Deterministic agent-style demo for the competitive intelligence MCP tools."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import mcp_server


PROJECT_ROOT = Path(__file__).parent
DEFAULT_OUTPUT_DIR = PROJECT_ROOT / "reports"


def _json_block(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2)


def _line(title: str) -> str:
    return f"\n## {title}\n"


def run_demo(output_dir: Path = DEFAULT_OUTPUT_DIR, slug: str = "agent-demo") -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    transcript: list[str] = [
        "# Agent Demo Transcript",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "This transcript simulates an agent using the MCP tools in sample mode.",
    ]

    transcript.append(_line("Agent Goal"))
    transcript.append(
        "Find the strongest competitive signals, summarize trends, and create "
        "shareable briefing artifacts without requiring live credentials."
    )

    analysis = mcp_server.analyze_saved_articles(
        output_dir=str(output_dir),
        slug=slug,
        dashboard=True,
    )
    transcript.append(_line("Tool Call: analyze_saved_articles"))
    transcript.append(_json_block({
        "article_count": analysis["article_count"],
        "event_count": analysis["event_count"],
        "paths": analysis["paths"],
    }))

    trends = mcp_server.get_trending_competitors(limit=3)
    transcript.append(_line("Tool Call: get_trending_competitors"))
    transcript.append(_json_block(trends))

    enterprise_events = mcp_server.search_events(query="enterprise", limit=5)
    transcript.append(_line("Tool Call: search_events"))
    transcript.append(_json_block({
        "query": "enterprise",
        "matched_events": enterprise_events["matched_events"],
        "results": enterprise_events["results"],
    }))

    brief = mcp_server.create_brief(output_dir=str(output_dir), slug=f"{slug}-brief")
    dashboard = mcp_server.create_dashboard(output_dir=str(output_dir), slug=f"{slug}-dashboard")
    transcript.append(_line("Tool Calls: create_brief and create_dashboard"))
    transcript.append(_json_block({
        "brief_path": brief["path"],
        "dashboard_path": dashboard["path"],
    }))

    live_guard = mcp_server.run_cocoindex_update(live=False)
    transcript.append(_line("Tool Call: run_cocoindex_update"))
    transcript.append(
        "The agent asks about live ingestion, and the tool refuses to run because "
        "live mode was not explicitly enabled."
    )
    transcript.append(_json_block(live_guard))

    top_trend = trends["results"][0] if trends["results"] else {}
    transcript.append(_line("Agent Summary"))
    transcript.append(
        f"Top active competitor: {top_trend.get('competitor', 'None')}. "
        f"Total sample events: {analysis['event_count']}. "
        "Recommended next step: review the generated brief and dashboard, then "
        "switch selected calls to mode='cocoindex' after live credentials are configured."
    )

    transcript_path = output_dir / f"{slug}-transcript.md"
    transcript_path.write_text("\n".join(transcript), encoding="utf-8")

    return {
        "transcript_path": str(transcript_path),
        "analysis": analysis,
        "trends": trends,
        "enterprise_events": enterprise_events,
        "brief": brief,
        "dashboard": dashboard,
        "live_guard": live_guard,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run the deterministic agent demo.")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--slug", default="agent-demo")
    parser.add_argument("--json", action="store_true", help="Print full JSON output")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = run_demo(output_dir=args.output_dir, slug=args.slug)
    if args.json:
        print(json.dumps(result, indent=2))
        return
    print(f"Transcript: {result['transcript_path']}")
    print(f"Brief: {result['brief']['path']}")
    print(f"Dashboard: {result['dashboard']['path']}")
    print(f"Top competitor: {result['trends']['results'][0]['competitor']}")


if __name__ == "__main__":
    main()
