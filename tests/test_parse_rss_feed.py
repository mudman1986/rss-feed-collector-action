#!/usr/bin/env python3
"""
Unit tests for parse_rss_feed function in collect_feeds.py
"""

import os
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

# Add parent directory to path to import the module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from collect_feeds import (  # noqa: E402 pylint: disable=wrong-import-position
    parse_rss_feed,
)


class TestParseRssFeed(unittest.TestCase):
    """Unit tests for parse_rss_feed function"""

    @patch("collect_feeds.urlopen")
    @patch("collect_feeds.feedparser.parse")
    def test_parse_valid_feed(self, mock_feedparser, mock_urlopen):
        """Test parsing a valid RSS feed with articles"""
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.read.return_value = b"<rss>mock feed content</rss>"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        # Mock feedparser response with proper entry objects
        mock_feed = MagicMock()
        mock_feed.bozo = False

        entry1 = MagicMock()
        entry1.get.side_effect = lambda key, default=None: {
            "title": "Test Article 1",
            "link": "https://example.com/article1",
        }.get(key, default)
        entry1.published_parsed = (2026, 1, 8, 12, 0, 0, 0, 0, 0)
        type(entry1).updated_parsed = property(lambda self: None)

        entry2 = MagicMock()
        entry2.get.side_effect = lambda key, default=None: {
            "title": "Test Article 2",
            "link": "https://example.com/article2",
        }.get(key, default)
        entry2.published_parsed = (2026, 1, 7, 12, 0, 0, 0, 0, 0)
        type(entry2).updated_parsed = property(lambda self: None)

        mock_feed.entries = [entry1, entry2]
        mock_feedparser.return_value = mock_feed

        # Call the function
        since_time = datetime(2026, 1, 6, 0, 0, 0)
        articles, error = parse_rss_feed("https://example.com/feed.xml", since_time)

        # Verify results
        self.assertIsNotNone(articles)
        self.assertIsNone(error)
        self.assertEqual(len(articles), 2)
        self.assertEqual(articles[0]["title"], "Test Article 1")
        self.assertEqual(articles[0]["link"], "https://example.com/article1")
        self.assertIn("published", articles[0])

    @patch("collect_feeds.urlopen")
    @patch("collect_feeds.feedparser.parse")
    def test_parse_feed_with_old_articles(self, mock_feedparser, mock_urlopen):
        """Test that old articles are filtered out"""
        mock_response = MagicMock()
        mock_response.read.return_value = b"<rss>mock feed content</rss>"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        mock_feed = MagicMock()
        mock_feed.bozo = False

        # Create mock entries with proper attributes
        recent_entry = MagicMock()
        recent_entry.get.side_effect = lambda key, default=None: {
            "title": "Recent Article",
            "link": "https://example.com/recent",
        }.get(key, default)
        recent_entry.published_parsed = (2026, 1, 8, 12, 0, 0, 0, 0, 0)
        type(recent_entry).updated_parsed = property(lambda self: None)

        old_entry = MagicMock()
        old_entry.get.side_effect = lambda key, default=None: {
            "title": "Old Article",
            "link": "https://example.com/old",
        }.get(key, default)
        old_entry.published_parsed = (2025, 12, 1, 12, 0, 0, 0, 0, 0)
        type(old_entry).updated_parsed = property(lambda self: None)

        mock_feed.entries = [recent_entry, old_entry]
        mock_feedparser.return_value = mock_feed

        since_time = datetime(2026, 1, 1, 0, 0, 0)
        articles, error = parse_rss_feed("https://example.com/feed.xml", since_time)

        self.assertIsNone(error)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "Recent Article")

    @patch("collect_feeds.urlopen")
    @patch("collect_feeds.feedparser.parse")
    def test_parse_feed_with_updated_parsed(self, mock_feedparser, mock_urlopen):
        """Test parsing feed with updated_parsed instead of published_parsed"""
        mock_response = MagicMock()
        mock_response.read.return_value = b"<rss>mock feed content</rss>"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_entry = {
            "title": "Updated Article",
            "link": "https://example.com/updated",
            "updated_parsed": (2026, 1, 8, 12, 0, 0, 0, 0, 0),
        }
        # Simulate no published_parsed attribute
        mock_entry_obj = MagicMock()
        mock_entry_obj.get.side_effect = lambda key, default=None: mock_entry.get(
            key, default
        )
        mock_entry_obj.published_parsed = None
        mock_entry_obj.updated_parsed = mock_entry["updated_parsed"]
        mock_entry_obj.__getitem__ = lambda self, key: mock_entry[key]

        # Create a proper mock for hasattr checks
        type(mock_entry_obj).published_parsed = property(lambda self: None)
        type(mock_entry_obj).updated_parsed = property(
            lambda self: mock_entry["updated_parsed"]
        )

        mock_feed.entries = [mock_entry_obj]
        mock_feedparser.return_value = mock_feed

        since_time = datetime(2026, 1, 1, 0, 0, 0)
        articles, error = parse_rss_feed("https://example.com/feed.xml", since_time)

        self.assertIsNone(error)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "Updated Article")

    @patch("collect_feeds.urlopen")
    @patch("collect_feeds.feedparser.parse")
    def test_parse_feed_without_dates(self, mock_feedparser, mock_urlopen):
        """Test parsing articles without publication dates"""
        mock_response = MagicMock()
        mock_response.read.return_value = b"<rss>mock feed content</rss>"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_entry = MagicMock()
        mock_entry.get.side_effect = lambda key, default=None: {
            "title": "No Date Article",
            "link": "https://example.com/nodate",
        }.get(key, default)
        # Mock hasattr to return False for date fields
        type(mock_entry).published_parsed = property(lambda self: None)
        type(mock_entry).updated_parsed = property(lambda self: None)

        mock_feed.entries = [mock_entry]
        mock_feedparser.return_value = mock_feed

        since_time = datetime(2026, 1, 1, 0, 0, 0)
        articles, error = parse_rss_feed("https://example.com/feed.xml", since_time)

        self.assertIsNone(error)
        self.assertEqual(len(articles), 1)
        self.assertEqual(articles[0]["title"], "No Date Article")
        self.assertEqual(articles[0]["published"], "Unknown")

    @patch("collect_feeds.urlopen")
    def test_parse_feed_network_error(self, mock_urlopen):
        """Test that network errors are handled gracefully"""
        mock_urlopen.side_effect = Exception("Network error")

        since_time = datetime(2026, 1, 1, 0, 0, 0)
        articles, error = parse_rss_feed("https://example.com/feed.xml", since_time)

        self.assertIsNone(articles)
        self.assertIsNotNone(error)
        self.assertIn("Network error", error)

    @patch("collect_feeds.urlopen")
    @patch("collect_feeds.feedparser.parse")
    def test_parse_feed_parsing_error(self, mock_feedparser, mock_urlopen):
        """Test that feed parsing errors are handled"""
        mock_response = MagicMock()
        mock_response.read.return_value = b"invalid xml"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        mock_feed = MagicMock()
        mock_feed.bozo = True
        mock_feed.entries = []
        mock_feed.get.return_value = "Parse error"
        mock_feedparser.return_value = mock_feed

        since_time = datetime(2026, 1, 1, 0, 0, 0)
        articles, error = parse_rss_feed("https://example.com/feed.xml", since_time)

        self.assertIsNone(articles)
        self.assertIsNotNone(error)
        self.assertIn("Feed parsing error", error)

    @patch("collect_feeds.urlopen")
    @patch("collect_feeds.feedparser.parse")
    def test_parse_feed_empty(self, mock_feedparser, mock_urlopen):
        """Test parsing an empty feed returns empty list"""
        mock_response = MagicMock()
        mock_response.read.return_value = b"<rss><channel></channel></rss>"
        mock_response.__enter__.return_value = mock_response
        mock_response.__exit__.return_value = None
        mock_urlopen.return_value = mock_response

        mock_feed = MagicMock()
        mock_feed.bozo = False
        mock_feed.entries = []
        mock_feedparser.return_value = mock_feed

        since_time = datetime(2026, 1, 1, 0, 0, 0)
        articles, error = parse_rss_feed("https://example.com/feed.xml", since_time)

        self.assertIsNotNone(articles)
        self.assertIsNone(error)
        self.assertEqual(len(articles), 0)


if __name__ == "__main__":
    unittest.main()
