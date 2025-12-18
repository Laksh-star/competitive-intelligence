#!/usr/bin/env python3
"""Test script to verify competitive intelligence pipeline results."""

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

def test_pipeline():
    """Run comprehensive tests on the pipeline."""

    print("🧪 Testing Competitive Intelligence Pipeline\n")
    print("=" * 80)

    # Load environment variables
    load_env()

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
                    title = row[0][:60] + "..." if len(row[0]) > 60 else row[0]
                    print(f"   • [{pub_date}] {title}")
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

                # Check for articles without events
                cur.execute("""
                    SELECT COUNT(DISTINCT a.id)
                    FROM competitiveintelligence__intel_articles a
                    LEFT JOIN competitiveintelligence__intel_events e ON a.id = e.article_id
                    WHERE e.article_id IS NULL
                """)
                articles_no_events = cur.fetchone()[0]
                if articles_no_events > 0:
                    print(f"   ℹ️  {articles_no_events} articles with no events extracted")
                    print(f"      (This is normal for non-relevant content)")
                else:
                    print(f"   ✅ All articles have at least one event")

                # Test 8: Sample extracted intelligence
                print("\n8️⃣  Sample extracted intelligence...")
                cur.execute("""
                    SELECT
                        e.competitor,
                        e.event_type,
                        e.description,
                        a.title,
                        a.url
                    FROM competitiveintelligence__intel_events e
                    JOIN competitiveintelligence__intel_articles a ON e.article_id = a.id
                    ORDER BY e.competitor, e.event_type
                    LIMIT 3
                """)
                for i, row in enumerate(cur.fetchall(), 1):
                    print(f"\n   Example {i}:")
                    print(f"   Company: {row[0]}")
                    print(f"   Type: {row[1]}")
                    desc = row[2][:80] + "..." if len(row[2]) > 80 else row[2]
                    print(f"   Event: {desc}")
                    title = row[3][:60] + "..." if len(row[3]) > 60 else row[3]
                    print(f"   Source: {title}")

                print("\n" + "=" * 80)
                print("✅ ALL TESTS PASSED")
                print(f"\nSummary: {article_count} articles → {event_count} events")
                print(f"Pipeline is working correctly!")
                return True

    except psycopg.OperationalError as e:
        print(f"\n❌ DATABASE CONNECTION FAILED: {e}")
        print("\nTroubleshooting:")
        print("  1. Check COCOINDEX_DATABASE_URL is set correctly")
        print("  2. Verify PostgreSQL is running")
        print("  3. Check firewall/network access to database")
        return False
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import sys
    sys.exit(0 if test_pipeline() else 1)
