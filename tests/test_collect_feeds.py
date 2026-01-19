#!/usr/bin/env python3
"""
Unit tests for collect_feeds.py
Tests the RSS feed collection functionality
"""

import json
import os
import unittest


class TestCollectFeedsIntegration(unittest.TestCase):
    """Integration tests for collect_feeds script"""

    def test_config_file_structure(self):
        """Test that config file has correct structure"""
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "rss-feeds.json"
        )

        # Check if config file exists
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)

            # Verify structure
            self.assertIn("feeds", config)
            self.assertIsInstance(config["feeds"], list)

            # Verify each feed has required fields
            for feed in config["feeds"]:
                self.assertIn("name", feed)
                self.assertIn("url", feed)
                self.assertIsInstance(feed["name"], str)
                self.assertIsInstance(feed["url"], str)
                # URLs should start with http or https
                self.assertTrue(
                    feed["url"].startswith("http://")
                    or feed["url"].startswith("https://"),
                    f"Feed URL should start with http:// or https://: {feed['url']}",
                )

    def test_script_exists(self):
        """Test that collect_feeds.py script exists"""
        script_path = os.path.join(os.path.dirname(__file__), "..", "collect_feeds.py")
        self.assertTrue(os.path.exists(script_path), "collect_feeds.py should exist")

    def test_generate_markdown_summary_script_exists(self):
        """Test that generate_markdown_summary.py script exists"""
        script_path = os.path.join(
            os.path.dirname(__file__), "..", "generate_markdown_summary.py"
        )
        self.assertTrue(
            os.path.exists(script_path), "generate_markdown_summary.py should exist"
        )


if __name__ == "__main__":
    unittest.main()
