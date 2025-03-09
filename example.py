#!/usr/bin/env python3
"""
Example script demonstrating the usage of the news scraper.
"""
from news_scraper import NYTimesScraper, BBCScraper
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser(description="News Scraper Example")
    parser.add_argument(
        "--source",
        choices=["nytimes", "bbc"],
        default="nytimes",
        help="News source to scrape (default: nytimes)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=3,
        help="Maximum number of articles to fetch (default: 3)",
    )
    parser.add_argument(
        "--url", type=str, help="Specific article URL to scrape (optional)"
    )
    parser.add_argument(
        "--output",
        type=str,
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    # Create the appropriate scraper
    if args.source == "nytimes":
        scraper = NYTimesScraper()
        print(f"Using NYTimes scraper")
    elif args.source == "bbc":
        scraper = BBCScraper()
        print(f"Using BBC scraper")

    # Scrape a specific URL if provided
    if args.url:
        print(f"Fetching article from URL: {args.url}")
        article = scraper.fetch_article(args.url)
        if article:
            output_articles([article], args.output)
        else:
            print("Failed to fetch the article.")
            sys.exit(1)
    # Otherwise, fetch the latest articles
    else:
        print(f"Fetching {args.limit} latest articles from {args.source}...")
        articles = scraper.fetch_latest_articles(limit=args.limit)
        if articles:
            output_articles(articles, args.output)
        else:
            print("No articles found.")
            sys.exit(1)


def output_articles(articles, format_type):
    """Output articles in the specified format."""
    if format_type == "json":
        # Convert articles to JSON
        articles_dict = [article.to_dict() for article in articles]
        print(json.dumps(articles_dict, indent=2))
    else:
        # Output as formatted text
        for i, article in enumerate(articles, 1):
            print(f"\nArticle {i}:")
            print(f"Title: {article.title}")
            print(f"URL: {article.url}")
            print(f"Author: {article.author}")
            print(f"Date: {article.date}")
            if article.summary:
                print(f"Summary: {article.summary}")
            if article.categories:
                print(f"Categories: {', '.join(article.categories)}")
            print(f"Content preview: {article.content[:150]}...")
            print("-" * 50)


if __name__ == "__main__":
    main()
