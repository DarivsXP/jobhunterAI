"""
Glints Scraper

Glints is a major job platform across Southeast Asia — Philippines, Indonesia,
Vietnam, Taiwan, Singapore. Has a public GraphQL/REST API for job search.
Only fetches remote/WFH-tagged roles.
"""

from __future__ import annotations

import re

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class GlintsScraper(BaseScraper):
    _API_URL = "https://glints.com/api/jobs/search"
    _WHITESPACE = re.compile(r"\s+")

    # Role keywords relevant to Cyril's profile
    _KEYWORDS = [
        "software engineer",
        "backend developer",
        "full stack developer",
        "php developer",
        "laravel developer",
        "python developer",
        "web developer",
        "technical support engineer",
        "application support",
    ]

    # Country codes Glints uses for PH / broader Asia
    _COUNTRY_CODES = ["PH", "ID", "VN", "SG", "TW"]

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from Glints (PH/SE Asia)...")
        all_jobs: list[Job] = []
        seen_ids: set[str] = set()

        for keyword in self._KEYWORDS:
            for country in self._COUNTRY_CODES:
                try:
                    response = requests.get(
                        self._API_URL,
                        params={
                            "keyword": keyword,
                            "country": country,
                            "workArrangements": "REMOTE",
                            "limit": 20,
                            "offset": 0,
                        },
                        headers={
                            "User-Agent": (
                                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                                "AppleWebKit/537.36 (KHTML, like Gecko) "
                                "Chrome/120.0.0.0 Safari/537.36"
                            ),
                            "Accept": "application/json",
                            "Referer": "https://glints.com/",
                        },
                        timeout=20,
                    )
                    response.raise_for_status()
                    data = response.json()
                except Exception:
                    logger.exception(
                        "Glints request failed for keyword='%s' country='%s'.", keyword, country
                    )
                    continue

                # Handle both list and dict response shapes
                jobs_list = (
                    data
                    if isinstance(data, list)
                    else data.get("data", data.get("jobs", data.get("items", [])))
                )
                if not isinstance(jobs_list, list):
                    continue

                for item in jobs_list:
                    job_id = str(item.get("id", "") or "")
                    if not job_id or job_id in seen_ids:
                        continue
                    seen_ids.add(job_id)

                    title = self._clean(item.get("title") or "")
                    if not title:
                        continue

                    company_data = item.get("company") or {}
                    company = self._clean(
                        company_data.get("name", "") if isinstance(company_data, dict)
                        else str(company_data)
                    ) or "Unknown"

                    description = self._clean(item.get("description") or "")

                    url = (
                        f"https://glints.com/opportunities/jobs/{job_id}"
                        if job_id
                        else "https://glints.com"
                    )

                    salary_min = item.get("salaryEstimate", {}).get("min") if item.get("salaryEstimate") else None
                    salary_max = item.get("salaryEstimate", {}).get("max") if item.get("salaryEstimate") else None
                    if salary_min and salary_max:
                        salary = f"{salary_min:,} - {salary_max:,}/month"
                    else:
                        salary = "Not specified"

                    posted_at = str(item.get("createdAt") or item.get("created_at") or "")

                    # Map country code to readable name
                    country_name_map = {
                        "PH": "Philippines",
                        "ID": "Indonesia",
                        "VN": "Vietnam",
                        "SG": "Singapore",
                        "TW": "Taiwan",
                    }
                    country_name = country_name_map.get(country, "Asia")

                    all_jobs.append(
                        Job(
                            title=title,
                            company=company,
                            description=description,
                            url=url,
                            posted_at=posted_at,
                            salary=salary,
                            country=country_name,
                            remote=True,
                            source="Glints",
                        )
                    )

        logger.info("Fetched %d Glints jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        return self._WHITESPACE.sub(" ", (value or "")).strip()
