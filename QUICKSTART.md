# Quick Start Guide

Get your competitive intelligence pipeline running in 3 minutes!

## Prerequisites Check

Before starting, make sure you have:

- [ ] Python 3.11+ installed (`python3 --version`)
- [ ] PostgreSQL database (local or cloud)
- [ ] Tavily API key ([get free key](https://tavily.com))
- [ ] OpenRouter API key ([get free key](https://openrouter.ai))

## 1. Install (30 seconds)

```bash
cd /path/to/cocoindex
pip install -e .
```

## 2. Configure (60 seconds)

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

Set these **required** variables:
```env
DATABASE_URL=postgresql://user:password@host:5432/dbname
COCOINDEX_DATABASE_URL=postgresql://user:password@host:5432/dbname
OPENAI_API_KEY=sk-or-v1-your-openrouter-key
TAVILY_API_KEY=tvly-your-tavily-key
```

💡 **Tip**: If your password has special characters like `@`, URL-encode them:
- `@` → `%40`
- `#` → `%23`
- `&` → `%26`

## 3. Run (90 seconds)

### Interactive Mode (Recommended)

```bash
python3 run_interactive.py
```

Follow the prompts:
1. Enter companies (e.g., `OpenAI,Anthropic`)
2. Select event type (press `1` for all)
3. Press Enter for defaults
4. Type `y` to confirm and start

### Quick Mode (Use defaults)

```bash
cocoindex update main -f
```

## 4. View Results (10 seconds)

```bash
python3 test_results.py
```

You'll see:
- ✅ Articles indexed
- ✅ Events extracted
- ✅ Competitor breakdown
- ✅ Sample intelligence

## What's Next?

### Query Your Data

```python
from main import competitive_intelligence_flow

# Find OpenAI news
result = competitive_intelligence_flow.search_by_competitor("OpenAI", limit=10)
print(result.results)

# Get trending competitors
result = competitive_intelligence_flow.get_trending_competitors(days=7)
print(result.results)
```

### Continuous Monitoring

Run the pipeline every hour:
```bash
cocoindex update -L main.py
```

Or use cron (Linux/Mac):
```bash
# Edit crontab
crontab -e

# Add hourly job
0 * * * * cd /path/to/cocoindex && /usr/bin/python3 -m cocoindex update main
```

### Customize Configuration

Edit `.env` to change:
```env
COMPETITORS=YourCompetitor1,YourCompetitor2,YourCompetitor3
REFRESH_INTERVAL_SECONDS=1800  # 30 minutes
SEARCH_DAYS_BACK=14             # 2 weeks
```

## Troubleshooting

### "No events extracted"

**Problem**: Articles indexed but `intel_events` table is empty

**Solution**:
1. Check OpenRouter API key: `echo $OPENAI_API_KEY`
2. Verify key has credits at [openrouter.ai](https://openrouter.ai)
3. Check logs: `cocoindex update main -f 2>&1 | grep -i error`

### "Database connection failed"

**Problem**: Can't connect to PostgreSQL

**Solution**:
1. Verify PostgreSQL is running: `pg_isready` (if local)
2. Check connection string format in `.env`
3. Test connection: `psql "$DATABASE_URL"`
4. Check firewall allows port 5432

### "Tavily search returns 0 results"

**Problem**: No articles found

**Solution**:
1. Check Tavily API key: `echo $TAVILY_API_KEY`
2. Verify quota at [tavily.com/dashboard](https://tavily.com/dashboard)
3. Try broader search terms in `.env`

### "Import error: No module named 'cocoindex'"

**Problem**: Dependencies not installed

**Solution**:
```bash
pip install -e .
```

## Common Use Cases

### Track Your Competitors
```env
COMPETITORS=YourCompany,Competitor1,Competitor2
```

### Monitor Funding in Your Industry
Edit `main.py:105-108`:
```python
search_query = f"{self._spec.competitor} AND (funding OR investment OR Series A OR Series B)"
```

### Daily Executive Brief
```bash
# Add to cron for 8 AM daily
0 8 * * * cd /path/to/cocoindex && python3 -c "from main import *; print(competitive_intelligence_flow.get_trending_competitors(days=1))"
```

## Documentation

- **Full Setup**: [README.md](README.md)
- **Testing**: [TESTING.md](TESTING.md)
- **Interactive Examples**: [INTERACTIVE_DEMO.md](INTERACTIVE_DEMO.md)
- **Architecture**: [CLAUDE.md](CLAUDE.md)

## Support

- CocoIndex Docs: [cocoindex.io](https://cocoindex.io)
- GitHub Issues: Report bugs or request features
- Examples: [github.com/cocoindex-io/cocoindex](https://github.com/cocoindex-io/cocoindex)

---

**Ready to start?** Run `python3 run_interactive.py` now! 🚀
