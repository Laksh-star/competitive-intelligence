"""
Competitive Intelligence Monitor using CocoIndex

Tracks competitor mentions across the web using Tavily AI Search.
Extracts competitive events using DeepSeek LLM: product launches, partnerships,
funding rounds, key hires, and strategic moves.
"""

import cocoindex
import os
import functools
import re
from psycopg_pool import ConnectionPool
from datetime import timedelta, datetime
from typing import Any, AsyncIterator, NamedTuple
import dataclasses

from tavily import TavilyClient
from cocoindex.op import (
    NON_EXISTENCE,
    SourceSpec,
    NO_ORDINAL,
    source_connector,
    PartialSourceRow,
    PartialSourceRowData,
)


# ============================================================================
# Data Models
# ============================================================================

@dataclasses.dataclass
class CompetitiveEvent:
    """A competitive intelligence event extracted from text.

    Examples:
    - Product Launch: "OpenAI released GPT-5 with multimodal capabilities"
    - Partnership: "Anthropic partnered with Google Cloud for enterprise AI"
    - Funding: "Mistral AI raised $400M Series B led by Andreessen Horowitz"
    - Key Hire: "Former Meta AI director joined Cohere as Chief Scientist"
    - Strategic Move: "Microsoft acquired AI startup Inflection for $650M"
    """

    event_type: str  # "product_launch", "partnership", "funding", "key_hire", "acquisition", "other"
    competitor: str  # Company name (e.g., "OpenAI", "Anthropic", "Google AI")
    description: str  # Brief description of the event
    significance: str  # "high", "medium", "low" - based on market impact
    related_companies: list[str]  # Other companies mentioned (partners, acquirers, etc.)


class _ArticleKey(NamedTuple):
    """Row key type for articles."""
    url: str


@dataclasses.dataclass
class _Article:
    """Article value type."""
    title: str
    content: str
    source: str
    published_at: datetime
    score: float


# ============================================================================
# Data Sources
# ============================================================================

class TavilySearchSource(SourceSpec):
    """Fetches competitive intelligence using Tavily AI Search API."""
    competitor: str
    days_back: int = 7
    max_results: int = 10
    query_terms: str = "(funding OR partnership OR product launch OR acquisition OR executive hire)"


@source_connector(
    spec_cls=TavilySearchSource,
    key_type=_ArticleKey,
    value_type=_Article,
)
class TavilySearchConnector:
    """Custom source connector for Tavily AI Search."""

    _spec: TavilySearchSource
    _api_key: str

    def __init__(self, spec: TavilySearchSource, api_key: str):
        self._spec = spec
        self._api_key = api_key

    @staticmethod
    async def create(spec: TavilySearchSource) -> "TavilySearchConnector":
        """Create a Tavily connector from the spec."""
        api_key = os.getenv("TAVILY_API_KEY", "")
        if not api_key:
            raise ValueError("TAVILY_API_KEY environment variable is required")
        return TavilySearchConnector(spec, api_key)

    async def list(
        self,
    ) -> AsyncIterator[PartialSourceRow[_ArticleKey, _Article]]:
        """List articles from Tavily search."""
        # Construct search query focused on competitive intelligence events
        search_query = (
            f"{self._spec.competitor} AND "
            f"{self._spec.query_terms}"
        )

        # Initialize Tavily client
        client = TavilyClient(api_key=self._api_key)

        # Perform search with advanced depth for better quality
        response = client.search(
            query=search_query,
            search_depth="advanced",
            max_results=self._spec.max_results,
            include_raw_content=True,
            include_domains=[],
            exclude_domains=[],
        )

        for result in response.get("results", []):
            url = result["url"]
            pub_date = result.get("published_date")
            ordinal = (
                int(datetime.fromisoformat(pub_date).timestamp())
                if pub_date
                else NO_ORDINAL
            )

            yield PartialSourceRow(
                key=_ArticleKey(url=url),
                data=PartialSourceRowData(ordinal=ordinal),
            )

    async def get_value(
        self, key: _ArticleKey
    ) -> PartialSourceRowData[_Article]:
        """Get a specific article by URL."""
        # Re-search to get the article (Tavily doesn't have a get-by-URL API)
        search_query = f"{self._spec.competitor} AND {self._spec.query_terms}"

        client = TavilyClient(api_key=self._api_key)
        response = client.search(
            query=search_query,
            search_depth="advanced",
            max_results=self._spec.max_results,
            include_raw_content=True,
        )

        for result in response.get("results", []):
            if result["url"] == key.url:
                pub_date = result.get("published_date")
                return PartialSourceRowData(
                    value=_Article(
                        title=result["title"],
                        content=result.get("raw_content", result.get("content", "")),
                        source=result.get("domain", "Unknown"),
                        published_at=datetime.fromisoformat(pub_date) if pub_date else datetime.now(),
                        score=result.get("score", 0.0),
                    )
                )

        return PartialSourceRowData(
            value=NON_EXISTENCE,
            ordinal=NO_ORDINAL,
            content_version_fp=None,
        )

    def provides_ordinal(self) -> bool:
        """Indicate that this source provides ordinal information."""
        return True


# ============================================================================
# Pipeline Definition
# ============================================================================

def _scope_field_name(prefix: str, value: str) -> str:
    """Build a CocoIndex-safe scope field name from user-provided text."""
    clean = re.sub(r"\W+", "_", value.strip())
    if not clean or clean[0].isdigit():
        clean = f"_{clean}"
    return f"{prefix}_{clean}"


