import json
import tempfile
import unittest
from pathlib import Path

import local_intel
import agent_demo
import env_utils
import mcp_server
import providers


class LocalIntelTests(unittest.TestCase):
    def setUp(self):
        self.config = local_intel.load_json(local_intel.DEFAULT_CONFIG)
        self.articles = local_intel.load_articles(local_intel.DEFAULT_INPUT)

    def test_extracts_events_from_sample_articles(self):
        events = local_intel.extract_events(self.config, self.articles)

        self.assertGreaterEqual(len(events), 3)
        self.assertIn("OpenAI", {event.competitor for event in events})
        self.assertIn("product_launch", {event.event_type for event in events})
        self.assertTrue(all(0 <= event.score <= 100 for event in events))

    def test_generates_reports(self):
        events = local_intel.extract_events(self.config, self.articles)

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            md_path = local_intel.write_markdown_report(self.config, events, output_dir, "test")
            json_path = local_intel.write_json_report(events, output_dir, "test")
            csv_path = local_intel.write_csv_report(events, output_dir, "test")
            html_path = local_intel.write_html_dashboard(self.config, events, output_dir, "test")

            self.assertTrue(md_path.exists())
            self.assertTrue(json_path.exists())
            self.assertTrue(csv_path.exists())
            self.assertTrue(html_path.exists())

            payload = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["summary"]["total_events"], len(events))
            self.assertIn("Competitive Intelligence Dashboard", html_path.read_text(encoding="utf-8"))

    def test_analyze_saved_articles_shared_engine(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = local_intel.analyze_saved_articles(output_dir=tmp, slug="shared", dashboard=True)

            self.assertEqual(result["mode"], "local")
            self.assertEqual(result["article_count"], 3)
            self.assertEqual(result["event_count"], 3)
            self.assertTrue(Path(result["paths"]["brief"]).exists())
            self.assertTrue(Path(result["paths"]["dashboard"]).exists())

    def test_local_provider_search_and_trends(self):
        provider = providers.LocalIntelProvider()

        search = provider.search_events(competitor="OpenAI", limit=5)
        trends = provider.get_trending_competitors(limit=2)

        self.assertEqual(search["mode"], "local")
        self.assertGreaterEqual(search["matched_events"], 1)
        self.assertEqual(trends["mode"], "local")
        self.assertLessEqual(len(trends["results"]), 2)
        self.assertIn("competitor", trends["results"][0])

    def test_provider_selection_rejects_unknown_mode(self):
        with self.assertRaises(ValueError):
            providers.get_provider("unknown")

    def test_mcp_tools_are_directly_callable(self):
        analysis = mcp_server.analyze_saved_articles(slug="mcp-smoke")
        search = mcp_server.search_events(query="enterprise", limit=2)
        trends = mcp_server.get_trending_competitors(limit=3)
        brief = mcp_server.create_brief(slug="mcp-brief")
        dashboard = mcp_server.create_dashboard(slug="mcp-dashboard")
        guarded_live = mcp_server.run_cocoindex_update(
            live=False,
            competitors="Apple, Microsoft",
            event_query="(product launch OR partnership)",
            max_results=2,
        )

        self.assertEqual(analysis["mode"], "local")
        self.assertGreaterEqual(search["matched_events"], 1)
        self.assertEqual(trends["mode"], "local")
        self.assertTrue(Path(brief["path"]).exists())
        self.assertTrue(Path(dashboard["path"]).exists())
        self.assertFalse(guarded_live["ok"])
        self.assertEqual(guarded_live["effective_config"]["competitors"], "Apple,Microsoft")

    def test_live_cocoindex_argument_overrides(self):
        env = {"COMPETITORS": "OpenAI", "MAX_RESULTS_PER_COMPETITOR": "1"}

        updated = mcp_server._apply_live_overrides(
            env,
            competitors=["Apple", "Microsoft"],
            event_query="(funding OR launch)",
            max_results=3,
            search_days_back=14,
            refresh_interval_seconds=120,
        )

        self.assertEqual(updated["COMPETITORS"], "Apple,Microsoft")
        self.assertEqual(updated["EVENT_QUERY"], "(funding OR launch)")
        self.assertEqual(updated["MAX_RESULTS_PER_COMPETITOR"], "3")
        self.assertEqual(updated["SEARCH_DAYS_BACK"], "14")
        self.assertEqual(updated["REFRESH_INTERVAL_SECONDS"], "120")

    def test_agent_demo_generates_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = agent_demo.run_demo(output_dir=Path(tmp), slug="agent-test")

            transcript_path = Path(result["transcript_path"])
            self.assertTrue(transcript_path.exists())
            transcript = transcript_path.read_text(encoding="utf-8")
            self.assertIn("Tool Call: analyze_saved_articles", transcript)
            self.assertIn("Agent Summary", transcript)
            self.assertTrue(Path(result["brief"]["path"]).exists())
            self.assertTrue(Path(result["dashboard"]["path"]).exists())

    def test_load_env_does_not_overwrite_existing_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            env_path = Path(tmp) / ".env"
            env_path.write_text("EXISTING=value_from_file\nNEW_VALUE=loaded\n", encoding="utf-8")
            import os

            os.environ["EXISTING"] = "already_set"
            env_utils.load_env(env_path)

            self.assertEqual(os.environ["EXISTING"], "already_set")
            self.assertEqual(os.environ["NEW_VALUE"], "loaded")


if __name__ == "__main__":
    unittest.main()
