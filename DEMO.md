# Agent-First CocoIndex Demo

This demo shows competitive intelligence as an agent tool system. The default
path is sample-first, so it works without Tavily, OpenRouter, Postgres, or
CocoIndex credentials. The live path keeps CocoIndex visible as the ingestion
and indexing backbone.

## Architecture

```text
Tavily Search -> CocoIndex Flow -> Postgres Tables -> MCP Tools -> Agent
                         |
                         v
              Sample JSON -> Local Analyzer -> Reports/Dashboard
```

## Demo Story

1. An agent asks what competitors are doing.
2. The MCP server exposes tools for analysis, event search, trends, briefs, and dashboards.
3. In sample mode, tools use `watchlist.json` and `data/sample_articles.json`.
4. In live mode, CocoIndex populates Postgres tables and the same tools query those tables.

## Sample-First Demo

Install dependencies:

```bash
pip install -e .
```

Run the local analyst workflow:

```bash
python3 local_intel.py --dashboard --slug demo
```

Run the deterministic agent transcript:

```bash
python3 agent_demo.py --slug demo-agent
```

This creates `reports/demo-agent-transcript.md` plus generated brief and
dashboard artifacts. It is the fastest way to show "agent asks -> tool calls ->
brief/dashboard" without needing a separate MCP client.

Start the MCP server:

```bash
python3 mcp_server.py
```

Example agent prompts:

- "Analyze the saved articles and create a dashboard."
- "Search events mentioning enterprise customers."
- "Which competitors are trending in the current sample?"
- "Create a board-ready competitive intelligence brief."

Direct smoke check without an MCP client:

```bash
python3 -m unittest test_local_intel.py
```

## MCP Client Config

Use `mcp-config.example.json` as a template for MCP-capable clients. Replace
`/ABSOLUTE/PATH/TO/competitive-intelligence` with this repo's absolute path.

For this machine, the command shape is:

```json
{
  "mcpServers": {
    "competitive-intelligence": {
      "command": "/Users/ln-mini/Documents/Medley projects/competitive-intelligence/.venv/bin/python",
      "args": [
        "/Users/ln-mini/Documents/Medley projects/competitive-intelligence/mcp_server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
```

## Live CocoIndex Demo

Configure `.env`:

```env
COCOINDEX_DATABASE_URL=postgresql://user:password@host:5432/competitive_intel
DATABASE_URL=postgresql://user:password@host:5432/competitive_intel
OPENAI_API_KEY=sk-or-v1-...
TAVILY_API_KEY=tvly-...
COMPETITORS=OpenAI,Anthropic,Google AI
MAX_RESULTS_PER_COMPETITOR=10
EVENT_QUERY=(funding OR partnership OR product launch OR acquisition OR executive hire)
```

Populate the CocoIndex tables:

```bash
cocoindex update main -f
```

Then ask an agent to call:

- `search_events(mode="cocoindex", competitor="Anthropic")`
- `get_trending_competitors(mode="cocoindex", days=7)`
- `create_brief(mode="cocoindex")`
- `create_dashboard(mode="cocoindex")`
- `run_cocoindex_update(live=true)`

`run_cocoindex_update` refuses to run unless `live=true` is passed and all live
credentials are present.
