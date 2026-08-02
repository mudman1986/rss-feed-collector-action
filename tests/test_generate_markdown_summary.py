#!/usr/bin/env python3
"""Unit tests for generate_markdown_summary.py."""

import os
import sys
import unittest

# Add parent directory to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from generate_markdown_summary import (  # noqa: E402 pylint: disable=wrong-import-position
    escape_markdown_table_cell,
    generate_markdown_summary,
)


class TestGenerateMarkdownSummary(unittest.TestCase):
    """Unit tests for markdown summary generation."""

    def test_escape_markdown_table_cell(self):
        """Table cell content should be escaped and single-line."""
        escaped = escape_markdown_table_cell("line1\nline2|part\\x")
        self.assertEqual(escaped, "line1 line2\\|part\\\\x")

    def test_generate_markdown_summary_escapes_dynamic_cells(self):
        """Summary should escape table-breaking characters in content."""
        data = {
            "metadata": {"collected_at": "2026-08-01T00:00:00Z", "hours": 24},
            "summary": {
                "total_feeds": 2,
                "successful_feeds": 1,
                "failed_feeds": 1,
                "total_articles": 1,
            },
            "feeds": {
                "Feed|Name": {
                    "count": 1,
                    "articles": [
                        {
                            "title": "Unsafe|Title\nRow",
                            "link": "https://example.com/path)",
                            "published": "2026-08-01T00:00:00Z|UTC",
                        }
                    ],
                }
            },
            "failed_feeds": [
                {
                    "name": "Failed|Feed",
                    "url": "https://bad.example/a|b",
                    "error": "boom\nbroken",
                }
            ],
        }

        summary = generate_markdown_summary(data)

        self.assertIn("### Feed\\|Name", summary)
        self.assertIn(
            "| [Unsafe\\|Title Row](https://example.com/path%29) | 2026-08-01T00:00:00Z\\|UTC |",
            summary,
        )
        self.assertIn(
            "| Failed\\|Feed | https://bad.example/a\\|b | boom broken |",
            summary,
        )


if __name__ == "__main__":
    unittest.main()
