# Usage Guide

Quick reference for running the competitive intelligence pipeline.

## See OpenRouter Activity

To make NEW API calls and see activity in OpenRouter console:

```bash
# Clear old data and fetch fresh articles
python3 clear_and_run.py
```

This will:
1. Clear existing database entries
2. Fetch NEW articles for your configured competitors
3. Call OpenRouter API for LLM extraction (you'll see this in console)
4. Store fresh intelligence

**Then check**: https://openrouter.ai/activity

## Generate Intelligence Report

Save all extracted intelligence to a text file:

```bash
# Generate comprehensive report
python3 generate_report.py
```

Creates: `intelligence_report_YYYY-MM-DD_HH-MM-SS.txt`

Contains:
- Summary statistics
- Event type distribution
- Competitor rankings
- Recent articles
- Detailed intelligence by competitor

## Complete Workflow

### 1. Fresh Run with Report

```bash
# Clear data and run fresh
python3 clear_and_run.py

# Generate report
python3 generate_report.py
```

### 2. Interactive Run with Report

```bash
# Interactive prompts
python3 run_interactive.py

# Generate report
python3 generate_report.py
```

### 3. Test Current Data

```bash
# View current database contents
python3 test_results.py

# Save to file
python3 generate_report.py
```

## Quick Commands

### Change Competitors

Edit `.env`:
```env
COMPETITORS=Tesla,Rivian,Lucid Motors
```

Then run:
```bash
python3 clear_and_run.py
```

### View Latest Intelligence

```bash
python3 generate_report.py && tail -100 intelligence_report_*.txt
```

### Clear Database Only

```python
python3 -c "
import psycopg, os
from pathlib import Path

# Load .env
env_file = Path('.env')
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key, value)

# Clear database
conn = psycopg.connect(os.getenv('COCOINDEX_DATABASE_URL'))
cur = conn.cursor()
cur.execute('TRUNCATE competitiveintelligence__intel_articles, competitiveintelligence__intel_events CASCADE')
conn.commit()
print('✅ Database cleared')
"
```

## Troubleshooting

### "No OpenRouter activity"

**Cause**: Processing cached articles from previous runs

**Solution**:
```bash
python3 clear_and_run.py  # Forces new API calls
```

### "Report file empty"

**Cause**: No data in database

**Solution**:
```bash
cocoindex update main -f  # Run pipeline first
python3 generate_report.py
```

### "Want to track different time period"

Edit `.env`:
```env
SEARCH_DAYS_BACK=14  # Last 14 days
```

Then:
```bash
python3 clear_and_run.py
```

## Report Output Example

```
================================================================================
COMPETITIVE INTELLIGENCE REPORT
Generated: 2025-12-18 15:30:45
================================================================================

📊 SUMMARY STATISTICS
--------------------------------------------------------------------------------
Total Articles Indexed: 35
Total Events Extracted: 42
Extraction Rate: 1.20 events/article

🎯 EVENT TYPE DISTRIBUTION
--------------------------------------------------------------------------------
  Product Launch           : 18 events
  Partnership              : 12 events
  Key Hire                 : 8 events
  Funding                  : 4 events

🏢 COMPETITOR ACTIVITY RANKING
--------------------------------------------------------------------------------
  1. Tesla                                    : 22 events
  2. Rivian                                   : 12 events
  3. Lucid Motors                             : 8 events

📰 RECENT ARTICLES
--------------------------------------------------------------------------------

  [2025-12-18] Tesla Unveils New Battery Technology
  Source: TechCrunch
  URL: https://...

================================================================================
DETAILED COMPETITIVE INTELLIGENCE
================================================================================

================================================================================
🏢 Tesla
================================================================================

  Event 1: PRODUCT LAUNCH
  Date: 2025-12-18
  Significance: high
  Description: Tesla announced new battery technology with 500-mile range...
  Source: Tesla Unveils New Battery Technology
  URL: https://...
```

## API Usage Tracking

### OpenRouter Console
- Activity: https://openrouter.ai/activity
- Shows: Model, tokens, cost per request
- Typical cost: ~$0.01-0.05 per article

### Tavily Dashboard
- Dashboard: https://tavily.com/dashboard
- Shows: Search count, quota remaining
- Free tier: 1,000 searches/month

## Cost Estimates

**Typical usage for 5 competitors, hourly monitoring:**
- Tavily: ~120 searches/day = 3,600/month (exceeds free tier)
- OpenRouter: ~$1-3/day = ~$30-90/month

**One-time analysis (10 competitors, 20 articles each):**
- Tavily: ~200 searches
- OpenRouter: ~$2-5 total

## Automation

### Hourly with Report

```bash
# Add to cron
0 * * * * cd /path/to/cocoindex && /usr/bin/python3 -c "import subprocess; subprocess.run(['cocoindex', 'update', 'main']); subprocess.run(['python3', 'generate_report.py'])"
```

### Daily Summary Email

```bash
# Add to cron (8 AM daily)
0 8 * * * cd /path/to/cocoindex && python3 generate_report.py && mail -s "Daily Intelligence Report" you@example.com < intelligence_report_*.txt
```
