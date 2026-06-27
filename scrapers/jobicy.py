"""
Jobicy Scraper
"""

from __future__ import annotations

from typing import List

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class JobicyScraper(BaseScraper):
    URL = "https://jobicy.com/api/v2/remote-jobs?count=100"

    def fetch_jobs(self) -> List[Job]:
        logger.info("Fetching jobs from Jobicy...")

        try:
            response = requests.get(
                self.URL,
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()
        except Exception:
            logger.exception("Jobicy request failed.")
            return []

        if not data or "jobs" not in data:
            logger.warning("Jobicy returned no jobs or invalid structure.")
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

            jobs.append(
                Job(
                    title=item.get("jobTitle", ""),
                    company=item.get("companyName", ""),
                    description=item.get("jobDescription", ""),
                    url=item.get("url", ""),
                    posted_at=str(item.get("pubDate", "")),
                    salary=salary,
                    country=item.get("jobGeo", "Worldwide"),
                    remote=True,
                    source="Jobicy",
                )
            )

        logger.info("Fetched %d Jobicy jobs.", len(jobs))
        return jobs
