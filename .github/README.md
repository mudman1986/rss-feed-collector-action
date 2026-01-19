# RSS Feed Collector - Composite Action

Reusable GitHub Actions composite action for collecting RSS/Atom feeds using `feedparser`.

## Features

- Robust RSS/Atom parsing with `feedparser` library
- Structured JSON output with article metadata
- Formatted GitHub workflow summary
- Configurable time window for article collection
- Graceful error handling for unavailable feeds
- Self-contained and portable (ready for extraction to separate repository)

## Usage

```yaml
- name: Collect RSS Feeds
  id: collect
  uses: ./actions/collect-rss-feeds
  with:
    config-path: ".github/rss-feeds.json"
    hours: 24
    output-path: "rss-output.json"

- name: Use outputs
  run: |
    echo "Found ${{ steps.collect.outputs.total-articles }} articles"
```

## Inputs

| Input         | Description                       | Default                  |
| ------------- | --------------------------------- | ------------------------ |
| `config-path` | RSS feeds configuration JSON file | `.github/rss-feeds.json` |
| `hours`       | Fetch articles from last N hours  | `24`                     |
| `output-path` | Path for output JSON              | `rss-feeds-output.json`  |

## Outputs

| Output             | Description                      |
| ------------------ | -------------------------------- |
| `output-file`      | Generated JSON output file path  |
| `total-articles`   | Total articles collected         |
| `successful-feeds` | Successfully fetched feeds count |
| `failed-feeds`     | Failed feeds count               |

## Configuration Format

```json
{
  "feeds": [
    {
      "name": "Feed Name",
      "url": "https://example.com/feed.xml"
    }
  ]
}
```

## Output JSON Structure

```json
{
  "metadata": {
    "collected_at": "2024-01-01T12:00:00+00:00",
    "since": "2024-01-01T00:00:00",
    "hours": 24
  },
  "feeds": {
    "Feed Name": {
      "url": "https://example.com/feed.xml",
      "articles": [...],
      "count": 1
    }
  },
  "summary": {
    "total_feeds": 1,
    "successful_feeds": 1,
    "failed_feeds": 0,
    "total_articles": 1
  }
}
```

## Files in This Action

- `action.yml` - Action definition
- `collect_feeds.py` - Core RSS feed collection logic
- `generate_markdown_summary.py` - Generates GitHub workflow Markdown summaries
- `tests/` - Unit tests for action components

## Note on HTML/RSS Generation

This action focuses on **collecting** RSS feed data. HTML page generation and RSS feed
generation are handled by separate workflow scripts (see `.github/workflows/scripts/rss-processing/`)
to keep the action lightweight and portable for extraction to a separate repository.
