"""
Jobicy Scraper

Fetches remote jobs from Jobicy's public API.
Makes two passes:
  1. Global feed (no geo filter) — worldwide remote jobs
  2. Asia feed (geo=asia) — jobs explicitly tagged for the Asia region,
     which includes Philippines, India, SE Asia, etc.
"""

from __future__ import annotations

from typing import List

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class JobicyScraper(BaseScraper):
    BASE_URL = "https://jobicy.com/api/v2/remote-jobs"

    # Geo tags Jobicy supports that are relevant for PH/India/Asia
    GEO_FEEDS = [
        ("Worldwide", None),          # No geo filter — global remote jobs
        ("Asia", "asia"),             # Asia region — covers PH, India, SE Asia
        ("Philippines", "philippines"),
        ("India", "india"),
    ]

    def fetch_jobs(self) -> List[Job]:
        logger.info("Fetching jobs from Jobicy (global + Asia/PH/India feeds)...")

        seen_urls: set[str] = set()
        jobs: List[Job] = []

        for label, geo in self.GEO_FEEDS:
            feed_jobs = self._fetch_feed(geo=geo, label=label)
            for job in feed_jobs:
                # Deduplicate by URL across all feeds
                if job.url and job.url not in seen_urls:
                    seen_urls.add(job.url)
                    jobs.append(job)

        logger.info("Fetched %d unique Jobicy jobs across all feeds.", len(jobs))
        return jobs

    def _fetch_feed(self, geo: str | None, label: str) -> List[Job]:
        params: dict = {"count": 100}
        if geo:
            params["geo"] = geo

        try:
            response = requests.get(
                self.BASE_URL,
                params=params,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    )
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except Exception:
            logger.exception("Jobicy request failed for geo=%s.", geo)
            return []

        if not data or "jobs" not in data:
            logger.warning("Jobicy returned no jobs or invalid structure for geo=%s.", geo)
            return []

        jobs: List[Job] = []
        for item in data["jobs"]:
            salary_min = item.get("salaryMin")
            salary_max = item.get("salaryMax")
            salary_curr = item.get("salaryCurrency", "USD")
            salary_period = item.get("salaryPeriod", "yearly")

            if salary_min and salary_max:
                salary = f"{salary_min} - {salary_max} {salary_curr}/{salary_period}"
            elif salary_min:
                salary = f"{salary_min}+ {salary_curr}/{salary_period}"
            else:
                salary = "Not specified"

            # Use the explicit jobGeo from the API; fall back to our feed label
            country = item.get("jobGeo") or label or "Worldwide"

            jobs.append(
                Job(
                    title=item.get("jobTitle", ""),
                    company=item.get("companyName", ""),
                    description=item.get("jobDescription", ""),
                    url=item.get("url", ""),
                    posted_at=str(item.get("pubDate", "")),
                    salary=salary,
                    country=country,
                    remote=True,
                    source="Jobicy",
                )
            )

        logger.info("  [Jobicy/%s] Fetched %d jobs.", label, len(jobs))
        return jobs
