"""
Arc.dev Scraper
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class ArcDevScraper(BaseScraper):
    _URL = "https://arc.dev/remote-developer-jobs"
    _BASE_URL = "https://arc.dev"
    _WHITESPACE = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Arc.dev...")
        all_jobs: list[Job] = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(self._URL, wait_until="networkidle", timeout=30000)
                
                try:
                    page.wait_for_selector('div[class*="job-card"], a[class*="job-card"], .job-list-item, a[href*="/remote-jobs/"]', timeout=10000)
                except Exception:
                    logger.warning("Arc.dev: timed out waiting for job elements")

                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            
            # Arc.dev jobs are typically within div or a elements with job-related classes
            job_cards = soup.select('div[class*="job-card"], a[class*="job-card"], .job-list-item')
            
            # Fallback if specific classes aren't found, look for generic links to jobs
            if not job_cards:
                job_cards = soup.find_all('a', href=re.compile(r'/remote-jobs/'))

            seen_urls = set()

            for card in job_cards:
                if card.name == 'a' and 'href' in card.attrs:
                    url_elem = card
                else:
                    url_elem = card.find('a', href=re.compile(r'/remote-jobs/'))

                if not url_elem:
                    continue

                url = url_elem['href']
                if url.startswith('/'):
                    url = self._BASE_URL + url
                
                if url in seen_urls:
                    continue
                seen_urls.add(url)

                title_elem = card.find(['h2', 'h3', 'h4', 'div'], class_=re.compile(r'title', re.I)) or url_elem
                title = self._clean(title_elem.get_text()) if title_elem else "Developer"

                company_elem = card.find(class_=re.compile(r'company', re.I))
                company = self._clean(company_elem.get_text()) if company_elem else "Unknown"

                desc_elem = card.find(class_=re.compile(r'desc', re.I))
                description = self._clean(desc_elem.get_text()) if desc_elem else ""

                all_jobs.append(
                    Job(
                        title=title,
                        company=company,
                        description=description,
                        url=url,
                        posted_at="Unknown",
                        salary="Not specified",
                        country="Worldwide",
                        remote=True,
                        source="Arc.dev",
                    )
                )

        except Exception:
            logger.exception("Arc.dev request failed")

        logger.info("Fetched %d Arc.dev jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        return self._WHITESPACE.sub(" ", value).strip()
