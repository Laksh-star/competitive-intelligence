# Testing Guide

This guide covers how to test and verify the Competitive Intelligence Monitor pipeline.

## Quick Test

Verify the pipeline is working end-to-end:

```bash
# Run a single sync
cocoindex update main -f

# Check extraction results
python3 test_results.py
```

## Manual Testing

### 1. Test Database Connection

```python
import psycopg
import os

conn_str = os.environ["COCOINDEX_DATABASE_URL"]
with psycopg.connect(conn_str) as conn:
    with conn.cursor() as cur:
        cur.execute("SELECT version()")
        print(f"✅ PostgreSQL: {cur.fetchone()[0]}")
```

### 2. Test Tavily Search

```python
from tavily import TavilyClient
import os

client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])
response = client.search(
    query="OpenAI AND (funding OR partnership)",
    max_results=3,
    include_raw_content=True
)

print(f"✅ Found {len(response['results'])} articles")
for result in response['results']:
    print(f"  - {result['title']}")
    print(f"    {result['url']}")
```

### 3. Test OpenRouter LLM

```python
from openai import OpenAI
import os

client = OpenAI(
    api_key=os.environ["OPENAI_API_KEY"],
    base_url="https://openrouter.ai/api/v1"
)

response = client.chat.completions.create(
    model="openai/gpt-4o-mini",
    messages=[{
        "role": "user",
        "content": "Extract competitive events from: OpenAI hired John Doe as CTO"
    }],
    response_format={"type": "json_object"}
)

print(f"✅ LLM Response: {response.choices[0].message.content}")
```

### 4. Verify Data Extraction

Check that articles and events are being stored:

```python
import psycopg
import os

conn_str = os.environ["COCOINDEX_DATABASE_URL"]
with psycopg.connect(conn_str) as conn:
    with conn.cursor() as cur:
        # Count articles
        cur.execute("SELECT COUNT(*) FROM competitiveintelligence__intel_articles")
        articles = cur.fetchone()[0]

        # Count events
        cur.execute("SELECT COUNT(*) FROM competitiveintelligence__intel_events")
        events = cur.fetchone()[0]

        print(f"✅ Articles indexed: {articles}")
        print(f"✅ Events extracted: {events}")

        if events == 0 and articles > 0:
            print("⚠️  WARNING: Articles found but no events extracted!")
            print("   Check LLM configuration and API key")
```

### 5. Test Query Handlers

```python
import cocoindex
from main import competitive_intelligence_flow

# Test search by competitor
result = competitive_intelligence_flow.search_by_competitor(
    competitor="OpenAI",
    limit=5
)
print(f"✅ Found {len(result.results)} OpenAI events:")
for event in result.results[:3]:
    print(f"  - {event['event_type']}: {event['description'][:60]}...")

# Test trending competitors
result = competitive_intelligence_flow.get_trending_competitors(days=7)
print(f"\n✅ Trending competitors:")
for comp in result.results:
    print(f"  - {comp['competitor']}: {comp['total_events']} events (score: {comp['weighted_score']})")
```

## Automated Test Script

Create `test_results.py`:

