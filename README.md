# Competitive Intelligence Monitor

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![CocoIndex](https://img.shields.io/badge/CocoIndex-0.3.9+-green.svg)](https://cocoindex.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Track competitor mentions across the web using AI-powered search and LLM extraction. Automatically monitors competitors, extracts competitive intelligence events, and stores structured data in PostgreSQL for analysis.

## What This Does

This pipeline automatically:
- **Searches** the web using Tavily AI (AI-native search engine optimized for agents)
- **Extracts** competitive intelligence events using DeepSeek LLM analysis:
  - Product launches and feature releases
  - Partnerships and collaborations
  - Funding rounds and financial news
  - Key executive hires/departures
  - Acquisitions and mergers
- **Indexes** both raw articles and extracted events in PostgreSQL
- **Enables queries** like:
  - "What has OpenAI been doing recently?"
  - "Which competitors are making the most news?"
  - "Find all partnership announcements"
  - "What are the most significant competitive moves this week?"

## Prerequisites

1. **PostgreSQL Database** - Choose one option:
   - Local PostgreSQL installation
   - Cloud PostgreSQL (AWS RDS, Google Cloud SQL, Azure Database, etc.)
2. **Python 3.11+** - Required for CocoIndex
3. **API Keys** (required):
   - Tavily API key from [tavily.com](https://tavily.com) (free tier: 1,000 searches/month)
   - OpenRouter API key for LLM extraction via GPT-4o-mini (cost-effective: ~$0.15 per 1M input tokens, ~$0.60 per 1M output tokens)

## Setup

### 1. Database Setup

Choose **Option A** (Local) or **Option B** (Cloud):

#### Option A: Local PostgreSQL

```bash
# Install PostgreSQL (macOS)
brew install postgresql@15
brew services start postgresql@15

# Create database
createdb competitive_intel

# Your connection string:
# postgresql://username:password@localhost:5432/competitive_intel
```

#### Option B: Cloud PostgreSQL (Google Cloud SQL / AWS RDS / Azure)

**Google Cloud SQL Example**:
1. Create PostgreSQL instance in [Google Cloud Console](https://console.cloud.google.com/sql)
2. Note the **Public IP address** (e.g., `34.71.19.121`)
3. Create database: `postgres` (or custom name)
4. Set password for `postgres` user
5. Allow your IP in Cloud SQL connections

**Connection string format**:
```
postgresql://postgres:YOUR_PASSWORD@PUBLIC_IP:5432/postgres
```

💡 **Special characters in password?** URL-encode them:
- `@` → `%40`
- `#` → `%23`
- `&` → `%26`

Example: Password `Lucas@123` becomes `Lucas%40123`

**AWS RDS / Azure**: Same format, just use your cloud database endpoint instead of public IP.

### 2. Install Dependencies

```bash
pip install -e .
```

### 3. Configure Environment

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` and set:
- `DATABASE_URL` - Your PostgreSQL connection string (from Step 1)
- `COCOINDEX_DATABASE_URL` - Same as DATABASE_URL (required by CocoIndex)
- `OPENAI_API_KEY` - OpenRouter API key from [openrouter.ai](https://openrouter.ai)
- `TAVILY_API_KEY` - Tavily API key from [tavily.com](https://tavily.com)
- `COMPETITORS` - Comma-separated list of companies to track
- `SEARCH_DAYS_BACK` - How many days back to search (default: 7)

**Example (Local PostgreSQL)**:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/competitive_intel
COCOINDEX_DATABASE_URL=postgresql://user:password@localhost:5432/competitive_intel
OPENAI_API_KEY=sk-or-v1-...
TAVILY_API_KEY=tvly-...
COMPETITORS=OpenAI,Anthropic,Google AI,Meta AI,Mistral AI
REFRESH_INTERVAL_SECONDS=3600
SEARCH_DAYS_BACK=7
```

**Example (Google Cloud SQL)**:
```env
DATABASE_URL=postgresql://postgres:Lucas%40123@34.71.19.121:5432/postgres
COCOINDEX_DATABASE_URL=postgresql://postgres:Lucas%40123@34.71.19.121:5432/postgres
OPENAI_API_KEY=sk-or-v1-...
TAVILY_API_KEY=tvly-...
COMPETITORS=Apple,Google,Microsoft,Amazon,Meta
REFRESH_INTERVAL_SECONDS=3600
SEARCH_DAYS_BACK=7
```

### 3. Run the Pipeline

**Option A: Interactive Mode (Recommended for first-time users)**

Run the interactive CLI that prompts you for what to monitor:
```bash
python3 run_interactive.py
```

This will ask you:
- Which companies to track
- What types of events to focus on (product launches, partnerships, funding, etc.)
- Time range to search (default: 7 days)
- How many articles per company (default: 10)
- One-time sync or continuous monitoring

See [INTERACTIVE_DEMO.md](INTERACTIVE_DEMO.md) for example sessions and use cases.

**Option B: Direct Mode (For automated/scheduled runs)**

Initial sync:
```bash
cocoindex update main -f
```

Continuous monitoring (live mode):
```bash
cocoindex update -L main.py
```

### 4. Verify It's Working

Run the test script to verify data extraction:
```bash
python3 test_results.py
```

### 5. Generate Reports

Save extracted intelligence to a text file:
```bash
python3 generate_report.py
```

This creates `intelligence_report_YYYY-MM-DD_HH-MM-SS.txt` with:
- Summary statistics
- Event type distribution
- Competitor rankings
- Detailed intelligence by company

See [USAGE_GUIDE.md](USAGE_GUIDE.md) for more commands and [TESTING.md](TESTING.md) for comprehensive testing.

## Query Examples

Once the pipeline is running, you can query your competitive intelligence:

### Find recent activity by competitor
```
"What has Anthropic been doing recently?"
→ Uses: search_by_competitor(competitor="Anthropic")
```

### Filter by event type
```
"Find funding news about OpenAI"
→ Uses: search_by_competitor(competitor="OpenAI", event_type="funding")
```

### Get high-impact events
```
"What are the most significant competitive moves this week?"
→ Uses: get_high_significance_events(days=7)
```

### Trending analysis
```
"Which AI companies are making the most news?"
→ Uses: get_trending_competitors(days=7)
```

### Partnership tracking
```
"What partnerships has Google AI announced?"
→ Uses: search_partnerships(partner="Google AI")
```

## Data Model

### Articles Table (`intel_articles`)
Stores raw articles from news sources and blogs:
- `id` - Article URL (primary key)
- `title` - Article headline
- `content` - Article text/summary
- `url` - Source URL
- `source` - Publisher name
- `published_at` - Publication timestamp

### Events Table (`intel_events`)
Stores extracted competitive intelligence events:
- `article_id` - Reference to source article
- `event_type` - Category: product_launch, partnership, funding, key_hire, acquisition
- `competitor` - Primary company involved
- `description` - Event summary
- `significance` - Impact rating: high, medium, low
- `related_companies` - Other companies mentioned (partners, investors, etc.)

## Customization

### Adjust Search Parameters

Edit [main.py](main.py) TavilySearchSource configuration:

```python
flow.add_source(
    TavilySearchSource(
        api_key=tavily_api_key,
        competitor=competitor.strip(),
        days_back=7,          # Adjust lookback period
        max_results=20,       # Increase results per competitor
    ),
    refresh_interval_seconds=1800,  # Check every 30 minutes
)
```

### Customize Search Queries

Modify the search query in TavilySearchSource (line ~65):

```python
search_query = (
    f"{self.competitor} AND "
    f"(funding OR partnership OR product launch OR acquisition OR executive hire OR regulatory)"
)
```

### Adjust Competitors List

Edit `.env` to track different companies:
```env
COMPETITORS=Company1,Company2,Company3
```

### Modify Event Types

Edit the `CompetitiveEvent` model in [main.py](main.py) to track different event categories.

### Change Refresh Frequency

Adjust `REFRESH_INTERVAL_SECONDS` in `.env`:
- `3600` = hourly (default)
- `1800` = every 30 minutes
- `86400` = daily

## Debugging

CocoIndex provides **CocoInsight** (free beta) for visualizing data lineage and debugging:
- See how data flows through the pipeline
- Inspect LLM extraction results
- Troubleshoot indexing issues

Visit the CocoIndex documentation for CocoInsight setup.

## Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                      COMPETITIVE INTELLIGENCE MONITOR                │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│   Tavily AI  │──────▶│  CocoIndex   │──────▶│  PostgreSQL  │
│    Search    │       │   Pipeline   │       │   Database   │
└──────────────┘       └──────────────┘       └──────────────┘
      │                       │                       │
      │                       │                       │
      ▼                       ▼                       ▼
   Articles              Extraction              Intelligence
  (web data)           (GPT-4o-mini)            (structured)
```

### Data Flow

1. **Data Ingestion** (Tavily AI Search)
   - Searches web for competitor mentions
   - Filters by time range (configurable: 1-30 days)
   - Returns clean, full article content
   - **Output**: Raw articles with metadata

2. **LLM Extraction** (GPT-4o-mini via OpenRouter)
   - Processes article content through LLM
   - Extracts structured `CompetitiveEvent` objects
   - Classifies: product launches, partnerships, funding, hires, acquisitions
   - Assigns significance: high, medium, low
   - **Output**: Structured intelligence events

3. **Dual Indexing** (CocoIndex + PostgreSQL)
   - **Articles Table**: Raw content, URLs, sources, timestamps
   - **Events Table**: Extracted intelligence with relationships
   - Incremental updates (only new data processed)
   - **Output**: Queryable database

4. **Query Layer** (SQL + Python)
   - Search by competitor
   - Filter by event type
   - Rank by significance
   - Trend analysis
   - **Output**: Intelligence reports

### Key Features

- **Incremental Processing**: CocoIndex tracks processed articles, avoiding duplicate work
- **Dual Indexing**: Both raw content and extracted entities for maximum flexibility
- **Weighted Scoring**: High-significance events = 3 points, medium = 2, low = 1
- **Relational Queries**: Join articles with events for full context
- **Real-time Monitoring**: Continuous mode refreshes every hour (configurable)

## Why Tavily?

Tavily is an **AI-native search engine** designed specifically for AI agents and LLMs:

- **Clean content extraction** - Returns full article text, not just snippets
- **Relevance scoring** - Built-in ranking for competitive intelligence
- **No scraping needed** - Handles content extraction and cleaning
- **Free tier** - 1,000 searches/month (enough for hourly monitoring of 5-10 competitors)
- **Advanced search** - Deeper crawling for comprehensive results

## Next Steps

- **Refine search queries** - Add industry-specific keywords or event types
- **Add custom event types** - Track regulation changes, PR crises, etc.
- **Sentiment analysis** - Classify news as positive/negative/neutral
- **Alert system** - Get notified of high-significance events via email/Slack
- **Dashboard** - Build a web UI for exploring competitive intelligence
- **Export reports** - Generate weekly/monthly competitor summary reports

## Project Structure

```
competitive-intelligence/
├── main.py                    # Core pipeline definition
├── run_interactive.py         # Interactive CLI for easy setup
├── test_results.py           # Validation and testing script
├── generate_report.py        # Report generation tool
├── clear_and_run.py          # Fresh data testing utility
├── pyproject.toml            # Project dependencies
├── .env.example              # Environment template
├── .env                      # Your credentials (git-ignored)
│
├── README.md                 # This file
├── QUICKSTART.md            # 3-minute setup guide
├── USAGE_GUIDE.md           # Complete command reference
├── TESTING.md               # Testing procedures
├── INTERACTIVE_DEMO.md      # Interactive mode examples
├── CLAUDE.md                # Developer guidance
├── CONTRIBUTING.md          # Contribution guidelines
└── LICENSE                  # MIT License
```

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

- Report bugs via GitHub Issues
- Submit feature requests
- Improve documentation
- Add new data sources
- Create new query handlers

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [CocoIndex](https://cocoindex.io) - Modern data pipeline framework
- Powered by [Tavily AI Search](https://tavily.com) - AI-native search engine
- LLM extraction via [OpenRouter](https://openrouter.ai) - Multi-model API gateway

## Support

- **Documentation**: [Full docs](README.md) | [Quick Start](QUICKSTART.md) | [Usage Guide](USAGE_GUIDE.md)
- **Issues**: Report bugs or request features via GitHub Issues
- **CocoIndex**: [cocoindex.io](https://cocoindex.io)
- **Examples**: [github.com/cocoindex-io/cocoindex](https://github.com/cocoindex-io/cocoindex)

---

**Built with ❤️ using CocoIndex** | Track your competitors automatically
