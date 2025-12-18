#!/usr/bin/env python3
"""Generate a comprehensive intelligence report and save to file."""

import psycopg
import os
from datetime import datetime
from pathlib import Path

def load_env():
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key, value)

def generate_report():
    """Generate comprehensive intelligence report."""
    load_env()

    conn_str = os.environ.get("COCOINDEX_DATABASE_URL")
    if not conn_str:
        print("❌ COCOINDEX_DATABASE_URL not set")
        return None

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    report_file = Path(__file__).parent / f"intelligence_report_{timestamp}.txt"

    report_lines = []

    def add_line(line=""):
        report_lines.append(line)
        print(line)

    add_line("="*80)
    add_line("COMPETITIVE INTELLIGENCE REPORT")
    add_line(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    add_line("="*80)
    add_line()

    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Summary statistics
                add_line("📊 SUMMARY STATISTICS")
                add_line("-"*80)

                cur.execute("SELECT COUNT(*) FROM competitiveintelligence__intel_articles")
                articles_count = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM competitiveintelligence__intel_events")
                events_count = cur.fetchone()[0]

                add_line(f"Total Articles Indexed: {articles_count}")
                add_line(f"Total Events Extracted: {events_count}")

                if articles_count > 0:
                    add_line(f"Extraction Rate: {events_count/articles_count:.2f} events/article")

                add_line()

                # Event type breakdown
                add_line("🎯 EVENT TYPE DISTRIBUTION")
                add_line("-"*80)

                cur.execute("""
                    SELECT event_type, COUNT(*) as count
                    FROM competitiveintelligence__intel_events
                    GROUP BY event_type
                    ORDER BY count DESC
                """)

                for row in cur.fetchall():
                    add_line(f"  {row[0].ljust(25)}: {row[1]} events")

                add_line()

                # Competitor ranking
                add_line("🏢 COMPETITOR ACTIVITY RANKING")
                add_line("-"*80)

                cur.execute("""
                    SELECT competitor, COUNT(*) as event_count
                    FROM competitiveintelligence__intel_events
                    GROUP BY competitor
                    ORDER BY event_count DESC
                    LIMIT 20
                """)

                for i, row in enumerate(cur.fetchall(), 1):
                    add_line(f"  {i}. {row[0].ljust(40)}: {row[1]} events")

                add_line()

                # Recent articles
                add_line("📰 RECENT ARTICLES")
                add_line("-"*80)

                cur.execute("""
                    SELECT title, source, url, published_at
                    FROM competitiveintelligence__intel_articles
                    ORDER BY published_at DESC
                    LIMIT 15
                """)

                for row in cur.fetchall():
                    pub_date = row[3].strftime("%Y-%m-%d") if row[3] else "Unknown"
                    add_line(f"\n  [{pub_date}] {row[0]}")
                    add_line(f"  Source: {row[1]}")
                    add_line(f"  URL: {row[2]}")

                add_line()
                add_line()

                # Detailed intelligence by competitor
                add_line("="*80)
                add_line("DETAILED COMPETITIVE INTELLIGENCE")
                add_line("="*80)
                add_line()

                cur.execute("""
                    SELECT DISTINCT competitor
                    FROM competitiveintelligence__intel_events
                    ORDER BY competitor
                """)

                competitors = [row[0] for row in cur.fetchall()]

                for competitor in competitors:
                    add_line(f"\n{'='*80}")
                    add_line(f"🏢 {competitor}")
                    add_line('='*80)

                    # Get all events for this competitor
                    cur.execute("""
                        SELECT
                            e.event_type,
                            e.description,
                            e.significance,
                            e.related_companies,
                            a.title,
                            a.url,
                            a.published_at
                        FROM competitiveintelligence__intel_events e
                        JOIN competitiveintelligence__intel_articles a ON e.article_id = a.id
                        WHERE e.competitor = %s
                        ORDER BY a.published_at DESC
                    """, (competitor,))

                    events = cur.fetchall()

                    for i, event in enumerate(events, 1):
                        pub_date = event[6].strftime("%Y-%m-%d") if event[6] else "Unknown"
                        add_line(f"\n  Event {i}: {event[0].upper()}")
                        add_line(f"  Date: {pub_date}")
                        add_line(f"  Significance: {event[2]}")
                        add_line(f"  Description: {event[1]}")

                        if event[3]:  # related_companies
                            add_line(f"  Related Companies: {', '.join(event[3]) if isinstance(event[3], list) else event[3]}")

                        add_line(f"  Source: {event[4]}")
                        add_line(f"  URL: {event[5]}")

                    add_line()

                add_line()
                add_line("="*80)
                add_line("END OF REPORT")
                add_line("="*80)

    except Exception as e:
        add_line(f"\n❌ Error generating report: {e}")
        return None

    # Write to file
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    return report_file

if __name__ == "__main__":
    print("\n📝 Generating Competitive Intelligence Report...\n")

    report_file = generate_report()

    if report_file:
        print(f"\n✅ Report saved to: {report_file}")
        print(f"   File size: {report_file.stat().st_size:,} bytes")
    else:
        print("\n❌ Failed to generate report")
