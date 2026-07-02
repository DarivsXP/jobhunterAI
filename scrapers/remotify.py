"""
Remotify.ph Scraper
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class RemotifyScraper(BaseScraper):
    _URL = "https://remotify.ph/jobs"
    _BASE_URL = "https://remotify.ph"
    _WHITESPACE = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Remotify.ph...")
        all_jobs: list[Job] = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(self._URL, wait_until="networkidle", timeout=30000)
                
                try:
                    page.wait_for_selector('div[class*="job"], article[class*="job"], .job-item, .card', timeout=10000)
                except Exception:
                    logger.warning("Remotify.ph: timed out waiting for job elements")

                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            
            job_cards = soup.select('div[class*="job"], article[class*="job"], .job-item, .card')
            
            seen_urls = set()

            for card in job_cards:
                url_elem = card.find('a', href=re.compile(r'/job/|/careers/'))

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

                salary_elem = card.find(string=re.compile(r'\$|PHP|php|k\b', re.I))
                salary = self._clean(salary_elem) if salary_elem else "Not specified"

                all_jobs.append(
                    Job(
                        title=title,
                        company=company,
                        description=description,
                        url=url,
                        posted_at="Unknown",
                        salary=salary,
                        country="Philippines",
                        remote=True,
                        source="Remotify.ph",
                    )
                )

        except Exception:
            logger.exception("Remotify.ph request failed")

        logger.info("Fetched %d Remotify.ph jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        return self._WHITESPACE.sub(" ", value).strip()
