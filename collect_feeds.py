#!/usr/bin/env python3
"""
RSS Feed Collector
Fetches and processes RSS/Atom feeds, outputting results in JSON format
"""

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import feedparser


def parse_rss_feed(
    url: str, since_time: datetime
) -> Tuple[Optional[List[Dict[str, Any]]], Optional[str]]:
    """
    Parse an RSS/Atom feed and return articles published after since_time

    Args:
        url: RSS feed URL
        since_time: datetime object - only return articles after this time

    Returns:
        Tuple of (articles list, error message). If successful, error is None.
        If failed, articles is None and error contains the reason.
    """
    articles = []

    try:
        # Add user agent to avoid 403 errors
        req = Request(url, headers={"User-Agent": "Mozilla/5.0 RSS-Feed-Collector/1.0"})
        with urlopen(req, timeout=30) as response:
            content = response.read()

        # Parse the feed
        feed = feedparser.parse(content)

        # Check for parsing errors
        if feed.bozo and not feed.entries:
            error_msg = str(feed.get("bozo_exception", "Unknown parsing error"))
            raise ValueError(f"Feed parsing error: {error_msg}")

        # Process entries
        for entry in feed.entries:
            title = entry.get("title", "No title")
            link = entry.get("link", "")

            # Get publication date - feedparser normalizes this
            pub_date = None
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                # Extract date components and create datetime
                time_tuple = entry.published_parsed[:6]
                pub_date = datetime(*time_tuple).replace(tzinfo=timezone.utc)
            elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                # Extract date components and create datetime
                time_tuple = entry.updated_parsed[:6]
                pub_date = datetime(*time_tuple).replace(tzinfo=timezone.utc)

            # Filter by date if available
            if pub_date:
                # Convert to naive UTC for comparison
                pub_date_naive = pub_date.replace(tzinfo=None)
                if pub_date_naive > since_time:
                    articles.append(
                        {
                            "title": title,
                            "link": link,
                            "published": pub_date.isoformat(),
                        }
                    )
            else:
                # No date available, include it anyway
                articles.append({"title": title, "link": link, "published": "Unknown"})

    except HTTPError as e:
        error_msg = f"HTTP {e.code}: {e.reason}"
        print(f"Error fetching feed {url}: {error_msg}", file=sys.stderr)
        return None, error_msg
    except URLError as e:
        error_msg = f"Connection error: {e.reason}"
        print(f"Error fetching feed {url}: {error_msg}", file=sys.stderr)
        return None, error_msg
    except TimeoutError:
        error_msg = "Connection timeout"
        print(f"Error fetching feed {url}: {error_msg}", file=sys.stderr)
        return None, error_msg
    except ValueError as e:
        error_msg = str(e)
        print(f"Error fetching feed {url}: {error_msg}", file=sys.stderr)
        return None, error_msg
    except Exception as e:  # pylint: disable=broad-exception-caught
        # Catch any other exceptions and provide a generic error
        # We catch all exceptions here because network/parsing can fail in many ways
        error_msg = f"Unknown error: {str(e)}" if str(e) else "Unknown error"
        print(f"Error fetching feed {url}: {error_msg}", file=sys.stderr)
        return None, error_msg

    return articles, None


def main():
    # pylint: disable=too-many-locals
    """
    Main entry point for the RSS feed collector script.

    Parses command line arguments, loads RSS feed configuration, and collects
    articles from feeds published within the specified time window.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description="Collect RSS feeds")
    parser.add_argument(
        "--config", required=True, help="Path to RSS feeds configuration file"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=720,
        help="Fetch articles from the last N hours (default: 720 = 30 days)",
    )
    parser.add_argument("--output", required=True, help="Output JSON file path")

    args = parser.parse_args()

    # Always collect for the maximum timeframe to support all filter options
    # Default to 30 days (720 hours) to support all timeframe options
    max_hours = max(args.hours, 720)
    since_time = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        hours=max_hours
    )
    print(
        f"Fetching articles published after {since_time.isoformat()} "
        f"(last {max_hours} hours)",
        file=sys.stderr,
    )

    # Load RSS feeds configuration
    try:
        with open(args.config, "r", encoding="utf-8") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file {args.config} not found", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.config}: {e}", file=sys.stderr)
        sys.exit(1)

    results = {
        "metadata": {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "since": since_time.isoformat(),
            "hours": max_hours,
        },
        "feeds": {},
        "failed_feeds": [],
    }

    # Fetch each feed
    total_articles = 0
    for feed in config.get("feeds", []):
        feed_name = feed.get("name", "Unknown")
        feed_url = feed.get("url", "")

        if not feed_url:
            print(f"Skipping feed '{feed_name}': No URL provided", file=sys.stderr)
            continue

        print(f"Fetching {feed_name}...", file=sys.stderr)
        articles, error = parse_rss_feed(feed_url, since_time)

        if articles is not None:
            results["feeds"][feed_name] = {
                "url": feed_url,
                "articles": articles,
                "count": len(articles),
            }
            total_articles += len(articles)
            print(f"  ✓ Found {len(articles)} new articles", file=sys.stderr)
        else:
            error_reason = error if error else "Unknown"
            results["failed_feeds"].append(
                {"name": feed_name, "url": feed_url, "error": error_reason}
            )
            print(f"  ✗ Failed to fetch: {error_reason}", file=sys.stderr)

    # Add summary to results
    results["summary"] = {
        "total_feeds": len(config.get("feeds", [])),
        "successful_feeds": len(results["feeds"]),
        "failed_feeds": len(results["failed_feeds"]),
        "total_articles": total_articles,
    }

    # Save results as JSON
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\n✓ Results saved to {args.output}", file=sys.stderr)
    print("\nSummary:", file=sys.stderr)
    summary = results["summary"]
    print(f"  Successful feeds: {summary['successful_feeds']}", file=sys.stderr)
    print(f"  Failed feeds: {summary['failed_feeds']}", file=sys.stderr)
    print(f"  Total articles: {summary['total_articles']}", file=sys.stderr)


if __name__ == "__main__":
    main()
