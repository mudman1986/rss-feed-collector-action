#!/usr/bin/env python3
"""
Markdown Summary Generator for RSS Feed Collector Action
Generates GitHub workflow summary from RSS feed collection data
"""

import argparse
import json
from typing import Any, Dict


def escape_markdown_table_cell(value: Any) -> str:
    """Escape content that is rendered inside markdown tables."""
    text = str(value)
    return (
        text.replace("\\", "\\\\")
        .replace("\r", " ")
        .replace("\n", " ")
        .replace("|", "\\|")
    )


def generate_markdown_summary(data: Dict[str, Any]) -> str:
    """
    Generate markdown summary from RSS feed collection data

    Args:
        data: RSS feed collection data dictionary

    Returns:
        Markdown formatted string
    """
    summary = []
    summary.append("# 📰 DevOps Feed Hub Summary\n")
    summary.append(f"**Collected at:** {data['metadata']['collected_at']}\n")
    hours = data["metadata"].get("hours", 24)
    summary.append(f"**Time range:** Last {hours} hours\n")
    summary.append(
        "**Note:** Web interface provides filtering for 1 day, 7 days, or 30 days\n"
    )
    summary.append("")

    # Overall summary
    summary.append("## 📊 Summary\n")
    summary.append(f"- **Total feeds:** {data['summary']['total_feeds']}")
    summary.append(f"- **Successful:** {data['summary']['successful_feeds']}")
    summary.append(f"- **Failed:** {data['summary']['failed_feeds']}")
    summary.append(f"- **Total articles:** {data['summary']['total_articles']}")
    summary.append("")

    # Successful feeds
    if data["feeds"]:
        summary.append("## ✅ Successful Feeds\n")
        for feed_name, feed_data in data["feeds"].items():
            summary.append(f"### {escape_markdown_table_cell(feed_name)}")
            summary.append(f"- **Articles:** {feed_data['count']}")

            if feed_data["articles"]:
                summary.append("\n| Title | Published |")
                summary.append("|-------|-----------|")
                for article in feed_data["articles"][:10]:  # Limit to first 10
                    safe_title = escape_markdown_table_cell(article["title"])
                    title = (
                        safe_title[:80] + "..." if len(safe_title) > 80 else safe_title
                    )
                    safe_link = str(article["link"]).replace(")", "%29")
                    published = escape_markdown_table_cell(article["published"])
                    summary.append(f"| [{title}]({safe_link}) | {published} |")

                if feed_data["count"] > 10:
                    summary.append(
                        f"\n*...and {feed_data['count'] - 10} more articles*"
                    )
            else:
                summary.append("*No new articles*")

            summary.append("")

    # Failed feeds
    if data["failed_feeds"]:
        summary.append("## ❌ Failed Feeds\n")
        summary.append("| Feed Name | URL | Error |")
        summary.append("|-----------|-----|-------|")
        for failed in data["failed_feeds"]:
            feed_name = escape_markdown_table_cell(failed["name"])
            feed_url = escape_markdown_table_cell(failed["url"])
            error_reason = escape_markdown_table_cell(failed.get("error", "Unknown"))
            summary.append(f"| {feed_name} | {feed_url} | {error_reason} |")
        summary.append("")

    return "\n".join(summary)


def main():
    """
    Main entry point for the markdown summary generator script.

    Returns:
        int: 0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Generate markdown summary from RSS feed collection data"
    )
    parser.add_argument(
        "--input", required=True, help="Input JSON file from RSS feed collection"
    )
    parser.add_argument("--output", required=True, help="Output markdown file path")

    args = parser.parse_args()

    # Read input JSON
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file {args.input} not found")
        return 1
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in {args.input}: {e}")
        return 1

    # Generate markdown
    markdown_content = generate_markdown_summary(data)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"✓ Markdown summary written to {args.output}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
