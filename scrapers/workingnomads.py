"""
Working Nomads Scraper

Free public JSON API — no key required.
Developer category: https://www.workingnomads.com/api/exposed_jobs/?category=development
"""

from __future__ import annotations

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class WorkingNomadsScraper(BaseScraper):
    # Fetch developer-specific jobs directly
    _CATEGORIES = [
        "development",
        "web-development",
        "php",
    ]
    BASE_URL = "https://www.workingnomads.com/api/exposed_jobs/"

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Working Nomads...")

        all_jobs: list[Job] = []
        seen_urls: set[str] = set()

        for category in self._CATEGORIES:
            try:
                response = requests.get(
                    self.BASE_URL,
                    params={"category": category},
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                    timeout=30,
                )
                response.raise_for_status()
                items = response.json()

                if not isinstance(items, list):
                    logger.warning("Working Nomads returned unexpected format for %s", category)
                    continue

                for item in items:
                    job_url = item.get("url", "")
                    if not job_url or job_url in seen_urls:
                        continue
                    seen_urls.add(job_url)

                    # location can be a string like "Worldwide", "USA", "Europe", etc.
                    location = item.get("location", "Worldwide") or "Worldwide"

                    all_jobs.append(
                        Job(
                            title=item.get("title", ""),
                            company=item.get("company_name", ""),
                            description=item.get("description", ""),
                            url=job_url,
                            posted_at=str(item.get("pub_date", "")),
                            salary="Not specified",
                            country=location,
                            remote=True,  # Working Nomads is remote-only by definition
                            source="WorkingNomads",
                        )
                    )

            except Exception:
                logger.exception("Working Nomads request failed for category: %s", category)

        logger.info("Fetched %d Working Nomads jobs.", len(all_jobs))
        return all_jobs
