# Tests for DevOps Feed Hub Action

This directory contains unit tests for the DevOps Feed Hub RSS feed collection action.

## Running Tests

To run all tests:

```bash
python3 -m pytest actions/collect-rss-feeds/tests/ -v
```

To run a specific test file:

```bash
python3 -m pytest actions/collect-rss-feeds/tests/test_collect_feeds.py -v
python3 -m pytest actions/collect-rss-feeds/tests/test_parse_rss_feed.py -v
```

## Test Coverage

### test_collect_feeds.py

Tests for the `collect_feeds.py` module:

- Configuration file validation
- Script existence checks
- Integration with Markdown summary generation

### test_parse_rss_feed.py

Tests for RSS feed parsing:

- Valid feed parsing
- Date filtering
- Error handling
- Network issues
- Empty feeds
- Malformed feeds

## Dependencies

Tests require the same dependencies as the main scripts:

- feedparser
- pytest
- Python 3.11+

Install test dependencies:

```bash
pip install feedparser pytest
```
