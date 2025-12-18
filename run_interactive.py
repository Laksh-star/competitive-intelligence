#!/usr/bin/env python3
"""Interactive CLI for running competitive intelligence monitoring."""

import os
import sys
import subprocess
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

def print_banner():
    """Print welcome banner."""
    print("\n" + "="*80)
    print("🔍  COMPETITIVE INTELLIGENCE MONITOR")
    print("="*80)
    print("\nTrack competitors across the web using AI-powered search and extraction.\n")

def get_competitors():
    """Prompt user for competitors to track."""
    print("📊 Which companies would you like to monitor?")
    print("   (Enter comma-separated list, or press Enter for default: OpenAI,Anthropic)\n")

    competitors = input("   Companies: ").strip()

    if not competitors:
        competitors = "OpenAI,Anthropic"
        print(f"   → Using default: {competitors}")

    return competitors

def get_event_types():
    """Prompt user for event types to focus on."""
    print("\n🎯 What types of events are you interested in?")
    print("   Available options:")
    print("   1. All events (default)")
    print("   2. Product launches & features")
    print("   3. Partnerships & collaborations")
    print("   4. Funding & acquisitions")
    print("   5. Executive moves & key hires")
    print("   6. Custom search query\n")

    choice = input("   Select (1-6): ").strip()

    search_queries = {
        "1": "(funding OR partnership OR product launch OR acquisition OR executive hire)",
        "2": "(product launch OR feature release OR product announcement)",
        "3": "(partnership OR collaboration OR alliance OR joint venture)",
        "4": "(funding OR acquisition OR investment OR merger OR IPO)",
        "5": "(executive hire OR appointment OR CEO OR CTO OR leadership)",
    }

    if choice == "6":
        custom = input("   Enter custom search terms: ").strip()
        return f"({custom})" if custom else search_queries["1"]

    query = search_queries.get(choice, search_queries["1"])
    print(f"   → Using: {query}")
    return query

def get_time_range():
    """Prompt user for time range to search."""
    print("\n📅 How many days back should we search?")
    print("   (Enter number, or press Enter for default: 7 days)\n")

    days = input("   Days: ").strip()

    if not days:
        days = "7"
        print(f"   → Using default: {days} days")
    elif not days.isdigit():
        print("   ⚠️  Invalid input, using default: 7 days")
        days = "7"

    return days

def get_max_results():
    """Prompt user for maximum articles per competitor."""
    print("\n📰 Maximum articles to fetch per competitor?")
    print("   (Enter number, or press Enter for default: 10 articles)\n")

    max_results = input("   Articles: ").strip()

    if not max_results:
        max_results = "10"
        print(f"   → Using default: {max_results} articles")
    elif not max_results.isdigit():
        print("   ⚠️  Invalid input, using default: 10 articles")
        max_results = "10"

    return max_results

def get_run_mode():
    """Prompt user for run mode."""
    print("\n⚙️  How would you like to run the pipeline?")
    print("   1. One-time sync (fetch and exit)")
    print("   2. Continuous monitoring (runs every hour)")
    print("   3. Custom interval\n")

    choice = input("   Select (1-3): ").strip()

    if choice == "2":
        return "continuous", "3600"
    elif choice == "3":
        interval = input("   Enter interval in seconds (e.g., 1800 for 30 min): ").strip()
        if interval.isdigit():
            return "continuous", interval
        print("   ⚠️  Invalid input, using one-time sync")

    return "once", None

def update_env_file(competitors, days_back):
    """Update .env file with user choices."""
    env_file = Path(__file__).parent / ".env"

    if not env_file.exists():
        print("\n❌ Error: .env file not found!")
        print("   Please copy .env.example to .env and add your API keys.")
        sys.exit(1)

    # Read existing .env
    with open(env_file, 'r') as f:
        lines = f.readlines()

    # Update competitors and days_back
    with open(env_file, 'w') as f:
        for line in lines:
            if line.startswith('COMPETITORS='):
                f.write(f'COMPETITORS={competitors}\n')
            elif line.startswith('SEARCH_DAYS_BACK='):
                f.write(f'SEARCH_DAYS_BACK={days_back}\n')
            else:
                f.write(line)

def create_custom_main(search_query, max_results):
    """Create a temporary main file with custom search query."""
    main_file = Path(__file__).parent / "main.py"

    with open(main_file, 'r') as f:
        content = f.read()

    # Update search query
    old_query = 'f"{self._spec.competitor} AND "\n            f"(funding OR partnership OR product launch OR acquisition OR executive hire)"'
    new_query = f'f"{{self._spec.competitor}} AND "\n            f"{search_query}"'

    content = content.replace(old_query, new_query)

    # Update max_results default
    content = content.replace('max_results: int = 10', f'max_results: int = {max_results}')

    # Write to temporary file
    temp_main = Path(__file__).parent / "main_custom.py"
    with open(temp_main, 'w') as f:
        f.write(content)

    return temp_main

def run_pipeline(mode, interval=None):
    """Run the cocoindex pipeline."""
    print("\n" + "="*80)
    print("🚀 STARTING PIPELINE")
    print("="*80 + "\n")

    if mode == "once":
        print("Running one-time sync...\n")
        subprocess.run(["cocoindex", "update", "main", "-f"])
    else:
        print(f"Starting continuous monitoring (interval: {interval}s)...\n")
        print("Press Ctrl+C to stop\n")
        subprocess.run(["cocoindex", "update", "-L", "main.py"])

def show_results_prompt():
    """Prompt to show results."""
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETED")
    print("="*80 + "\n")

    print("Would you like to view the extracted intelligence? (y/n): ", end='')
    choice = input().strip().lower()

    if choice == 'y':
        print("\nRunning test results...\n")
        subprocess.run(["python3", "test_results.py"])

def main():
    """Main interactive CLI."""
    # Load existing environment
    load_env()

    # Check for required API keys
    if not os.environ.get("TAVILY_API_KEY") or not os.environ.get("OPENAI_API_KEY"):
        print("\n❌ Error: Missing API keys in .env file!")
        print("   Please set TAVILY_API_KEY and OPENAI_API_KEY")
        sys.exit(1)

    # Show banner
    print_banner()

    # Get user preferences
    competitors = get_competitors()
    search_query = get_event_types()
    days_back = get_time_range()
    max_results = get_max_results()
    mode, interval = get_run_mode()

    # Show summary
    print("\n" + "="*80)
    print("📋 CONFIGURATION SUMMARY")
    print("="*80)
    print(f"  Companies:    {competitors}")
    print(f"  Event focus:  {search_query}")
    print(f"  Time range:   Last {days_back} days")
    print(f"  Max articles: {max_results} per company")
    print(f"  Run mode:     {mode.title()}" + (f" (every {interval}s)" if interval else ""))
    print("="*80 + "\n")

    # Confirm
    print("Proceed with these settings? (y/n): ", end='')
    confirm = input().strip().lower()

    if confirm != 'y':
        print("\n❌ Cancelled by user")
        sys.exit(0)

    # Update configuration
    print("\n⚙️  Updating configuration...")
    update_env_file(competitors, days_back)

    # Note: For now, we'll use the default main.py
    # In a production version, you'd modify main.py with the custom search query
    if search_query != "(funding OR partnership OR product launch OR acquisition OR executive hire)":
        print("   ℹ️  Custom search queries require editing main.py:105-108")
        print(f"      Change to: {search_query}")

    # Run pipeline
    try:
        run_pipeline(mode, interval)

        if mode == "once":
            show_results_prompt()
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline stopped by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
