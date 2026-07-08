"""
Kalibrr Scraper

Kalibrr is one of the Philippines' leading job boards.
Uses their public job search API — no key required.
Only fetches remote/WFH-tagged jobs.
"""

from __future__ import annotations

import re

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class KalibrrScraper(BaseScraper):
    _BASE_URL = "https://www.kalibrr.com/api/te/job-ads"
    _WHITESPACE = re.compile(r"\s+")

    # Search terms that cover Cyril's target roles
    _SEARCH_TERMS = [
        "software engineer",
        "backend developer",
        "full stack developer",
        "php developer",
        "laravel developer",
        "python developer",
        "web developer",
        "technical support",
        "application support",
    ]

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Kalibrr...")
        all_jobs: list[Job] = []
        seen_ids: set[str] = set()

        for term in self._SEARCH_TERMS:
            try:
                response = requests.get(
                    self._BASE_URL,
                    params={
                        "limit": 20,
                        "offset": 0,
                        "keyword": term,
                        "is_remote": True,
                    },
                    headers={
                        "User-Agent": (
                            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        ),
                        "Accept": "application/json",
                        "Referer": "https://www.kalibrr.com/",
                    },
                    timeout=20,
                )
                response.raise_for_status()
                data = response.json()
            except Exception:
                logger.exception("Kalibrr request failed for term '%s'.", term)
                continue

            jobs_list = data if isinstance(data, list) else data.get("data", data.get("jobs", []))
            if not isinstance(jobs_list, list):
                logger.warning("Kalibrr: unexpected response structure for '%s'.", term)
                continue

            for item in jobs_list:
                job_id = str(item.get("id", "") or item.get("code", ""))
                if not job_id or job_id in seen_ids:
                    continue
                seen_ids.add(job_id)

                title = self._clean(item.get("title") or item.get("position") or "")
                if not title:
                    continue

                company = self._clean(
                    (item.get("company") or {}).get("name", "")
                    or item.get("company_name", "Unknown")
                )

                description = self._clean(
                    item.get("description") or item.get("job_description") or ""
                )

                # Build URL
                slug = item.get("slug") or item.get("code") or job_id
                url = f"https://www.kalibrr.com/job-board/te/{slug}"

                salary_min = item.get("salary_min") or item.get("minimum_salary")
                salary_max = item.get("salary_max") or item.get("maximum_salary")
                if salary_min and salary_max:
                    salary = f"PHP {salary_min:,} - {salary_max:,}/month"
                elif salary_min:
                    salary = f"PHP {salary_min:,}+/month"
                else:
                    salary = "Not specified"

                posted_at = str(item.get("activation_date") or item.get("created_at") or "")

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
                        source="Kalibrr",
                    )
                )

        logger.info("Fetched %d Kalibrr jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        return self._WHITESPACE.sub(" ", (value or "")).strip()
