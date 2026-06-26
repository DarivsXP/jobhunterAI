"""
RemoteOK Scraper
"""

from typing import List

import requests

from core.logger import get_logger
from core.models import Job

from scrapers.base import BaseScraper

logger = get_logger(__name__)


class RemoteOKScraper(BaseScraper):

    URL = "https://remoteok.com/api"

    def fetch_jobs(self) -> List[Job]:

        logger.info("Fetching jobs from RemoteOK...")

        headers = {
            "User-Agent": "JobHunterAI/1.0"
        }

        response = requests.get(
            self.URL,
            headers=headers,
            timeout=30,
        )

        response.raise_for_status()

        data = response.json()

        jobs: List[Job] = []

        # First item is metadata
        for item in data[1:]:

            jobs.append(

                Job(

                    title=item.get("position", ""),

                    company=item.get("company", ""),

                    description=item.get("description", ""),

                    url=item.get("url", ""),

                    posted_at=str(item.get("date", "")),

                    salary=item.get("salary_min", "") or "Not specified",

                    country=item.get("location", "Worldwide"),

                    remote=True,

                    source="RemoteOK",

                )

            )

        logger.info(f"Fetched {len(jobs)} RemoteOK jobs.")

        return jobs