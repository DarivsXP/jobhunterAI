"""
Hubstaff Talent Scraper
"""

from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class HubstaffTalentScraper(BaseScraper):
    _URL = "https://talent.hubstaff.com/search/jobs?search=developer"
    _BASE_URL = "https://talent.hubstaff.com"
    _WHITESPACE = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Hubstaff Talent...")
        all_jobs: list[Job] = []

        try:
            response = requests.get(
                self._URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=15,
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            
            # Hubstaff jobs are typically loaded dynamically or within specific containers.
            # We will attempt to find common job card containers.
            job_cards = soup.select('div.job-result, div[class*="job-card"], a[href*="/jobs/"]')
            
            seen_urls = set()

            for card in job_cards:
                # If the card itself is an anchor, or contains an anchor
                if card.name == 'a' and 'href' in card.attrs:
                    url_elem = card
                else:
                    url_elem = card.find('a', href=re.compile(r'/jobs/'))

                if not url_elem:
                    continue

                url = url_elem['href']
                if url.startswith('/'):
                    url = self._BASE_URL + url
                
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title_elem = card.find(['h3', 'h4', 'h2']) or url_elem
                title = self._clean(title_elem.get_text()) if title_elem else "Developer"

                desc_elem = card.select_one('.description, p')
                description = self._clean(desc_elem.get_text()) if desc_elem else ""

                all_jobs.append(
                    Job(
                        title=title,
                        company="Unknown",
                        description=description,
                        url=url,
                        posted_at="Unknown",
                        salary="Not specified",
                        country="Worldwide",
                        remote=True,
                        source="Hubstaff Talent",
                    )
                )

        except Exception:
            logger.exception("Hubstaff Talent request failed")

        logger.info("Fetched %d Hubstaff Talent jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        return self._WHITESPACE.sub(" ", value).strip()
