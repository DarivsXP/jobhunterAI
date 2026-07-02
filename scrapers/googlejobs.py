"""
Google Jobs Scraper via Playwright
"""

from __future__ import annotations

import os
import re
import time

from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class GoogleJobsScraper(BaseScraper):
    _URL = "https://www.google.com/search?q=remote+developer+jobs&ibp=htl;jobs"
    _WHITESPACE = re.compile(r"\s+")
    _STATE_FILE = "google_auth_state.json"

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Google Jobs...")
        all_jobs: list[Job] = []

        try:
            with sync_playwright() as p:
                # We run headful (headless=False) so you can manually solve the CAPTCHA if needed
                browser = p.chromium.launch(headless=False)
                
                # Load previous session state if it exists to bypass CAPTCHA
                context_args = {}
                if os.path.exists(self._STATE_FILE):
                    context_args["storage_state"] = self._STATE_FILE
                    
                context = browser.new_context(**context_args)
                page = context.new_page()
                
                # Add stealth-like headers/user-agent
                page.set_extra_http_headers({
                    "Accept-Language": "en-US,en;q=0.9",
                })

                page.goto(self._URL)
                
                # Wait for either job listings or a CAPTCHA to appear
                try:
                    page.wait_for_selector('div[role="treeitem"], form#captcha-form', timeout=15000)
                except Exception:
                    logger.warning("Google Jobs: timed out waiting for job elements or CAPTCHA")

                # If CAPTCHA is present, wait for the user to manually solve it
                if page.locator('form#captcha-form').count() > 0 or "unusual traffic" in page.content():
                    logger.warning("Google CAPTCHA detected! Please solve it in the browser window.")
                    logger.warning("Waiting up to 60 seconds for manual CAPTCHA solve...")
                    try:
                        page.wait_for_selector('div[role="treeitem"]', timeout=60000)
                        logger.info("CAPTCHA solved successfully. Saving session state.")
                        context.storage_state(path=self._STATE_FILE)
                    except Exception:
                        logger.error("Failed to solve CAPTCHA in time.")
                        browser.close()
                        return []
                else:
                    # Save state for future runs
                    context.storage_state(path=self._STATE_FILE)

                # Scroll to load a few more jobs
                for _ in range(3):
                    page.mouse.wheel(0, 2000)
                    time.sleep(1)

                html = page.content()
                browser.close()

            soup = BeautifulSoup(html, "html.parser")
            
            # Google Jobs cards are typically marked with role="treeitem"
            job_cards = soup.find_all('div', role='treeitem')

            for card in job_cards:
                text_content = card.get_text(separator='\n').split('\n')
                text_content = [t.strip() for t in text_content if t.strip()]

                if not text_content:
                    continue

                # The first item is usually the title, second is company
                title = self._clean(text_content[0]) if len(text_content) > 0 else "Developer"
                company = self._clean(text_content[1]) if len(text_content) > 1 else "Unknown"
                
                # Find salary/location markers if they exist
                salary = "Not specified"
                for text in text_content:
                    if re.search(r'\$|K\b|PHP|year|month|hour', text, re.I):
                        salary = self._clean(text)
                        break

                description = " ".join(text_content[2:10]) if len(text_content) > 2 else ""

                all_jobs.append(
                    Job(
                        title=title,
                        company=company,
                        description=description,
                        url=self._URL,  # Google Jobs doesn't expose direct cleanly, linking back to search
                        posted_at="Unknown",
                        salary=salary,
                        country="Worldwide",
                        remote=True,
                        source="Google Jobs",
                    )
                )

        except Exception:
            logger.exception("Google Jobs request failed")

        logger.info("Fetched %d Google jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        return self._WHITESPACE.sub(" ", value).strip()
