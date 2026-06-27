"""
Remote.co Scraper

Parses the curated RSS feed for developer jobs.
https://remote.co/remote-jobs/developer/feed/
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class RemoteCoScraper(BaseScraper):
    _FEED_URLS = [
        "https://remote.co/remote-jobs/developer/feed/",
        "https://remote.co/remote-jobs/customer-service/feed/",
    ]
    _html_tags = re.compile(r"<[^>]+>")
    _whitespace = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Remote.co...")

        all_jobs: list[Job] = []
        seen_urls: set[str] = set()

        for feed_url in self._FEED_URLS:
            try:
                response = requests.get(
                    feed_url,
                    headers={"User-Agent": "JobHunterAI/1.0"},
                    timeout=15,
                )
                response.raise_for_status()
                root = ET.fromstring(response.text)

                for item in root.findall("./channel/item"):
                    url = (item.findtext("link") or "").strip()
                    if not url or url in seen_urls:
                        continue
                    seen_urls.add(url)

                    title = (item.findtext("title") or "").strip()
                    description_raw = item.findtext("description") or ""
                    description = self._clean(description_raw)
                    posted_at = (item.findtext("pubDate") or "").strip()

                    # Try to extract company from the <author> or description
                    company = (item.findtext("author") or "").strip()
                    if not company:
                        creator = item.findtext(
                            "{http://purl.org/dc/elements/1.1/}creator"
                        ) or ""
                        company = creator.strip() or "Unknown"

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
                            source="Remote.co",
                        )
                    )

            except Exception:
                logger.exception("Remote.co request failed for %s", feed_url)

        logger.info("Fetched %d Remote.co jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        value = self._html_tags.sub(" ", value)
        return self._whitespace.sub(" ", value).strip()
