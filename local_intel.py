#!/usr/bin/env python3
"""Local competitive-intelligence analysis without API or database setup.

This module turns saved article JSON into scored intelligence events, Markdown
briefs, JSON exports, CSV exports, and a static HTML dashboard. It is intended
as a fast analyst workspace alongside the production CocoIndex pipeline.
"""

from __future__ import annotations

import argparse
import csv
import dataclasses
import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).parent
DEFAULT_CONFIG = PROJECT_ROOT / "watchlist.json"
DEFAULT_INPUT = PROJECT_ROOT / "data" / "sample_articles.json"
DEFAULT_REPORT_DIR = Path(__file__).with_name("reports")


@dataclasses.dataclass(frozen=True)
class Competitor:
    name: str
    aliases: tuple[str, ...]
    priority: str = "medium"


@dataclasses.dataclass(frozen=True)
class Article:
    title: str
    source: str
    url: str
    published_at: str
    content: str


@dataclasses.dataclass(frozen=True)
class IntelEvent:
    competitor: str
    event_type: str
    title: str
    description: str
    source: str
    url: str
    published_at: str
    significance: str
    score: int
    matched_terms: tuple[str, ...]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def resolve_path(path: str | Path | None, default: Path) -> Path:
    if path is None:
        return default
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    return candidate


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def load_competitors(config: dict[str, Any]) -> list[Competitor]:
    competitors = []
    for item in config.get("competitors", []):
        competitors.append(
            Competitor(
                name=item["name"],
                aliases=tuple(item.get("aliases", [])),
                priority=item.get("priority", "medium"),
            )
        )
    return competitors


def load_articles(path: Path) -> list[Article]:
    raw_articles = load_json(path)
    articles = []
    for item in raw_articles:
        articles.append(
            Article(
                title=normalize_text(item.get("title", "Untitled")),
                source=normalize_text(item.get("source", "Unknown")),
                url=item.get("url", ""),
                published_at=item.get("published_at", ""),
                content=normalize_text(item.get("content", "")),
            )
        )
    return articles


def load_events(path: Path) -> list[IntelEvent]:
    raw = load_json(path)
    raw_events = raw.get("events", raw) if isinstance(raw, dict) else raw
    events = []
    for item in raw_events:
        events.append(
            IntelEvent(
                competitor=item.get("competitor", ""),
                event_type=item.get("event_type", "other"),
                title=item.get("title", item.get("article_title", "Untitled")),
                description=item.get("description", ""),
                source=item.get("source", ""),
                url=item.get("url", ""),
                published_at=item.get("published_at", ""),
                significance=item.get("significance", "low"),
                score=int(item.get("score", 0)),
                matched_terms=tuple(item.get("matched_terms", [])),
            )
        )
    return sorted(events, key=lambda event: (event.score, event.published_at), reverse=True)


def find_competitors(article: Article, competitors: list[Competitor]) -> list[Competitor]:
    text = f"{article.title} {article.content}".lower()
    matches = []
    for competitor in competitors:
        names = (competitor.name, *competitor.aliases)
        if any(name.lower() in text for name in names):
            matches.append(competitor)
    return matches


def matched_keywords(text: str, keywords: list[str]) -> tuple[str, ...]:
    lowered = text.lower()
    return tuple(keyword for keyword in keywords if keyword.lower() in lowered)


def classify_event(text: str, event_types: dict[str, list[str]]) -> tuple[str, tuple[str, ...]]:
    best_type = "other"
    best_terms: tuple[str, ...] = ()
    for event_type, keywords in event_types.items():
        terms = matched_keywords(text, keywords)
        if len(terms) > len(best_terms):
            best_type = event_type
            best_terms = terms
    return best_type, best_terms


def score_event(
    text: str,
    competitor: Competitor,
    event_type: str,
    significance_terms: dict[str, list[str]],
    matched_terms: tuple[str, ...],
) -> tuple[str, int]:
    score = 20
    if competitor.priority == "high":
        score += 20
    elif competitor.priority == "medium":
        score += 10

    event_weights = {
        "acquisition": 30,
        "funding": 25,
        "product_launch": 20,
        "partnership": 20,
        "customer_win": 18,
        "pricing": 15,
        "key_hire": 12,
        "regulatory": 18,
        "other": 5,
    }
    score += event_weights.get(event_type, 5)
    score += min(len(matched_terms) * 5, 20)

    lowered = text.lower()
    high_hits = matched_keywords(lowered, significance_terms.get("high", []))
    medium_hits = matched_keywords(lowered, significance_terms.get("medium", []))
    low_hits = matched_keywords(lowered, significance_terms.get("low", []))

    score += len(high_hits) * 12
    score += len(medium_hits) * 6
    score -= len(low_hits) * 4
    score = max(0, min(score, 100))

    if score >= 75:
        return "high", score
    if score >= 50:
        return "medium", score
    return "low", score