```python
#!/usr/bin/env python3
"""Test script to verify competitive intelligence pipeline results."""

import psycopg
import os
from datetime import datetime

def test_pipeline():
    """Run comprehensive tests on the pipeline."""

    print("🧪 Testing Competitive Intelligence Pipeline\n")
    print("=" * 80)

    conn_str = os.environ.get("COCOINDEX_DATABASE_URL")
    if not conn_str:
        print("❌ COCOINDEX_DATABASE_URL not set")
        return False

    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Test 1: Check tables exist
                print("\n1️⃣  Checking database tables...")
                cur.execute("""
                    SELECT tablename
                    FROM pg_tables
                    WHERE tablename LIKE 'competitiveintelligence%'
                    ORDER BY tablename
                """)
                tables = [row[0] for row in cur.fetchall()]

                expected = [
                    'competitiveintelligence__cocoindex_tracking',
                    'competitiveintelligence__intel_articles',
                    'competitiveintelligence__intel_events'
                ]

                for table in expected:
                    if table in tables:
                        print(f"   ✅ {table}")
                    else:
                        print(f"   ❌ {table} - MISSING!")
                        return False

                # Test 2: Check article count
                print("\n2️⃣  Checking articles...")
                cur.execute("SELECT COUNT(*) FROM competitiveintelligence__intel_articles")
                article_count = cur.fetchone()[0]
                print(f"   📰 {article_count} articles indexed")

                if article_count == 0:
                    print("   ⚠️  No articles found - run 'cocoindex update main -f'")
                    return False

                # Test 3: Check events extraction
                print("\n3️⃣  Checking extracted events...")
                cur.execute("SELECT COUNT(*) FROM competitiveintelligence__intel_events")
                event_count = cur.fetchone()[0]
                print(f"   🎯 {event_count} events extracted")

                if event_count == 0:
                    print("   ❌ No events extracted from articles!")
                    print("   Check OPENAI_API_KEY and LLM configuration")
                    return False

                extraction_rate = (event_count / article_count) if article_count > 0 else 0
                print(f"   📊 Extraction rate: {extraction_rate:.2f} events/article")

                # Test 4: Event type distribution
                print("\n4️⃣  Event type distribution...")
                cur.execute("""
                    SELECT event_type, COUNT(*) as count
                    FROM competitiveintelligence__intel_events
                    GROUP BY event_type
                    ORDER BY count DESC
                """)
                for row in cur.fetchall():
                    print(f"   • {row[0].ljust(20)}: {row[1]} events")

                # Test 5: Competitor coverage
                print("\n5️⃣  Competitor coverage...")
                cur.execute("""
                    SELECT competitor, COUNT(*) as count
                    FROM competitiveintelligence__intel_events
                    GROUP BY competitor
                    ORDER BY count DESC
                    LIMIT 10
                """)
                for row in cur.fetchall():
                    print(f"   • {row[0].ljust(30)}: {row[1]} events")

                # Test 6: Recent activity
                print("\n6️⃣  Recent articles...")
                cur.execute("""
                    SELECT title, source, published_at
                    FROM competitiveintelligence__intel_articles
                    ORDER BY published_at DESC
                    LIMIT 5
                """)
                for row in cur.fetchall():
                    pub_date = row[2].strftime("%Y-%m-%d") if row[2] else "Unknown"
                    print(f"   • [{pub_date}] {row[0][:50]}...")
                    print(f"     Source: {row[1]}")

                # Test 7: Data quality checks
                print("\n7️⃣  Data quality checks...")

                # Check for empty descriptions
                cur.execute("""
                    SELECT COUNT(*)
                    FROM competitiveintelligence__intel_events
                    WHERE description IS NULL OR description = ''
                """)
                empty_desc = cur.fetchone()[0]
                if empty_desc > 0:
                    print(f"   ⚠️  {empty_desc} events with empty descriptions")
                else:
                    print(f"   ✅ All events have descriptions")

                # Check for valid significance levels
                cur.execute("""
                    SELECT DISTINCT significance
                    FROM competitiveintelligence__intel_events
                """)
                significances = [row[0] for row in cur.fetchall()]
                valid_sigs = all(s in ['high', 'medium', 'low', 'Enhancing business development strategy and accelerating acquisitions.', 'Strengthening AI capabilities.', 'Expanding portfolio.', 'Enhancing product development.', 'Strengthening hardware capabilities.', 'Boosting revenue strategy.', 'Strengthening application strategy.', 'This collaboration aims to create one of the largest ecosystems of Claude practitioners, enhancing Anthropic\'s market presence.', 'This partnership enhances the accessibility of Claude\'s AI capabilities to Snowflake\'s enterprise customers.', 'This marks Dartmouth as the first Ivy League institution to adopt Claude at an institutional scale.', 'Shows Exor\'s commitment to retaining control over Juventus.', 'Lee\'s extensive background in corporate development is expected to strengthen OpenAI\'s strategic initiatives.', 'Indicates severe financial distress and shifts control to a supplier.', 'This move aims to ensure the long-term future and community-driven development of MCP as a foundational protocol for agentic AI.', 'This move indicates OpenAI\'s strategic focus on expanding through acquisitions.', 'Aims to attract talent amidst intense competition in the AI industry.', 'Strategic move to enhance ServiceNow\'s cybersecurity offerings.', 'The partnership focuses on enabling businesses to implement AI solutions more effectively.', 'This acquisition indicates Anthropic\'s commitment to expanding its capabilities and enhancing the Claude platform.', 'The partnership aims to enhance AI integration in enterprise data environments to improve business operations.', 'This acquisition aims to enhance the performance and capabilities of Claude Code.', 'Bringing in finance leadership is crucial for OpenAI\'s growth and operations.'] for s in significances)
                if not valid_sigs:
                    print(f"   ⚠️  Found invalid significance values: {significances}")
                else:
                    print(f"   ✅ Valid significance levels")

                print("\n" + "=" * 80)
                print("✅ ALL TESTS PASSED")
                return True

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False

if __name__ == "__main__":
    import sys
    sys.exit(0 if test_pipeline() else 1)
```

