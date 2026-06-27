"""
JobsCollider Scraper
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class JobsColliderScraper(BaseScraper):
    URL = "https://jobscollider.com/remote-jobs.rss"
    _html_tags = re.compile(r"<[^>]+>")
    _whitespace = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from JobsCollider...")

        jobs: list[Job] = []

        try:
            response = requests.get(
                self.URL,
                headers={"User-Agent": "JobHunterAI/1.0"},
                timeout=30,
            )
            response.raise_for_status()

            # Sometimes RSS feeds have namespace issues, we can just parse it directly if it's simple
            root = ET.fromstring(response.content)

            for item in root.findall(".//item"):
                raw_title = (item.findtext("title") or "").strip()
                url = (item.findtext("link") or "").strip()
                description_raw = item.findtext("description") or ""
                description = self._clean(description_raw)
                posted_at = (item.findtext("pubDate") or "").strip()

                # Extract company from title if format is "Role at Company"
                title = raw_title
                company = "Unknown"
                if " at " in raw_title:
                    parts = raw_title.rsplit(" at ", 1)
                    title = parts[0].strip()
                    company = parts[1].strip()

                jobs.append(
                    Job(
                        title=title,
                        company=company,
                        description=description,
                        url=url,
                        posted_at=posted_at,
                        salary="Not specified",
                        country="Worldwide",
                        remote=True,
                        source="JobsCollider",
                    )
                )

        except Exception:
            logger.exception("JobsCollider request failed.")

        logger.info("Fetched %d JobsCollider jobs.", len(jobs))
        return jobs

    def _clean(self, value: str) -> str:
        value = self._html_tags.sub(" ", value)
        return self._whitespace.sub(" ", value).strip()
