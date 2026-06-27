"""
Scraper Service

Collects jobs from every registered scraper.
"""

from __future__ import annotations

from core.logger import get_logger
from core.models import Job
from scrapers import SCRAPERS

logger = get_logger(__name__)


class ScraperService:
    def collect_jobs(self) -> list[Job]:
        jobs: list[Job] = []

        for scraper in SCRAPERS:
            logger.info("Running %s", scraper.__class__.__name__)

            try:
                jobs.extend(scraper.fetch_jobs())

            except Exception:
                logger.exception(
                    "Scraper failed: %s",
                    scraper.__class__.__name__,
                )

        logger.info("Collected %d jobs.", len(jobs))
        return jobs
