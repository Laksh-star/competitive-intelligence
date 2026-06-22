# Quick Start Guide

Get the agent-first competitive intelligence demo running in a few minutes.

## Prerequisites

- Python 3.11+ installed (`python3 --version`)
- No API keys are required for the default sample demo

PostgreSQL, Tavily, OpenRouter, and CocoIndex credentials are only needed for
the optional live mode.

## 1. Install

```bash
cd /path/to/competitive-intelligence
pip install -e .
```

## 2. Run the Sample Demo

```bash
python3 local_intel.py --dashboard --slug demo
```

This reads `watchlist.json` and `data/sample_articles.json`, then writes:

- `reports/brief-demo.md`
- `reports/intel-events-demo.json`
- `reports/intel-events-demo.csv`
- `reports/dashboard-demo.html`

## 3. Start the MCP Tool Server

```bash
python3 mcp_server.py
```

For MCP-capable clients, copy `mcp-config.example.json` and replace the
placeholder paths with this repo's absolute path.

Other agents can call tools such as:

- `analyze_saved_articles`
- `search_events`
- `get_trending_competitors`
- `create_brief`
- `create_dashboard`
- `run_cocoindex_update`

Example agent prompts:

- "Analyze the saved articles and create a dashboard."
- "Search events about enterprise customers."
- "Which competitors are trending?"
- "Create a board-ready intelligence brief."

## 4. Run the Deterministic Agent Demo

```bash
python3 agent_demo.py --slug demo-agent
```

This writes a transcript to `reports/demo-agent-transcript.md` and generates
brief/dashboard artifacts. Use this when you want a repeatable demo without a
separate MCP client.

## 5. Test Locally

```bash
python3 -m unittest test_local_intel.py
```

## Optional: Live CocoIndex Mode

Copy and edit the environment file:

```bash
cp .env.example .env
```

Set the required live variables:

```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
COCOINDEX_DATABASE_URL=postgresql://user:password@host:5432/dbname
OPENAI_API_KEY=sk-or-v1-your-openrouter-key
TAVILY_API_KEY=tvly-your-tavily-key
```

Populate CocoIndex/Postgres:

```bash
cocoindex update main -f
```

Then agents can call:

- `search_events(mode="cocoindex", competitor="OpenAI")`
- `get_trending_competitors(mode="cocoindex", days=7)`
- `run_cocoindex_update(live=true)`

## Troubleshooting

### "Import error: No module named 'mcp'"

Install the project dependencies:

```bash
pip install -e .
```

The unit tests can import `mcp_server.py` without the SDK, but running the real
MCP server requires `mcp[cli]>=1.27,<2`.

### "Live CocoIndex mode says credentials are missing"

`run_cocoindex_update` only runs when `live=true` and these variables are set:
`COCOINDEX_DATABASE_URL`, `OPENAI_API_KEY`, and `TAVILY_API_KEY`.

### "Database connection failed"

1. Verify PostgreSQL is running: `pg_isready` (if local)
2. Check connection string format in `.env`
3. Test connection: `psql "$DATABASE_URL"`
4. Check firewall allows port 5432

## Documentation

- **Full Setup**: [README.md](README.md)
- **Demo Script**: [DEMO.md](DEMO.md)
- **Testing**: [TESTING.md](TESTING.md)
- **Interactive Examples**: [INTERACTIVE_DEMO.md](INTERACTIVE_DEMO.md)
- **Architecture**: [CLAUDE.md](CLAUDE.md)

## Support

- CocoIndex Docs: [cocoindex.io](https://cocoindex.io)
- GitHub Issues: Report bugs or request features
- Examples: [github.com/cocoindex-io/cocoindex](https://github.com/cocoindex-io/cocoindex)

---

**Ready to start?** Run `python3 local_intel.py --dashboard --slug demo`.
