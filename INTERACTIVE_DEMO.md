# Interactive Mode Demo

This shows what you'll see when running `python3 run_interactive.py`

## Example Session

```
================================================================================
🔍  COMPETITIVE INTELLIGENCE MONITOR
================================================================================

Track competitors across the web using AI-powered search and extraction.

📊 Which companies would you like to monitor?
   (Enter comma-separated list, or press Enter for default: OpenAI,Anthropic)

   Companies: Tesla,Rivian,Lucid Motors

🎯 What types of events are you interested in?
   Available options:
   1. All events (default)
   2. Product launches & features
   3. Partnerships & collaborations
   4. Funding & acquisitions
   5. Executive moves & key hires
   6. Custom search query

   Select (1-6): 2
   → Using: (product launch OR feature release OR product announcement)

📅 How many days back should we search?
   (Enter number, or press Enter for default: 7 days)

   Days: 14
   → Using: 14 days

📰 Maximum articles to fetch per competitor?
   (Enter number, or press Enter for default: 10 articles)

   Articles: 15
   → Using: 15 articles

⚙️  How would you like to run the pipeline?
   1. One-time sync (fetch and exit)
   2. Continuous monitoring (runs every hour)
   3. Custom interval

   Select (1-3): 1

================================================================================
📋 CONFIGURATION SUMMARY
================================================================================
  Companies:    Tesla,Rivian,Lucid Motors
  Event focus:  (product launch OR feature release OR product announcement)
  Time range:   Last 14 days
  Max articles: 15 per company
  Run mode:     Once
================================================================================

Proceed with these settings? (y/n): y

⚙️  Updating configuration...

================================================================================
🚀 STARTING PIPELINE
================================================================================

Running one-time sync...

Setup is already up to date.
⏳ CompetitiveIntelligence.articles_Tesla (batch update): [========] 0/15 source rows
⏳ CompetitiveIntelligence.articles_Rivian (batch update): [========] 0/12 source rows
⏳ CompetitiveIntelligence.articles_Lucid Motors (batch update): [========] 0/8 source rows
...
✅ CompetitiveIntelligence.articles_Tesla (batch update): [++++++++] 15/15 source rows
✅ CompetitiveIntelligence.articles_Rivian (batch update): [++++++++] 12/12 source rows
✅ CompetitiveIntelligence.articles_Lucid Motors (batch update): [++++++++] 8/8 source rows

================================================================================
✅ PIPELINE COMPLETED
================================================================================

Would you like to view the extracted intelligence? (y/n): y

Running test results...

🧪 Testing Competitive Intelligence Pipeline

================================================================================

1️⃣  Checking database tables...
   ✅ competitiveintelligence__cocoindex_tracking
   ✅ competitiveintelligence__intel_articles
   ✅ competitiveintelligence__intel_events

2️⃣  Checking articles...
   📰 35 articles indexed

3️⃣  Checking extracted events...
   🎯 42 events extracted
   📊 Extraction rate: 1.20 events/article

4️⃣  Event type distribution...
   • Product Launch    : 18 events
   • Partnership       : 12 events
   • Key Hire          : 8 events
   • Funding           : 4 events

5️⃣  Competitor coverage...
   • Tesla             : 22 events
   • Rivian            : 12 events
   • Lucid Motors      : 8 events
...
```

## Use Cases

### 1. Monitor AI Companies
```bash
Companies: OpenAI,Anthropic,Google AI,Microsoft AI
Event focus: 1 (All events)
Time range: 7 days
Run mode: 2 (Continuous)
```

### 2. Track EV Market Product Launches
```bash
Companies: Tesla,Rivian,Lucid,BYD,NIO
Event focus: 2 (Product launches)
Time range: 30 days
Run mode: 1 (One-time)
```

### 3. Monitor Funding in Biotech
```bash
Companies: Moderna,BioNTech,Ginkgo Bioworks,Recursion
Event focus: 4 (Funding & acquisitions)
Time range: 14 days
Run mode: 3 (Custom: 7200s = 2 hours)
```

### 4. Track Executive Moves in Tech
```bash
Companies: Apple,Google,Microsoft,Amazon,Meta
Event focus: 5 (Executive moves)
Time range: 7 days
Run mode: 1 (One-time)
```

### 5. Custom Industry Keywords
```bash
Companies: Stripe,Square,PayPal,Adyen
Event focus: 6 (Custom)
Custom terms: regulation OR compliance OR fintech OR payment
Time range: 14 days
Run mode: 1 (One-time)
```

## Tips

1. **Start with one-time sync** to see results quickly before setting up continuous monitoring

2. **Use specific event types** (options 2-5) if you want focused intelligence rather than all events

3. **Adjust time range** based on your needs:
   - 7 days: Recent competitive moves
   - 14-30 days: Broader market trends
   - 3 days: Breaking news focus

4. **Increase max articles** for comprehensive coverage, but be aware:
   - More articles = longer processing time
   - More articles = higher API costs
   - Default of 10-15 is usually sufficient

5. **Continuous monitoring** works great for:
   - Daily briefings (interval: 86400s)
   - Real-time alerts (interval: 3600s)
   - Background monitoring on a server

## Environment Persistence

Your choices update the `.env` file, so:
- **COMPETITORS** and **SEARCH_DAYS_BACK** are saved
- Next time you run direct mode (`cocoindex update main`), it uses your last settings
- You can always re-run `run_interactive.py` to change configuration
