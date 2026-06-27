"""
Himalayas Scraper
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class HimalayasScraper(BaseScraper):
    URL = "https://himalayas.app/jobs/rss"
    _prefix_cleaner = re.compile(r"([</?])[a-zA-Z0-9]+:", re.IGNORECASE)

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Himalayas...")

        response = requests.get(
            self.URL,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            timeout=30,
        )
        response.raise_for_status()

        # Clean namespaces so ElementTree can parse it without namespace configuration errors
        xml_clean = self._prefix_cleaner.sub(r"\1", response.text)
        root = ET.fromstring(xml_clean)

        jobs: list[Job] = []

        for item in root.findall(".//item"):
            title = (item.findtext("title") or "").strip()
            company = (item.findtext("companyName") or "").strip()
            description = (item.findtext("description") or "").strip()
            url = (item.findtext("link") or "").strip()
            posted_at = (item.findtext("pubDate") or "").strip()
            country = (item.findtext("locationRestriction") or "Worldwide").strip()

            jobs.append(
                Job(
                    title=title,
                    company=company,
                    description=description,
                    url=url,
                    posted_at=posted_at,
                    salary="Not specified",
                    country=country,
                    remote=True,
                    source="Himalayas",
                )
            )

        logger.info("Fetched %d Himalayas jobs.", len(jobs))
        return jobs
