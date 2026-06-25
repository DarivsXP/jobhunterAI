"""
Remotive Scraper
"""

from typing import List

import requests

from core.logger import get_logger
from core.models import Job

logger = get_logger(__name__)

URL = "https://remotive.com/api/remote-jobs"


def fetch_jobs() -> List[Job]:
    """
    Fetch jobs from Remotive.
    """

    logger.info("Fetching jobs from Remotive...")

    response = requests.get(URL, timeout=30)
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
                posted_at=item.get("publication_date", ""),
                salary=item.get("salary", "Not specified"),
                country=item.get(
                    "candidate_required_location",
                    "Worldwide",
                ),
                remote=True,
                source="Remotive",
            )
        )

    logger.info(f"Retrieved {len(jobs)} jobs.")

    return jobs