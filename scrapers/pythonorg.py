"""
Python.org Jobs scraper.
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


class PythonOrgScraper(BaseScraper):
    URL = "https://www.python.org/jobs/feed/rss/"
    _html_tags = re.compile(r"<[^>]+>")
    _whitespace = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Python.org...")

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
            
            # The location is often the first line of the description before HTML tags
            country = "Worldwide"
            if description_html and not description_html.startswith("<"):
                first_line = description_html.split("\n")[0].strip()
                if first_line and len(first_line) < 50:
                    country = first_line

            jobs.append(
                Job(
                    title=title,
                    company=company,
                    description=description,
                    url=(item.findtext("link") or "").strip(),
                    posted_at=posted_at,
                    salary="Not specified",
                    country=country,
                    remote=True,  # Most python.org jobs allow remote, or we assume true for search purposes
                    source="Python.org",
                )
            )

        logger.info("Fetched %d Python.org jobs.", len(jobs))
        return jobs

    def _split_company_and_title(self, value: str) -> tuple[str, str]:
        # Usually "Title, Company" or "Title at Company"
        parts = [part.strip() for part in value.rsplit(",", 1)]
        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[1], parts[0]
            
        parts = [part.strip() for part in value.rsplit(" at ", 1)]
        if len(parts) == 2 and parts[0] and parts[1]:
            return parts[1], parts[0]

        return "Unknown Company", value.strip()

    def _clean_description(self, value: str) -> str:
        value = html.unescape(value)
        value = self._html_tags.sub(" ", value)
        value = self._whitespace.sub(" ", value)
        return value.strip()
