"""
VueJobs scraper.
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


class VueJobsScraper(BaseScraper):
    URL = "https://vuejobs.com/feed/posts"
    _html_tags = re.compile(r"<[^>]+>")
    _whitespace = re.compile(r"\s+")
    _employer_pattern = re.compile(r"<strong>Employer:</strong>\s*([^<]+)")
    _location_pattern = re.compile(r"<strong>Location:</strong>\s*([^<]+)")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from VueJobs...")

        try:
            response = requests.get(
                self.URL,
                headers={"User-Agent": "JobHunterAI/1.0"},
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch VueJobs: {e}")
            return []

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logger.error(f"Failed to parse VueJobs XML: {e}")
            return []

        jobs: list[Job] = []

        for item in root.findall("./channel/item"):
            title = (item.findtext("title") or "").strip()
            description_html = item.findtext("description") or ""
            
            employer_match = self._employer_pattern.search(description_html)
            company = employer_match.group(1).strip() if employer_match else "Unknown Company"
            
            location_match = self._location_pattern.search(description_html)
            country = location_match.group(1).strip() if location_match else "Worldwide"
            
            description = self._clean_description(description_html)
            posted_at = (item.findtext("pubDate") or "").strip()
            url = (item.findtext("link") or "").strip()
            
            remote = True
            if "remote" not in country.lower() and "remote" not in title.lower() and "remote" not in description.lower():
                remote = False

            jobs.append(
                Job(
                    title=title,
                    company=company,
                    description=description,
                    url=url,
                    posted_at=posted_at,
                    salary="Not specified",
                    country=country or "Worldwide",
                    remote=remote,
                    source="VueJobs",
                )
            )

        logger.info("Fetched %d VueJobs jobs.", len(jobs))
        return jobs

    def _clean_description(self, value: str) -> str:
        value = html.unescape(value)
        value = self._html_tags.sub(" ", value)
        value = self._whitespace.sub(" ", value)
        return value.strip()