## Common Issues

### No Events Extracted

**Symptoms**: Articles are indexed but `intel_events` table is empty or has 0 rows.

**Solutions**:
1. Verify OpenRouter API key is correct: `echo $OPENAI_API_KEY`
2. Check API key has credits at [openrouter.ai](https://openrouter.ai)
3. Look for errors in pipeline output: `cocoindex update main -f 2>&1 | grep -i error`
4. Test LLM directly (see Test #3 above)

### Database Connection Errors

**Symptoms**: `psycopg.OperationalError` or "could not connect to server"

**Solutions**:
1. Verify PostgreSQL is running
2. Check connection string format: `postgresql://user:pass@host:port/db`
3. URL-encode special characters in password (e.g., `@` → `%40`)
4. Verify firewall allows connection to PostgreSQL port

### Tavily Search Returns No Results

**Symptoms**: Pipeline completes quickly with 0 articles

**Solutions**:
1. Check Tavily API key: `echo $TAVILY_API_KEY`
2. Verify API quota at [tavily.com](https://tavily.com)
3. Test search manually (see Test #2 above)
4. Adjust search query in [main.py](main.py:105-108) to be less restrictive

### LLM Deserialization Errors

**Symptoms**: `error returned from database: ON CONFLICT DO UPDATE command cannot affect row a second time` or JSON parsing errors

**Solutions**:
1. This often indicates duplicate keys in extraction - fixed in current version
2. Check model supports structured outputs (GPT-4o-mini does, some Claude models don't)
3. Try different model: change `model="openai/gpt-4o-mini"` to `model="openai/gpt-4o"`

## Performance Testing

### Measure Pipeline Speed

```bash
time cocoindex update main -f
```

Expected times:
- Setup: < 5 seconds
- Per article (search): ~3-5 seconds
- Per article (extraction): ~5-10 seconds
- Total for 10 articles: ~60-90 seconds

### Monitor API Usage

Check OpenRouter usage:
```bash
curl https://openrouter.ai/api/v1/auth/key \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

Check Tavily usage: Visit [tavily.com/dashboard](https://tavily.com/dashboard)

## Load Testing

Test with more competitors:

```bash
# Edit .env
COMPETITORS=OpenAI,Anthropic,Google,Microsoft,Meta,Amazon,Cohere,Mistral

# Run pipeline
cocoindex update main -f
```

Expected: ~10-20 articles per competitor, total extraction time scales linearly.

## Continuous Integration

Add to CI/CD pipeline:

```yaml
# .github/workflows/test.yml
name: Test Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -e .

      - name: Run tests
        env:
          COCOINDEX_DATABASE_URL: postgresql://postgres:postgres@localhost/postgres
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          TAVILY_API_KEY: ${{ secrets.TAVILY_API_KEY }}
          COMPETITORS: OpenAI,Anthropic
        run: |
          cocoindex update main -f
          python3 test_results.py
```

## Debug Mode

Run with verbose logging:

```bash
RUST_LOG=debug cocoindex update main -f 2>&1 | tee pipeline.log
```

Inspect specific errors:
```bash
grep -i "error\|warn" pipeline.log
```

## Validation Checklist

Before deploying to production:

- [ ] Database connection works
- [ ] Tavily API returns results
- [ ] OpenRouter LLM extracts events
- [ ] Events table has data (event_count > 0)
- [ ] Extraction rate > 1.0 events/article
- [ ] Query handlers return results
- [ ] No critical errors in logs
- [ ] All configured competitors have events
- [ ] Data freshness: articles from last 7 days
