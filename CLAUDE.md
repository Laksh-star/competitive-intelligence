# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Competitive Intelligence Monitor** - A CocoIndex pipeline that tracks competitor mentions across the web using Tavily AI Search. Uses DeepSeek LLM-powered extraction to identify product launches, partnerships, funding rounds, key hires, and strategic moves.

## Development Commands

### Setup
```bash
pip install -e .                    # Install dependencies
cp .env.example .env                # Create environment config
# Edit .env with your API keys and database URL
```

### Running the Pipeline
```bash
cocoindex update main -f            # One-time sync (force refresh)
cocoindex update -L main.py         # Live mode (continuous monitoring)
```

### Testing
```bash
python3 test_results.py             # Run comprehensive tests
```

See [TESTING.md](TESTING.md) for detailed testing procedures.

### Database Setup
Requires PostgreSQL. The pipeline auto-creates tables:
- `intel_articles` - Raw news articles and blog posts
- `intel_events` - Extracted competitive intelligence events

## Architecture

### Data Flow
```
Sources → LLM Extraction → Dual Indexing → Query Handlers
```

1. **Sources** ([main.py:49-99](main.py#L49-L99))
   - `TavilySearchSource` - AI-native web search optimized for agents
   - Searches with query: `"{competitor} AND (funding OR partnership OR product launch OR acquisition OR executive hire)"`
   - Returns clean, full article content (not just snippets)
   - Configurable via `.env`: `COMPETITORS`, `REFRESH_INTERVAL_SECONDS`, `SEARCH_DAYS_BACK`

2. **LLM Extraction** ([main.py:136-164](main.py#L136-L164))
   - `ExtractByLlm` processes article content
   - Outputs structured `CompetitiveEvent` objects with:
     - `event_type`: product_launch, partnership, funding, key_hire, acquisition
     - `competitor`: Primary company involved
     - `significance`: high, medium, low (market impact)
     - `related_companies`: Partners, investors, etc.

3. **Dual Indexing** ([main.py:172-191](main.py#L172-L191))
   - Articles collector: Raw content with primary key = URL
   - Events collector: Extracted events with composite key
   - Both exported to PostgreSQL via `PostgresExporter`

4. **Query Handlers** ([main.py:203-327](main.py#L203-L327))
   - `search_by_competitor()` - Filter by company and event type
   - `get_high_significance_events()` - High-impact events from recent days
   - `get_trending_competitors()` - Weighted ranking by news volume
   - `search_partnerships()` - Partnership announcements only

### Key Design Patterns

**Incremental Processing**: CocoIndex tracks what's been processed, only syncing new content.

**Weighted Scoring**: High-significance events = 3 points, medium = 2, low = 1 for trending analysis.

**Relational Joins**: Queries join `intel_events` with `intel_articles` to show source context.

## Configuration

Environment variables (`.env`):
- `DATABASE_URL` - PostgreSQL connection string (required)
- `DEEPSEEK_API_KEY` - For LLM extraction (required, ~$0.14 per 1M tokens)
- `TAVILY_API_KEY` - For AI-powered web search (required, free tier: 1K searches/month)
- `COMPETITORS` - Comma-separated company list (default: OpenAI,Anthropic,Google AI,Meta AI)
- `REFRESH_INTERVAL_SECONDS` - Source polling frequency (default: 3600)
- `SEARCH_DAYS_BACK` - Lookback period for searches (default: 7)

## Adding New Sources

To add a data source, create a class extending `SourceSpec` with:
1. Configuration fields (API keys, URLs, etc.)
2. `async def fetch()` returning `list[dict[str, Any]]`
3. Each dict must have: `id`, `title`, `content`, `url`, `source`, `published_at`

Example:
```python
class TwitterSource(SourceSpec):
    bearer_token: str
    search_query: str

    async def fetch(self) -> list[dict[str, Any]]:
        # Implement Twitter API calls
        pass

# Then add to flow
flow.add_source(
    TwitterSource(bearer_token=token, search_query="AI news"),
    refresh_interval_seconds=1800,
)
```

## Extending Event Types

To track different competitive insights:
1. Modify `CompetitiveEvent` class ([main.py:17-33](main.py#L17-L33)) to add fields
2. Update LLM instruction ([main.py:144-165](main.py#L144-L165)) to extract new data
3. Add query handlers for new event types
4. Database schema auto-updates on next run

## Dependencies

- **cocoindex** (≥0.3.9) - Core indexing framework
- **tavily-python** (≥0.3.0) - AI-native search API
- **psycopg[binary,pool]** - PostgreSQL adapter

## Why Tavily?

Tavily is an AI-native search engine designed for AI agents:
- **Clean content** - Returns full article text, not snippets
- **Relevance scoring** - Built-in ranking for quality results
- **Free tier** - 1,000 searches/month (sufficient for 5-10 competitors hourly)
- **No scraping** - Handles extraction and cleaning automatically
- **Advanced mode** - Deeper crawling for comprehensive intelligence
