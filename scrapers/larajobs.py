"""
LaraJobs scraper.
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


class LaraJobsScraper(BaseScraper):
    URL = "https://larajobs.com/feed"
    _html_tags = re.compile(r"<[^>]+>")
    _whitespace = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from LaraJobs...")

        try:
            response = requests.get(
                self.URL,
                headers={"User-Agent": "JobHunterAI/1.0"},
                timeout=30,
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch LaraJobs: {e}")
            return []

        namespaces = {
            'dc': 'http://purl.org/dc/elements/1.1/',
            'ns1': 'https://larajobs.com',
            'ns2': 'http://purl.org/rss/1.0/modules/content/'
        }

        try:
            root = ET.fromstring(response.text)
        except ET.ParseError as e:
            logger.error(f"Failed to parse LaraJobs XML: {e}")
            return []

        jobs: list[Job] = []

        for item in root.findall("./channel/item"):
            title = (item.findtext("title") or "").strip()
            
            # Company can be in dc:creator or ns1:company
            company = item.findtext("dc:creator", namespaces=namespaces)
            if not company:
                company = item.findtext("ns1:company", namespaces=namespaces) or "Unknown Company"
                
            # Location can be in ns1:location
            country = item.findtext("ns1:location", namespaces=namespaces) or "Worldwide"
            
            description_html = item.findtext("ns2:encoded", namespaces=namespaces)
            if not description_html:
                description_html = item.findtext("description") or ""
                
            description = self._clean_description(description_html)
            posted_at = (item.findtext("pubDate") or "").strip()
            url = (item.findtext("link") or "").strip()
            
            remote = True
            if "remote" not in country.lower() and "remote" not in title.lower() and "remote" not in description.lower():
                remote = False

            jobs.append(
                Job(
                    title=title,
                    company=company.strip(),
                    description=description,
                    url=url,
                    posted_at=posted_at,
                    salary="Not specified",
                    country=country.strip() or "Worldwide",
                    remote=remote,
                    source="LaraJobs",
                )
            )

        logger.info("Fetched %d LaraJobs jobs.", len(jobs))
        return jobs

    def _clean_description(self, value: str) -> str:
        value = html.unescape(value)
        value = self._html_tags.sub(" ", value)
        value = self._whitespace.sub(" ", value)
        return value.strip()
