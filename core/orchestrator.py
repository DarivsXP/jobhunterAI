"""
JobHunterAI Orchestrator
"""

from core.logger import get_logger
from core.pipeline import ProcessingPipeline
from services.database_service import DatabaseService
from services.notification_service import NotificationService
from services.recruiter_service import RecruiterService
from services.scraper_service import ScraperService

logger = get_logger(__name__)


class JobOrchestrator:
    def __init__(self) -> None:
        logger.info("Initializing JobHunterAI...")

        self.scraper = ScraperService()
        self.pipeline = ProcessingPipeline()
        self.recruiter = RecruiterService()
        self.database = DatabaseService()
        self.notification = NotificationService()

    def run(self) -> None:
        logger.info("=" * 60)
        logger.info("JOB SCAN STARTED")
        logger.info("=" * 60)

        #
        # Step 1
        #
        jobs = self.scraper.collect_jobs()
        logger.info("Scraped %d jobs", len(jobs))

        #
        # Step 2
        #
        jobs = self.pipeline.process(jobs)
        logger.info("Pipeline kept %d jobs", len(jobs))

        #
        # Step 3
        #
        jobs = self.recruiter.process(
            jobs,
            self.database,
        )
        logger.info("Recruiter accepted %d jobs", len(jobs))

        #
        # Step 4
        #
        saved = self.database.save_all(jobs)

        logger.info(
            "Saved %d new jobs",
            saved,
        )

        #
        # Step 5
        #
        self.notification.notify(jobs)

        hot = sum(job.priority == "HOT" for job in jobs)
        high = sum(job.priority == "HIGH" for job in jobs)
        good = sum(job.priority == "GOOD" for job in jobs)

        logger.info("=" * 60)
        logger.info("JOB SCAN COMPLETE")
        logger.info("=" * 60)
        logger.info("Accepted : %d", len(jobs))
        logger.info("HOT      : %d", hot)
        logger.info("HIGH     : %d", high)
        logger.info("GOOD     : %d", good)
        logger.info("=" * 60)