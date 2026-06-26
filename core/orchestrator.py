"""
JobHunterAI Orchestrator
"""

from core.logger import get_logger

from services.scraper_service import ScraperService
from services.recruiter_service import RecruiterService
from services.database_service import DatabaseService
from services.notification_service import NotificationService

logger = get_logger(__name__)


class JobOrchestrator:

    def __init__(self):

        logger.info("Initializing JobHunterAI...")

        self.scraper = ScraperService()

        self.recruiter = RecruiterService()

        self.database = DatabaseService()

        self.notification = NotificationService()

    def run(self):

        logger.info("=" * 50)
        logger.info("Starting Job Scan")
        logger.info("=" * 50)

        #
        # Step 1
        #

        jobs = self.scraper.collect_jobs()

        #
        # Step 2
        #

        jobs = self.recruiter.process(

            jobs,

            self.database

        )

        #
        # Step 3
        #

        self.database.save_all(jobs)

        #
        # Step 4
        #

        self.notification.notify(jobs)

        #
        # Summary
        #

        hot = len(

            [j for j in jobs if j.priority == "HOT"]

        )

        high = len(

            [j for j in jobs if j.priority == "HIGH"]

        )

        good = len(

            [j for j in jobs if j.priority == "GOOD"]

        )

        logger.info("=" * 50)
        logger.info("SCAN COMPLETE")
        logger.info("=" * 50)

        logger.info(f"Accepted Jobs : {len(jobs)}")
        logger.info(f"HOT Matches   : {hot}")
        logger.info(f"HIGH Matches  : {high}")
        logger.info(f"GOOD Matches  : {good}")

        logger.info("=" * 50)