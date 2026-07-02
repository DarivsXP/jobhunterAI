"""
JustRemote Scraper

JustRemote is a client-side rendered app.
Uses Playwright to render the page before scraping.
"""

from __future__ import annotations

import re

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class JustRemoteScraper(BaseScraper):
    _URL = "https://justremote.co/remote-developer-jobs"
    _BASE_URL = "https://justremote.co"
    _WHITESPACE = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from JustRemote...")
        all_jobs: list[Job] = []

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                page.goto(self._URL, wait_until="networkidle", timeout=30000)
                
                # Wait for job listings to appear
                try:
                    page.wait_for_selector('div[class*="job-item"], div[class*="job-card"], a[href*="/remote-jobs/"]', timeout=10000)
                except Exception:
                    logger.warning("JustRemote: timed out waiting for job elements")

                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            
            job_cards = soup.select('div[class*="job"], div[class*="item"]')
            
            seen_urls = set()

            for card in job_cards:
                url_elem = card.find('a', href=re.compile(r'/remote-jobs/'))
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

                desc_elem = card.find(class_=re.compile(r'desc', re.I)) or card.find('p')
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
                        source="JustRemote",
                    )
                )

        except Exception:
            logger.exception("JustRemote request failed")

        logger.info("Fetched %d JustRemote jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        return self._WHITESPACE.sub(" ", value).strip()

