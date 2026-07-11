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
        # Step 1 — Scrape
        #
        scraped_jobs = self.scraper.collect_jobs()
        logger.info("Scraped %d jobs", len(scraped_jobs))

        #
        # Step 2 — Normalise + filter + deduplicate in-memory
        #
        jobs = self.pipeline.process(scraped_jobs)
        logger.info("Pipeline kept %d jobs", len(jobs))

        #
        # Step 3 — Score, rank, AI-enrich (skips DB duplicates)
        #
        jobs = self.recruiter.process(
            jobs,
            self.database,
        )
        logger.info("Recruiter accepted %d jobs", len(jobs))

        #
        # Step 4 — Persist; only newly-inserted jobs are returned for notification
        #
        # Filter to jobs not yet in DB before saving so we know exactly what's new
        new_jobs = self.database.filter_new_jobs(jobs)
        saved = self.database.save_all(jobs)

        logger.info(
            "Saved %d new jobs (%d were already in DB)",
            saved,
            len(jobs) - saved,
        )

        #
        # Step 5 — Notify only for jobs that were actually new this run
        #
        self.notification.notify(
            new_jobs=new_jobs,
            total_scraped=len(scraped_jobs),
            total_kept=len(jobs),
        )

        hot = sum(job.priority == "HOT" for job in jobs)
        high = sum(job.priority == "HIGH" for job in jobs)
        good = sum(job.priority == "GOOD" for job in jobs)

        logger.info("=" * 60)
        logger.info("JOB SCAN COMPLETE")
        logger.info("=" * 60)
        logger.info("Scraped  : %d", len(scraped_jobs))
        logger.info("Accepted : %d", len(jobs))
        logger.info("New      : %d", saved)
        logger.info("HOT      : %d", hot)
        logger.info("HIGH     : %d", high)
        logger.info("GOOD     : %d", good)
        logger.info("=" * 60)