#!/usr/bin/env python3
"""Clear database and run fresh pipeline to see OpenRouter activity."""

import os
import psycopg
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

def clear_database():
    """Clear existing competitive intelligence data."""
    load_env()

    conn_str = os.environ.get("COCOINDEX_DATABASE_URL")
    if not conn_str:
        print("❌ COCOINDEX_DATABASE_URL not set")
        return False

    print("🗑️  Clearing existing data...\n")

    try:
        with psycopg.connect(conn_str) as conn:
            with conn.cursor() as cur:
                # Get counts before clearing
                cur.execute("SELECT COUNT(*) FROM competitiveintelligence__intel_articles")
                articles = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM competitiveintelligence__intel_events")
                events = cur.fetchone()[0]

                print(f"   Found {articles} articles and {events} events")

                # Clear tables
                cur.execute("""
                    TRUNCATE
                        competitiveintelligence__intel_articles,
                        competitiveintelligence__intel_events
                    CASCADE
                """)
                conn.commit()

                print("   ✅ Database cleared\n")
                return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

if __name__ == "__main__":
    import subprocess

    print("="*80)
    print("🔄 FRESH RUN - Clear Database and Process New Articles")
    print("="*80 + "\n")

    # Clear database
    if not clear_database():
        exit(1)

    # Show current competitors
    load_env()
    competitors = os.environ.get("COMPETITORS", "Not set")
    print(f"📊 Will fetch fresh articles for: {competitors}\n")

    # Confirm
    print("This will make NEW OpenRouter API calls for LLM extraction.")
    print("You'll see activity in the OpenRouter console.\n")
    confirm = input("Proceed? (y/n): ").strip().lower()

    if confirm != 'y':
        print("❌ Cancelled")
        exit(0)

    print("\n" + "="*80)
    print("🚀 Running pipeline with fresh data...")
    print("="*80 + "\n")

    # Run pipeline
    subprocess.run(["cocoindex", "update", "main", "-f"])

    print("\n" + "="*80)
    print("✅ Done! Check OpenRouter console at:")
    print("   https://openrouter.ai/activity")
    print("="*80)
