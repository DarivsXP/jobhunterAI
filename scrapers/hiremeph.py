"""
HireMe.ph Scraper
"""

from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class HireMePhScraper(BaseScraper):
    _URL = "https://hireme.ph/jobs"
    _BASE_URL = "https://hireme.ph"
    _WHITESPACE = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from HireMe.ph...")
        all_jobs: list[Job] = []

        try:
            response = requests.get(
                self._URL,
                headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
                timeout=15,
                verify=False, # Required for some PH boards due to misconfigured SSL
            )
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            
            job_cards = soup.select('div[class*="job"], article[class*="job"], .job-item')
            
            seen_urls = set()

            for card in job_cards:
                url_elem = card.find('a', href=re.compile(r'/job/|/jobs/'))

                if not url_elem:
                    continue

                url = url_elem['href']
                if url.startswith('/'):
                    url = self._BASE_URL + url
                
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title_elem = card.find(['h2', 'h3', 'h4']) or url_elem
                title = self._clean(title_elem.get_text()) if title_elem else "Developer"

                company_elem = card.find(class_=re.compile(r'company', re.I))
                company = self._clean(company_elem.get_text()) if company_elem else "Unknown"

                desc_elem = card.find(class_=re.compile(r'desc|summary', re.I)) or card.find('p')
                description = self._clean(desc_elem.get_text()) if desc_elem else ""

                all_jobs.append(
                    Job(
                        title=title,
                        company=company,
                        description=description,
                        url=url,
                        posted_at="Unknown",
                        salary="Not specified",
                        country="Philippines",
                        remote=True,
                        source="HireMe.ph",
                    )
                )

        except Exception:
            logger.exception("HireMe.ph request failed")

        logger.info("Fetched %d HireMe.ph jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        return self._WHITESPACE.sub(" ", value).strip()
