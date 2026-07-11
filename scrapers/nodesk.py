"""
NoDesk Scraper

NoDesk is a curated remote job board with a public RSS feed.
No API key needed.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class NoDeskScraper(BaseScraper):
    _FEEDS = [
        ("https://nodesk.co/remote-jobs/engineering/feed/", "Engineering"),
        ("https://nodesk.co/remote-jobs/developer/feed/", "Developer"),
    ]
    _html_tags = re.compile(r"<[^>]+>")
    _whitespace = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from NoDesk...")

        all_jobs: list[Job] = []
        seen_urls: set[str] = set()

        for feed_url, category in self._FEEDS:
            try:
                response = requests.get(
                    feed_url,
                    headers={"User-Agent": "JobHunterAI/1.0"},
                    timeout=(8, 12),
                )
                response.raise_for_status()
                root = ET.fromstring(response.text)

                for item in root.findall("./channel/item"):
                    url = (item.findtext("link") or "").strip()
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = (item.findtext("title") or "").strip()
                    if not title:
                        continue

                    description_raw = item.findtext("description") or ""
                    description = self._clean(description_raw)
                    posted_at = (item.findtext("pubDate") or "").strip()

                    company = (
                        item.findtext("{http://purl.org/dc/elements/1.1/}creator") or ""
                    ).strip() or "Unknown"

                    all_jobs.append(
                        Job(
                            title=title,
                            company=company,
                            description=description,
                            url=url,
                            posted_at=posted_at,
                            salary="Not specified",
                            country="Worldwide",
                            remote=True,
                            source="NoDesk",
                        )
                    )

            except Exception:
                logger.exception("NoDesk request failed for %s", feed_url)

        logger.info("Fetched %d NoDesk jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        value = self._html_tags.sub(" ", value)
        return self._whitespace.sub(" ", value).strip()
