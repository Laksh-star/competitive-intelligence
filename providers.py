"""Data providers for local and CocoIndex-backed intelligence tools."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import local_intel


PROJECT_ROOT = Path(__file__).parent
DEFAULT_EVENTS_PATH = PROJECT_ROOT / "reports" / "intel-events-sample.json"


def _resolve(path: str | Path | None, default: Path) -> Path:
    return local_intel.resolve_path(path, default)


class LocalIntelProvider:
    """Provider backed by saved articles or previously generated local events."""

    mode = "local"

    def analyze_saved_articles(
        self,
        config_path: str | Path | None = None,
        input_path: str | Path | None = None,
        output_dir: str | Path | None = None,
        slug: str | None = None,
        dashboard: bool = False,
    ) -> dict[str, Any]:
        return local_intel.analyze_saved_articles(
            config_path=config_path,
            input_path=input_path,
            output_dir=output_dir,
            slug=slug,
            dashboard=dashboard,
        )

    def events(
        self,
        config_path: str | Path | None = None,
        input_path: str | Path | None = None,
        events_path: str | Path | None = None,
    ) -> list[local_intel.IntelEvent]:
        if events_path:
            return local_intel.load_events(_resolve(events_path, DEFAULT_EVENTS_PATH))
        config = local_intel.load_json(_resolve(config_path, local_intel.DEFAULT_CONFIG))
        articles = local_intel.load_articles(_resolve(input_path, local_intel.DEFAULT_INPUT))
        return local_intel.extract_events(config, articles)

    def search_events(
        self,
        query: str | None = None,
        competitor: str | None = None,
        event_type: str | None = None,
        significance: str | None = None,
        limit: int = 20,
        config_path: str | Path | None = None,
        input_path: str | Path | None = None,
        events_path: str | Path | None = None,
    ) -> dict[str, Any]:
        events = self.events(config_path=config_path, input_path=input_path, events_path=events_path)
        matches = local_intel.filter_events(
            events,
            query=query,
            competitor=competitor,
            event_type=event_type,
            significance=significance,
            limit=limit,
        )
        return {
            "mode": self.mode,
            "total_events": len(events),
            "matched_events": len(matches),
            "results": [local_intel.event_to_dict(event) for event in matches],
        }

    def get_trending_competitors(
        self,
        limit: int = 10,
        config_path: str | Path | None = None,
        input_path: str | Path | None = None,
        events_path: str | Path | None = None,
    ) -> dict[str, Any]:
        events = self.events(config_path=config_path, input_path=input_path, events_path=events_path)
        return {
            "mode": self.mode,
            "total_events": len(events),
            "results": local_intel.trending_competitors(events, limit=limit),
        }

    def create_brief(
        self,
        config_path: str | Path | None = None,
        input_path: str | Path | None = None,
        events_path: str | Path | None = None,
        output_dir: str | Path | None = None,
        slug: str | None = None,
    ) -> dict[str, Any]:
        config_file = _resolve(config_path, local_intel.DEFAULT_CONFIG)
        config = local_intel.load_json(config_file)
        events = self.events(config_path=config_file, input_path=input_path, events_path=events_path)
        report_dir = _resolve(output_dir, local_intel.DEFAULT_REPORT_DIR)
        run_slug = slug or local_intel.timestamp_slug()
        path = local_intel.write_markdown_report(config, events, report_dir, run_slug)
        return {
            "mode": self.mode,
            "event_count": len(events),
            "summary": local_intel.summarize(events),
            "path": str(path),
        }

    def create_dashboard(
        self,
        config_path: str | Path | None = None,
        input_path: str | Path | None = None,
        events_path: str | Path | None = None,
        output_dir: str | Path | None = None,
        slug: str | None = None,
    ) -> dict[str, Any]:
        config_file = _resolve(config_path, local_intel.DEFAULT_CONFIG)
        config = local_intel.load_json(config_file)
        events = self.events(config_path=config_file, input_path=input_path, events_path=events_path)
        report_dir = _resolve(output_dir, local_intel.DEFAULT_REPORT_DIR)
        run_slug = slug or local_intel.timestamp_slug()
        path = local_intel.write_html_dashboard(config, events, report_dir, run_slug)
        return {
            "mode": self.mode,
            "event_count": len(events),
            "summary": local_intel.summarize(events),
            "path": str(path),
        }


class CocoIndexPostgresProvider:
    """Provider backed by the PostgreSQL tables populated by the CocoIndex flow."""

    mode = "cocoindex"

    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.getenv("COCOINDEX_DATABASE_URL")
        if not self.database_url:
            raise ValueError("COCOINDEX_DATABASE_URL is required for mode='cocoindex'")

    def _connect(self):
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Install psycopg to use the CocoIndex provider") from exc
        return psycopg.connect(self.database_url)

    def events(self, limit: int = 200) -> list[local_intel.IntelEvent]:
        score_by_significance = {"high": 90, "medium": 65, "low": 35}
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        e.competitor,
                        e.event_type,
                        e.description,
                        e.significance,
                        a.title,
                        a.url,
                        a.source,
                        a.published_at
                    FROM competitiveintelligence__intel_events e
                    JOIN competitiveintelligence__intel_articles a ON e.article_id = a.id
                    ORDER BY a.published_at DESC
                    LIMIT %s
                    """,
                    (limit,),
                )
                rows = cur.fetchall()

        events = []
        for row in rows:
            significance = row[3] or "low"
            events.append(
                local_intel.IntelEvent(
                    competitor=row[0],
                    event_type=row[1],
                    description=row[2],
                    significance=significance,
                    title=row[4],
                    url=row[5],
                    source=row[6],
                    published_at=row[7].isoformat() if row[7] else "",
                    score=score_by_significance.get(significance, 35),
                    matched_terms=(),
                )
            )
        return events

    def search_events(
        self,
        query: str | None = None,
        competitor: str | None = None,
        event_type: str | None = None,
        significance: str | None = None,
        limit: int = 20,
    ) -> dict[str, Any]:
        where = []
        params: list[Any] = []
        if query:
            where.append("(LOWER(e.description) LIKE LOWER(%s) OR LOWER(a.title) LIKE LOWER(%s))")
            params.extend([f"%{query}%", f"%{query}%"])
        if competitor:
            where.append("LOWER(e.competitor) LIKE LOWER(%s)")
            params.append(f"%{competitor}%")
        if event_type:
            where.append("e.event_type = %s")
            params.append(event_type)
        if significance:
            where.append("e.significance = %s")
            params.append(significance)
        where_sql = "WHERE " + " AND ".join(where) if where else ""
        params.append(limit)

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT
                        e.competitor,
                        e.event_type,
                        e.description,
                        e.significance,
                        e.related_companies,
                        a.title,
                        a.url,
                        a.source,
                        a.published_at
                    FROM competitiveintelligence__intel_events e
                    JOIN competitiveintelligence__intel_articles a ON e.article_id = a.id
                    {where_sql}
                    ORDER BY a.published_at DESC
                    LIMIT %s
                    """,
                    params,
                )
                rows = cur.fetchall()

        results = []
        for row in rows:
            results.append(
                {
                    "competitor": row[0],
                    "event_type": row[1],
                    "description": row[2],
                    "significance": row[3],
                    "related_companies": row[4],
                    "title": row[5],
                    "url": row[6],
                    "source": row[7],
                    "published_at": row[8].isoformat() if row[8] else None,
                }
            )
        return {"mode": self.mode, "matched_events": len(results), "results": results}

    def get_trending_competitors(self, days: int = 7, limit: int = 10) -> dict[str, Any]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        e.competitor,
                        COUNT(*) as total_events,
                        SUM(CASE
                            WHEN e.significance = 'high' THEN 3
                            WHEN e.significance = 'medium' THEN 2
                            ELSE 1
                        END) as weighted_score,
                        COUNT(DISTINCT e.event_type) as event_types_count,
                        array_agg(DISTINCT e.event_type) as event_types
                    FROM competitiveintelligence__intel_events e
                    JOIN competitiveintelligence__intel_articles a ON e.article_id = a.id
                    WHERE a.published_at >= NOW() - (%s * INTERVAL '1 day')
                    GROUP BY e.competitor
                    ORDER BY weighted_score DESC
                    LIMIT %s
                    """,
                    (days, limit),
                )
                rows = cur.fetchall()

        results = [
            {
                "competitor": row[0],
                "total_events": row[1],
                "weighted_score": row[2],
                "event_types_count": row[3],
                "event_types": row[4],
            }
            for row in rows
        ]
        return {"mode": self.mode, "days": days, "results": results}

    def create_brief(
        self,
        config_path: str | Path | None = None,
        output_dir: str | Path | None = None,
        slug: str | None = None,
        limit: int = 200,
    ) -> dict[str, Any]:
        config_file = _resolve(config_path, local_intel.DEFAULT_CONFIG)
        config = local_intel.load_json(config_file)
        events = self.events(limit=limit)
        report_dir = _resolve(output_dir, local_intel.DEFAULT_REPORT_DIR)
        run_slug = slug or local_intel.timestamp_slug()
        path = local_intel.write_markdown_report(config, events, report_dir, run_slug)
        return {
            "mode": self.mode,
            "event_count": len(events),
            "summary": local_intel.summarize(events),
            "path": str(path),
        }

    def create_dashboard(
        self,
        config_path: str | Path | None = None,
        output_dir: str | Path | None = None,
        slug: str | None = None,
        limit: int = 200,
    ) -> dict[str, Any]:
        config_file = _resolve(config_path, local_intel.DEFAULT_CONFIG)
        config = local_intel.load_json(config_file)
        events = self.events(limit=limit)
        report_dir = _resolve(output_dir, local_intel.DEFAULT_REPORT_DIR)
        run_slug = slug or local_intel.timestamp_slug()
        path = local_intel.write_html_dashboard(config, events, report_dir, run_slug)
        return {
            "mode": self.mode,
            "event_count": len(events),
            "summary": local_intel.summarize(events),
            "path": str(path),
        }


def get_provider(mode: str = "local"):
    if mode == "local":
        return LocalIntelProvider()
    if mode == "cocoindex":
        return CocoIndexPostgresProvider()
    raise ValueError("mode must be 'local' or 'cocoindex'")
