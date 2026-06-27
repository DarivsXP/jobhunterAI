"""
Remotive Scraper
"""

from typing import List

import requests

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class RemotiveScraper(BaseScraper):

    URL = "https://remotive.com/api/remote-jobs?category=software-dev&limit=100"

    def fetch_jobs(self) -> List[Job]:

        logger.info("Fetching jobs from Remotive...")

        response = requests.get(
            self.URL,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        jobs: List[Job] = []

        for item in data["jobs"]:

            jobs.append(

                Job(

                    title=item.get("title", ""),

                    company=item.get("company_name", ""),

                    description=item.get("description", ""),

                    url=item.get("url", ""),

                    posted_at=item.get(
                        "publication_date",
                        ""
                    ),

                    salary=item.get(
                        "salary",
                        "Not specified"
                    ),

                    country=item.get(
                        "candidate_required_location",
                        "Worldwide"
                    ),

                    remote=True,

                    source="Remotive",

                )

            )

        logger.info(
            f"Fetched {len(jobs)} Remotive jobs."
        )

        return jobs