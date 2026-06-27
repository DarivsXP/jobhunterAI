"""
Arbeitnow Scraper

Free public API — no API key required.
https://www.arbeitnow.com/api/job-board-api
"""

from __future__ import annotations

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class ArbeitnowScraper(BaseScraper):
    BASE_URL = "https://www.arbeitnow.com/api/job-board-api"

    # Fetch the first 2 pages (20 jobs/page = up to 200 jobs)
    _MAX_PAGES = 2

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Arbeitnow...")

        all_jobs: list[Job] = []
        seen_slugs: set[str] = set()

        for page in range(1, self._MAX_PAGES + 1):
            try:
                response = requests.get(
                    self.BASE_URL,
                    params={"page": page},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                    timeout=30,
                )
                response.raise_for_status()
                data = response.json()

                items = data.get("data", [])
                if not items:
                    break  # No more pages

                for item in items:
                    slug = item.get("slug", "")
                    if slug in seen_slugs:
                        continue
                    seen_slugs.add(slug)

                    # Arbeitnow returns unix timestamp for created_at
                    posted_raw = item.get("created_at", "")
                    posted_at = str(posted_raw) if posted_raw else ""

                    # Build salary string
                    salary_from = item.get("salary_from")
                    salary_to = item.get("salary_to")
                    salary_currency = item.get("salary_currency", "EUR")
                    if salary_from and salary_to:
                        salary = f"{salary_from} - {salary_to} {salary_currency}"
                    elif salary_from:
                        salary = f"{salary_from}+ {salary_currency}"
                    else:
                        salary = "Not specified"

                    # Location / remote flag
                    remote = item.get("remote", True)
                    location = item.get("location", "Worldwide") or "Worldwide"

                    all_jobs.append(
                        Job(
                            title=item.get("title", ""),
                            company=item.get("company_name", ""),
                            description=item.get("description", ""),
                            url=item.get("url", ""),
                            posted_at=posted_at,
                            salary=salary,
                            country=location,
                            remote=bool(remote),
                            source="Arbeitnow",
                        )
                    )

            except Exception:
                logger.exception("Arbeitnow request failed on page %d", page)
                break

        logger.info("Fetched %d Arbeitnow jobs.", len(all_jobs))
        return all_jobs
