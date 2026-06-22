#!/usr/bin/env python3
"""MCP tools for agent-first competitive intelligence demos."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import env_utils
import providers

env_utils.load_env()


try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # Allows direct smoke tests before installing mcp[cli].
    FastMCP = None


class _ToolRegistry:
    """Tiny decorator-compatible registry used when MCP is not installed."""

    def __init__(self, name: str):
        self.name = name
        self.tools = {}

    def tool(self):
        def decorator(func):
            self.tools[func.__name__] = func
            return func

        return decorator

    def run(self, *args, **kwargs):
        raise RuntimeError("Install mcp[cli]>=1.27,<2 to run the MCP server")


mcp = FastMCP("Competitive Intelligence Agent Tools") if FastMCP else _ToolRegistry(
    "Competitive Intelligence Agent Tools"
)


@mcp.tool()
def analyze_saved_articles(
    config_path: str | None = None,
    input_path: str | None = None,
    output_dir: str | None = None,
    slug: str | None = None,
    dashboard: bool = False,
) -> dict[str, Any]:
    """Analyze saved article JSON and write brief/event exports for agents."""
    provider = providers.LocalIntelProvider()
    return provider.analyze_saved_articles(
        config_path=config_path,
        input_path=input_path,
        output_dir=output_dir,
        slug=slug,
        dashboard=dashboard,
    )


@mcp.tool()
def search_events(
    mode: str = "local",
    query: str | None = None,
    competitor: str | None = None,
    event_type: str | None = None,
    significance: str | None = None,
    limit: int = 20,
    config_path: str | None = None,
    input_path: str | None = None,
    events_path: str | None = None,
) -> dict[str, Any]:
    """Search competitive events from local sample data or CocoIndex/Postgres."""
    provider = providers.get_provider(mode)
    if mode == "cocoindex":
        return provider.search_events(
            query=query,
            competitor=competitor,
            event_type=event_type,
            significance=significance,
            limit=limit,
        )
    return provider.search_events(
        query=query,
        competitor=competitor,
        event_type=event_type,
        significance=significance,
        limit=limit,
        config_path=config_path,
        input_path=input_path,
        events_path=events_path,
    )


@mcp.tool()
def get_trending_competitors(
    mode: str = "local",
    days: int = 7,
    limit: int = 10,
    config_path: str | None = None,
    input_path: str | None = None,
    events_path: str | None = None,
) -> dict[str, Any]:
    """Rank competitors by current intelligence activity."""
    provider = providers.get_provider(mode)
    if mode == "cocoindex":
        return provider.get_trending_competitors(days=days, limit=limit)
    return provider.get_trending_competitors(
        limit=limit,
        config_path=config_path,
        input_path=input_path,
        events_path=events_path,
    )


@mcp.tool()
def create_brief(
    mode: str = "local",
    config_path: str | None = None,
    input_path: str | None = None,
    events_path: str | None = None,
    output_dir: str | None = None,
    slug: str | None = None,
    limit: int = 200,
) -> dict[str, Any]:
    """Create a Markdown intelligence brief for an agent or analyst."""
    provider = providers.get_provider(mode)
    if mode == "cocoindex":
        return provider.create_brief(
            config_path=config_path,
            output_dir=output_dir,
            slug=slug,
            limit=limit,
        )
    return provider.create_brief(
        config_path=config_path,
        input_path=input_path,
        events_path=events_path,
        output_dir=output_dir,
        slug=slug,
    )


@mcp.tool()
def create_dashboard(
    mode: str = "local",
    config_path: str | None = None,
    input_path: str | None = None,
    events_path: str | None = None,
    output_dir: str | None = None,
    slug: str | None = None,
    limit: int = 200,
) -> dict[str, Any]:
    """Create a static HTML dashboard from competitive intelligence events."""
    provider = providers.get_provider(mode)
    if mode == "cocoindex":
        return provider.create_dashboard(
            config_path=config_path,
            output_dir=output_dir,
            slug=slug,
            limit=limit,
        )
    return provider.create_dashboard(
        config_path=config_path,
        input_path=input_path,
        events_path=events_path,
        output_dir=output_dir,
        slug=slug,
    )


@mcp.tool()
def run_cocoindex_update(live: bool = False, watch: bool = False, force: bool = True) -> dict[str, Any]:
    """Run the live CocoIndex update path when explicitly enabled."""
    if not live:
        return {
            "ok": False,
            "mode": "cocoindex",
            "message": "Set live=true to run CocoIndex because this can call APIs and write Postgres.",
        }

    missing = [
        key
        for key in ("COCOINDEX_DATABASE_URL", "TAVILY_API_KEY", "OPENAI_API_KEY")
        if not os.getenv(key)
    ]
    if missing:
        return {
            "ok": False,
            "mode": "cocoindex",
            "missing_env": missing,
            "message": "Live CocoIndex mode requires database and API credentials.",
        }

    cocoindex_bin = Path(sys.executable).with_name("cocoindex")
    command = [str(cocoindex_bin) if cocoindex_bin.exists() else "cocoindex", "update"]
    if watch:
        command.extend(["-L", "main.py"])
    else:
        command.append("main")
        if force:
            command.append("-f")

    completed = subprocess.run(command, capture_output=True, text=True, timeout=600)
    return {
        "ok": completed.returncode == 0,
        "mode": "cocoindex",
        "command": command,
        "returncode": completed.returncode,
        "stdout": completed.stdout[-4000:],
        "stderr": completed.stderr[-4000:],
    }


if __name__ == "__main__":
    mcp.run()
