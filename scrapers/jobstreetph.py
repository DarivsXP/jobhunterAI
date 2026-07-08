"""
JobStreet Philippines Scraper

JobStreet is Southeast Asia's largest job board (owned by SEEK).
Uses their public search endpoint to scrape remote/WFH tech roles in PH.
Falls back gracefully if the API shape changes.
"""

from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class JobStreetPhScraper(BaseScraper):
    _SEARCH_URL = "https://www.jobstreet.com.ph/jobs"
    _WHITESPACE = re.compile(r"\s+")

    # Queries targeting Cyril's roles; work-from-home filter applied via URL param
    _QUERIES = [
        "software engineer remote",
        "backend developer remote",
        "full stack developer remote",
        "php developer remote",
        "laravel developer remote",
        "python developer remote",
        "web developer remote",
        "technical support remote",
        "application support remote",
    ]

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from JobStreet PH...")
        all_jobs: list[Job] = []
        seen_urls: set[str] = set()

        for query in self._QUERIES:
            try:
                response = requests.get(
                    self._SEARCH_URL,
                    params={
                        "q": query,
                        "work-type": "remote",         # JobStreet WFH filter
                        "page": 1,
                    },
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        ),
                        "Accept-Language": "en-PH,en;q=0.9",
                    },
                    timeout=25,
                )
                response.raise_for_status()
            except Exception:
                logger.exception("JobStreet PH request failed for query '%s'.", query)
                continue

            try:
                soup = BeautifulSoup(response.text, "html.parser")

                # JobStreet renders job cards as articles or divs with data-job-id
                job_cards = soup.select(
                    "article[data-job-id], div[data-job-id], "
                    "[data-automation='job-card'], [data-testid='job-card']"
                )

                for card in job_cards:
                    job_id = card.get("data-job-id", "")

                    # Title
                    title_el = card.select_one(
                        "h1, h2, h3, "
                        "[data-automation='job-title'], "
                        "[data-testid='job-title'], "
                        "a[href*='/job/']"
                    )
                    title = self._clean(title_el.get_text()) if title_el else ""
                    if not title:
                        continue

                    # URL
                    link_el = card.select_one("a[href*='/job/'], a[href*='/jobs/']")
                    if link_el and link_el.get("href"):
                        href = link_el["href"]
                        url = href if href.startswith("http") else f"https://www.jobstreet.com.ph{href}"
                    elif job_id:
                        url = f"https://www.jobstreet.com.ph/job/{job_id}"
                    else:
                        continue

                    if url in seen_urls:
                        continue
                    seen_urls.add(url)

                    # Company
                    company_el = card.select_one(
                        "[data-automation='job-company'], "
                        "[data-testid='company-name'], "
                        "[class*='company']"
                    )
                    company = self._clean(company_el.get_text()) if company_el else "Unknown"

                    # Description snippet
                    desc_el = card.select_one(
                        "[data-automation='job-description-text'], "
                        "[class*='description'], p"
                    )
                    description = self._clean(desc_el.get_text()) if desc_el else ""

                    # Salary
                    salary_el = card.select_one("[data-automation='job-salary'], [class*='salary']")
                    salary = self._clean(salary_el.get_text()) if salary_el else "Not specified"

                    # Posted date
                    date_el = card.select_one("[data-automation='job-listed-date'], time, [class*='date']")
                    posted_at = date_el.get("datetime", self._clean(date_el.get_text())) if date_el else "Unknown"

                    all_jobs.append(
                        Job(
                            title=title,
                            company=company,
                            description=description,
                            url=url,
                            posted_at=posted_at,
                            salary=salary,
                            country="Philippines",
                            remote=True,
                            source="JobStreet PH",
                        )
                    )

            except Exception:
                logger.exception("JobStreet PH parsing failed for query '%s'.", query)
                continue

        logger.info("Fetched %d JobStreet PH jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        return self._WHITESPACE.sub(" ", (value or "")).strip()
