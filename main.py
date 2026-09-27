"""
EEE Opportunity Tracker
------------------------
Fetches new postings from configured RSS feeds, asks Gemini how relevant
each one is to an Electrical/Electronics Engineering student, and writes
a Markdown digest of the best matches.

Usage:
    python main.py
"""

import sys

from config import load_sources, ensure_dirs
from fetch_opportunities import fetch_all
from ai_evaluator import evaluate
from report_writer import write_report


def main() -> int:
    ensure_dirs()

    try:
        sources = load_sources()
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return 1

    feed_urls = sources.get("feeds", [])
    keywords = sources.get("keywords", ["electrical engineering", "electronics"])

    print(f"Checking {len(feed_urls)} feed(s) for new postings...")
    opportunities = fetch_all(feed_urls)
    print(f"Found {len(opportunities)} new posting(s).")

    if not opportunities:
        print("Nothing new to evaluate. Exiting.")
        return 0

    print("Asking Groq to score relevance...")
    evaluations = evaluate(opportunities, keywords)

    report_path = write_report(evaluations, min_score=sources.get("min_score", 5))
    print(f"Report written to: {report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