def extract_events(config: dict[str, Any], articles: list[Article]) -> list[IntelEvent]:
    competitors = load_competitors(config)
    event_types = config.get("event_types", {})
    significance_terms = config.get("significance_terms", {})
    events: list[IntelEvent] = []

    for article in articles:
        article_text = normalize_text(f"{article.title}. {article.content}")
        article_competitors = find_competitors(article, competitors)
        event_type, terms = classify_event(article_text, event_types)
        if not article_competitors or event_type == "other":
            continue

        for competitor in article_competitors:
            significance, score = score_event(
                article_text, competitor, event_type, significance_terms, terms
            )
            events.append(
                IntelEvent(
                    competitor=competitor.name,
                    event_type=event_type,
                    title=article.title,
                    description=article.content or article.title,
                    source=article.source,
                    url=article.url,
                    published_at=article.published_at,
                    significance=significance,
                    score=score,
                    matched_terms=terms,
                )
            )

    return sorted(events, key=lambda event: (event.score, event.published_at), reverse=True)


def timestamp_slug() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")


def event_to_dict(event: IntelEvent) -> dict[str, Any]:
    data = dataclasses.asdict(event)
    data["matched_terms"] = list(event.matched_terms)
    return data


def summarize(events: list[IntelEvent]) -> dict[str, Any]:
    by_competitor = Counter(event.competitor for event in events)
    by_type = Counter(event.event_type for event in events)
    by_significance = Counter(event.significance for event in events)
    return {
        "total_events": len(events),
        "by_competitor": dict(by_competitor),
        "by_type": dict(by_type),
        "by_significance": dict(by_significance),
        "top_events": [event_to_dict(event) for event in events[:5]],
    }


def filter_events(
    events: list[IntelEvent],
    query: str | None = None,
    competitor: str | None = None,
    event_type: str | None = None,
    significance: str | None = None,
    limit: int = 20,
) -> list[IntelEvent]:
    query_lower = query.lower().strip() if query else ""
    competitor_lower = competitor.lower().strip() if competitor else ""
    filtered = []
    for event in events:
        haystack = " ".join(
            [
                event.competitor,
                event.event_type,
                event.title,
                event.description,
                event.source,
                " ".join(event.matched_terms),
            ]
        ).lower()
        if query_lower and query_lower not in haystack:
            continue
        if competitor_lower and competitor_lower not in event.competitor.lower():
            continue
        if event_type and event.event_type != event_type:
            continue
        if significance and event.significance != significance:
            continue
        filtered.append(event)
    return filtered[: max(limit, 0)]


def trending_competitors(events: list[IntelEvent], limit: int = 10) -> list[dict[str, Any]]:
    grouped: dict[str, list[IntelEvent]] = defaultdict(list)
    for event in events:
        grouped[event.competitor].append(event)

    rows = []
    for competitor, competitor_events in grouped.items():
        weighted_score = sum(event.score for event in competitor_events)
        rows.append(
            {
                "competitor": competitor,
                "total_events": len(competitor_events),
                "weighted_score": weighted_score,
                "event_types_count": len({event.event_type for event in competitor_events}),
                "event_types": sorted({event.event_type for event in competitor_events}),
                "high_significance_events": sum(
                    1 for event in competitor_events if event.significance == "high"
                ),
            }
        )
    return sorted(rows, key=lambda row: row["weighted_score"], reverse=True)[: max(limit, 0)]


