"""
Job Processing Pipeline
"""

from core.fingerprint import JobFingerprint
from core.logger import get_logger
from core.models import Job
from core.normalizer import JobNormalizer
from core.prefilter import JobPrefilter

logger = get_logger(__name__)


class ProcessingPipeline:
    """
    Executes the processing pipeline for every scraped job.

    Scraper
    Normalizer
    Prefilter
    Fingerprint
    In-memory duplicate detection
    """

    def __init__(self) -> None:
        self.normalizer = JobNormalizer()
        self.prefilter = JobPrefilter()

    def process(self, jobs: list[Job]) -> list[Job]:
        processed: list[Job] = []
        fingerprints: set[str] = set()

        for job in jobs:
            try:
                job = self.normalizer.normalize(job)

                if not self.prefilter.should_keep(job):
                    logger.debug(
                        "Prefilter skipped: %s (%s)",
                        job.title,
                        job.company,
                    )
                    continue

                job = JobFingerprint.assign(job)

                if job.fingerprint in fingerprints:
                    logger.debug(
                        "Duplicate skipped: %s (%s)",
                        job.title,
                        job.company,
                    )
                    continue

                fingerprints.add(job.fingerprint)
                processed.append(job)

            except Exception:
                logger.exception(
                    "Failed processing job: %s",
                    getattr(job, "title", "Unknown"),
                )

        logger.info(
            "Pipeline finished (%d to %d jobs)",
            len(jobs),
            len(processed),
        )

        return processed