@cocoindex.flow_def(name="CompetitiveIntelligence")
def competitive_intelligence_flow(
    flow_builder: cocoindex.FlowBuilder, data_scope: cocoindex.DataScope
) -> None:
    """Main pipeline for competitive intelligence monitoring."""

    # Environment configuration
    competitors = os.getenv("COMPETITORS", "OpenAI,Anthropic").split(",")
    refresh_interval = int(os.getenv("REFRESH_INTERVAL_SECONDS", "3600"))
    search_days_back = int(os.getenv("SEARCH_DAYS_BACK", "7"))
    max_results = int(os.getenv("MAX_RESULTS_PER_COMPETITOR", "10"))
    query_terms = os.getenv(
        "EVENT_QUERY",
        "(funding OR partnership OR product launch OR acquisition OR executive hire)",
    )

    # Add Tavily search source for each competitor
    for competitor in competitors:
        competitor_clean = competitor.strip()
        data_scope[_scope_field_name("articles", competitor_clean)] = flow_builder.add_source(
            TavilySearchSource(
                competitor=competitor_clean,
                days_back=search_days_back,
                max_results=max_results,
                query_terms=query_terms,
            ),
            refresh_interval=timedelta(seconds=refresh_interval),
        )

    articles_index = data_scope.add_collector()
    events_index = data_scope.add_collector()

    # Process each competitor's articles
    for competitor in competitors:
        competitor_clean = competitor.strip()
        articles = data_scope[_scope_field_name("articles", competitor_clean)]

        with articles.row() as article:
            # Extract competitive events from articles using GPT-4o-mini via OpenRouter
            article["events"] = article["content"].transform(
                cocoindex.functions.ExtractByLlm(
                    llm_spec=cocoindex.LlmSpec(
                        api_type=cocoindex.LlmApiType.OPENAI,
                        model="openai/gpt-4o-mini",
                        address="https://openrouter.ai/api/v1",
                    ),
                    output_type=list[CompetitiveEvent],
                    instruction=(
                        "Extract competitive intelligence events from this article. "
                        "Focus on: product launches, partnerships, funding rounds, key hires, "
                        "acquisitions, and other strategic moves. Return an empty list if no events found."
                    ),
                )
            )

            # Collect articles
            articles_index.collect(
                id=article["url"],
                title=article["title"],
                content=article["content"],
                url=article["url"],
                source=article["source"],
                published_at=article["published_at"],
                score=article["score"],
            )

            # Collect extracted events
            with article["events"].row() as event:
                events_index.collect(
                    article_id=article["url"],
                    event_type=event["event_type"],
                    competitor=event["competitor"],
                    description=event["description"],
                    significance=event["significance"],
                    related_companies=event["related_companies"],
                )

    # Export to PostgreSQL
    articles_index.export(
        "intel_articles",
        cocoindex.targets.Postgres(),
        primary_key_fields=["id"],
    )

    events_index.export(
        "intel_events",
        cocoindex.targets.Postgres(),
        primary_key_fields=["article_id", "event_type", "competitor", "description"],
    )


# ============================================================================
# Query Handlers
# ============================================================================

@functools.cache
def connection_pool() -> ConnectionPool:
    """Get a connection pool to the database."""
    return ConnectionPool(os.environ["COCOINDEX_DATABASE_URL"])


@competitive_intelligence_flow.query_handler()
def search_by_competitor(competitor: str, event_type: str | None = None, limit: int = 20) -> cocoindex.QueryOutput:
    """Find recent competitive intelligence about a specific competitor."""
    events_table = cocoindex.utils.get_target_default_name(
        competitive_intelligence_flow, "intel_events"
    )
    articles_table = cocoindex.utils.get_target_default_name(
        competitive_intelligence_flow, "intel_articles"
    )

    with connection_pool().connection() as conn:
        with conn.cursor() as cur:
            sql = f"""
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
                FROM {events_table} e
                JOIN {articles_table} a ON e.article_id = a.id
                WHERE LOWER(e.competitor) LIKE LOWER(%s)
            """
            params = [f"%{competitor}%"]

            if event_type:
                sql += " AND e.event_type = %s"
                params.append(event_type)

            sql += " ORDER BY a.published_at DESC LIMIT %s"
            params.append(limit)

            cur.execute(sql, params)

            results = []
            for row in cur.fetchall():
                results.append({
                    "competitor": row[0],
                    "event_type": row[1],
                    "description": row[2],
                    "significance": row[3],
                    "related_companies": row[4],
                    "article_title": row[5],
                    "url": row[6],
                    "source": row[7],
                    "published_at": row[8].isoformat() if row[8] else None,
                })

            return cocoindex.QueryOutput(results=results)


@competitive_intelligence_flow.query_handler()
def get_trending_competitors(days: int = 7) -> cocoindex.QueryOutput:
    """Get competitors ranked by recent news volume and significance."""
    events_table = cocoindex.utils.get_target_default_name(
        competitive_intelligence_flow, "intel_events"
    )
    articles_table = cocoindex.utils.get_target_default_name(
        competitive_intelligence_flow, "intel_articles"
    )

    with connection_pool().connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT
                    e.competitor,
                    COUNT(*) as total_events,
                    SUM(CASE
                        WHEN e.significance = 'high' THEN 3
                        WHEN e.significance = 'medium' THEN 2
                        ELSE 1
                    END) as weighted_score,
                    COUNT(DISTINCT e.event_type) as event_types,
                    array_agg(DISTINCT e.event_type) as events
                FROM {events_table} e
                JOIN {articles_table} a ON e.article_id = a.id
                WHERE a.published_at >= NOW() - (%s * INTERVAL '1 day')
                GROUP BY e.competitor
                ORDER BY weighted_score DESC
                """,
                (days,),
            )

            results = []
            for row in cur.fetchall():
                results.append({
                    "competitor": row[0],
                    "total_events": row[1],
                    "weighted_score": row[2],
                    "event_types_count": row[3],
                    "event_types": row[4],
                })

            return cocoindex.QueryOutput(results=results)