def analyze_saved_articles(
    config_path: str | Path | None = None,
    input_path: str | Path | None = None,
    output_dir: str | Path | None = None,
    slug: str | None = None,
    dashboard: bool = False,
) -> dict[str, Any]:
    config_file = resolve_path(config_path, DEFAULT_CONFIG)
    input_file = resolve_path(input_path, DEFAULT_INPUT)
    report_dir = resolve_path(output_dir, DEFAULT_REPORT_DIR)
    config = load_json(config_file)
    articles = load_articles(input_file)
    events = extract_events(config, articles)
    run_slug = slug or timestamp_slug()

    paths = {
        "brief": write_markdown_report(config, events, report_dir, run_slug),
        "events_json": write_json_report(events, report_dir, run_slug),
        "events_csv": write_csv_report(events, report_dir, run_slug),
    }
    if dashboard:
        paths["dashboard"] = write_html_dashboard(config, events, report_dir, run_slug)

    return {
        "mode": "local",
        "config_path": str(config_file),
        "input_path": str(input_file),
        "output_dir": str(report_dir),
        "slug": run_slug,
        "article_count": len(articles),
        "event_count": len(events),
        "summary": summarize(events),
        "paths": {name: str(path) for name, path in paths.items()},
    }


def write_json_report(events: list[IntelEvent], output_dir: Path, slug: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"intel-events-{slug}.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": summarize(events),
        "events": [event_to_dict(event) for event in events],
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def write_csv_report(events: list[IntelEvent], output_dir: Path, slug: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"intel-events-{slug}.csv"
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "competitor",
                "event_type",
                "significance",
                "score",
                "published_at",
                "source",
                "title",
                "url",
                "description",
                "matched_terms",
            ],
        )
        writer.writeheader()
        for event in events:
            row = event_to_dict(event)
            row["matched_terms"] = ", ".join(event.matched_terms)
            writer.writerow(row)
    return path


