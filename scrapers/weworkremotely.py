"""
We Work Remotely scraper.
"""

from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class WeWorkRemotelyScraper(BaseScraper):
    URL = "https://weworkremotely.com/remote-jobs.rss"
    _html_tags = re.compile(r"<[^>]+>")
    _whitespace = re.compile(r"\s+")
    _headquarters = re.compile(
        r"Headquarters:\s*</strong>\s*([^<]+)",
        re.IGNORECASE,
    )

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from We Work Remotely...")

        response = requests.get(
            self.URL,
            headers={"User-Agent": "JobHunterAI/1.0"},
            timeout=30,
        )
        response.raise_for_status()

        root = ET.fromstring(response.text)
        jobs: list[Job] = []

        for item in root.findall("./channel/item"):
            raw_title = (item.findtext("title") or "").strip()
            description_html = item.findtext("description") or ""
            company, title = self._split_company_and_title(raw_title)
            description = self._clean_description(description_html)
            posted_at = (item.findtext("pubDate") or "").strip()
            country = self._extract_headquarters(description_html)

            jobs.append(
                Job(
                    title=title,
                    company=company,
                    description=description,
                    url=(item.findtext("link") or "").strip(),
                    posted_at=posted_at,
                    salary="Not specified",
                    country=country or "Worldwide",
                    remote=True,
                    source="WeWorkRemotely",
                )
            )

        logger.info("Fetched %d We Work Remotely jobs.", len(jobs))
        return jobs

    def _split_company_and_title(self, value: str) -> tuple[str, str]:
        parts = [part.strip() for part in value.split(":", 1)]

        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[0], parts[1]

        return "Unknown Company", value.strip()

    def _extract_headquarters(self, value: str) -> str:
        match = self._headquarters.search(value)

        if not match:
            return "Worldwide"

        return self._clean_description(match.group(1))

    def _clean_description(self, value: str) -> str:
        value = html.unescape(value)
        value = self._html_tags.sub(" ", value)
        value = self._whitespace.sub(" ", value)
        return value.strip()
