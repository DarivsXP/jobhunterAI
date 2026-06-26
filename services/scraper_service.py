"""
Scraper Service

Collects jobs from every registered scraper.
"""

from typing import List

from core.logger import get_logger
from core.models import Job

from scrapers import SCRAPERS

logger = get_logger(__name__)


class ScraperService:

    def collect_jobs(self) -> List[Job]:

        jobs: List[Job] = []

        for scraper in SCRAPERS:

            logger.info(
                f"Running {scraper.__class__.__name__}"
            )

            try:

                jobs.extend(
                    scraper.fetch_jobs()
                )

            except Exception as error:

                logger.exception(error)

        logger.info(
            f"Collected {len(jobs)} jobs."
        )

        return jobs