def write_markdown_report(
    config: dict[str, Any], events: list[IntelEvent], output_dir: Path, slug: str
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"brief-{slug}.md"
    summary = summarize(events)
    lines = [
        "# Competitive Intelligence Brief",
        "",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Industry: {config.get('industry', 'Unspecified')}",
        f"Analyst company: {config.get('analyst_company', 'Unspecified')}",
        "",
        "## Executive Snapshot",
        "",
        f"- Total events: {summary['total_events']}",
        f"- High significance: {summary['by_significance'].get('high', 0)}",
        f"- Medium significance: {summary['by_significance'].get('medium', 0)}",
        f"- Low significance: {summary['by_significance'].get('low', 0)}",
        "",
        "## Top Signals",
        "",
    ]

    if not events:
        lines.append("No events matched the current watchlist.")
    for event in events[:10]:
        lines.extend(
            [
                f"### {event.competitor}: {event.event_type.replace('_', ' ').title()}",
                "",
                f"- Significance: {event.significance} ({event.score}/100)",
                f"- Source: [{event.source}]({event.url})",
                f"- Published: {event.published_at or 'Unknown'}",
                f"- Matched terms: {', '.join(event.matched_terms) or 'None'}",
                f"- Signal: {event.description}",
                "",
            ]
        )

    grouped: dict[str, list[IntelEvent]] = defaultdict(list)
    for event in events:
        grouped[event.competitor].append(event)

    lines.extend(["## Competitor Breakdown", ""])
    for competitor, competitor_events in grouped.items():
        lines.append(f"### {competitor}")
        for event in competitor_events:
            lines.append(
                f"- {event.published_at or 'Unknown'} | {event.event_type} | "
                f"{event.significance} | {event.title}"
            )
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_html_dashboard(
    config: dict[str, Any], events: list[IntelEvent], output_dir: Path, slug: str
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"dashboard-{slug}.html"
    summary = summarize(events)
    event_cards = []
    for event in events:
        event_cards.append(
            f"""
            <article class="event" data-competitor="{html.escape(event.competitor)}"
              data-type="{html.escape(event.event_type)}" data-significance="{html.escape(event.significance)}">
              <div class="event__meta">
                <span>{html.escape(event.competitor)}</span>
                <span>{html.escape(event.event_type.replace("_", " ").title())}</span>
                <span class="badge badge--{html.escape(event.significance)}">{html.escape(event.significance)}</span>
                <strong>{event.score}/100</strong>
              </div>
              <h2>{html.escape(event.title)}</h2>
              <p>{html.escape(event.description)}</p>
              <footer>
                <span>{html.escape(event.published_at or "Unknown date")} · {html.escape(event.source)}</span>
                <a href="{html.escape(event.url)}">Source</a>
              </footer>
            </article>
            """
        )

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Competitive Intelligence Dashboard</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #17202a;
      --muted: #667085;
      --line: #d0d5dd;
      --surface: #ffffff;
      --page: #f6f8fb;
      --accent: #0f766e;
      --warn: #b54708;
      --danger: #b42318;
    }}
    body {{
      margin: 0;
      font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: var(--page);
      color: var(--ink);
    }}
    header {{
      background: #ffffff;
      border-bottom: 1px solid var(--line);
      padding: 28px max(24px, 6vw);
    }}
    h1 {{
      margin: 0 0 8px;
      font-size: 32px;
      line-height: 1.15;
    }}
    main {{
      padding: 24px max(24px, 6vw) 48px;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
      gap: 12px;
      margin-bottom: 20px;
    }}
    .stat, .event {{
      background: var(--surface);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}
    .stat strong {{
      display: block;
      font-size: 28px;
    }}
    .toolbar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin: 0 0 18px;
    }}
    input, select {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      min-height: 40px;
      background: #fff;
      color: var(--ink);
    }}
    input {{
      min-width: min(420px, 100%);
      flex: 1;
    }}
    .events {{
      display: grid;
      gap: 12px;
    }}
    .event__meta {{
      display: flex;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      color: var(--muted);
      font-size: 14px;
    }}
    .event h2 {{
      font-size: 18px;
      margin: 10px 0 8px;
    }}
    .event p {{
      margin: 0;
      color: #344054;
      line-height: 1.5;
    }}
    .event footer {{
      display: flex;
      justify-content: space-between;
      gap: 12px;
      margin-top: 14px;
      color: var(--muted);
      font-size: 14px;
    }}
    .badge {{
      border-radius: 999px;
      padding: 3px 8px;
      border: 1px solid var(--line);
      text-transform: capitalize;
    }}
    .badge--high {{ color: var(--danger); border-color: #fecdca; background: #fffbfa; }}
    .badge--medium {{ color: var(--warn); border-color: #fedf89; background: #fffcf5; }}
    .badge--low {{ color: var(--accent); border-color: #99f6e4; background: #f0fdfa; }}
    a {{ color: #175cd3; }}
  </style>
</head>
<body>
  <header>
    <h1>Competitive Intelligence Dashboard</h1>
    <div>{html.escape(config.get("industry", "Unspecified industry"))} · generated {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</div>
  </header>
  <main>
    <section class="stats">
      <div class="stat"><strong>{summary["total_events"]}</strong><span>Total events</span></div>
      <div class="stat"><strong>{summary["by_significance"].get("high", 0)}</strong><span>High significance</span></div>
      <div class="stat"><strong>{len(summary["by_competitor"])}</strong><span>Competitors active</span></div>
      <div class="stat"><strong>{len(summary["by_type"])}</strong><span>Event categories</span></div>
    </section>
    <section class="toolbar" aria-label="Filters">
      <input id="search" placeholder="Search events">
      <select id="significance">
        <option value="">All significance</option>
        <option value="high">High</option>
        <option value="medium">Medium</option>
        <option value="low">Low</option>
      </select>
    </section>
    <section class="events" id="events">
      {''.join(event_cards) or '<p>No events matched the current watchlist.</p>'}
    </section>
  </main>
  <script>
    const search = document.getElementById('search');
    const significance = document.getElementById('significance');
    const cards = [...document.querySelectorAll('.event')];
    function applyFilters() {{
      const query = search.value.toLowerCase();
      const level = significance.value;
      cards.forEach((card) => {{
        const text = card.innerText.toLowerCase();
        const show = (!query || text.includes(query)) &&
          (!level || card.dataset.significance === level);
        card.style.display = show ? '' : 'none';
      }});
    }}
    search.addEventListener('input', applyFilters);
    significance.addEventListener('change', applyFilters);
  </script>
</body>
</html>
"""
    path.write_text(html_doc, encoding="utf-8")
    return path


def run_analysis(args: argparse.Namespace) -> list[Path]:
    result = analyze_saved_articles(
        config_path=args.config,
        input_path=args.input,
        output_dir=args.output_dir,
        slug=args.slug,
        dashboard=args.dashboard,
    )
    print(
        f"Analyzed {result['article_count']} articles and found "
        f"{result['event_count']} events."
    )
    paths = [Path(path) for path in result["paths"].values()]
    for path in paths:
        print(f"Wrote {path}")
    return paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Analyze saved articles into a local competitive-intelligence brief."
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG, help="Watchlist JSON path")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Article JSON path")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_REPORT_DIR, help="Report directory")
    parser.add_argument("--slug", help="Optional output filename slug")
    parser.add_argument("--dashboard", action="store_true", help="Generate a static HTML dashboard")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    run_analysis(args)


if __name__ == "__main__":
    main()
