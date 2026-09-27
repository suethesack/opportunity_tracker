"""
Fetches new postings (hackathons, internships, scholarships, etc.) from a
list of RSS/Atom feeds and filters out ones already seen in a previous run.
"""

import json
from dataclasses import dataclass, asdict
from typing import List

import feedparser

from config import SEEN_FILE


@dataclass
class Opportunity:
    title: str
    link: str
    summary: str
    source: str
    published: str = ""

    def to_dict(self):
        return asdict(self)


def _load_seen_links() -> set:
    if not SEEN_FILE.exists():
        return set()
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except (json.JSONDecodeError, OSError):
        return set()


def _save_seen_links(links: set) -> None:
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(links), f, indent=2)


def fetch_all(feed_urls: List[str], mark_as_seen: bool = True) -> List[Opportunity]:
    """
    Pull entries from every feed URL, skip ones we've already reported,
    and return the new ones as Opportunity objects.
    """
    seen_links = _load_seen_links()
    new_opportunities: List[Opportunity] = []

    for url in feed_urls:
        parsed = feedparser.parse(url)

        if parsed.bozo and not parsed.entries:
            # Feed failed to parse and returned nothing usable; skip it
            # rather than crashing the whole run.
            print(f"  [warn] could not read feed: {url}")
            continue

        source_name = parsed.feed.get("title", url)

        for entry in parsed.entries:
            link = entry.get("link", "")
            if not link or link in seen_links:
                continue

            new_opportunities.append(
                Opportunity(
                    title=entry.get("title", "Untitled"),
                    link=link,
                    summary=entry.get("summary", "")[:500],
                    source=source_name,
                    published=entry.get("published", ""),
                )
            )
            seen_links.add(link)

    if mark_as_seen:
        _save_seen_links(seen_links)

    return new_opportunities
