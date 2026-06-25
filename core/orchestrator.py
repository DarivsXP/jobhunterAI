"""
JobHunterAI Orchestrator

Coordinates the entire job hunting pipeline.
"""

from typing import List

from core.database import JobRepository
from core.logger import get_logger
from core.models import Job
from core.recruiter import Recruiter

from telegram.bot import TelegramBot

from scrapers.remotive import fetch_jobs

logger = get_logger(__name__)


class JobOrchestrator:

    def __init__(self):

        logger.info("Initializing JobOrchestrator...")

        self.db = JobRepository()

        self.bot = TelegramBot()

        self.recruiter = Recruiter()

    def run(self):

    logger.info("Starting job scan...")

    jobs: List[Job] = []

    jobs.extend(fetch_jobs())

    logger.info(f"{len(jobs)} jobs collected.")

    new_jobs = 0
    duplicates = 0
    rejected = 0

    hot = 0
    high = 0
    good = 0

    for job in jobs:

        if self.db.exists(job.url):

            duplicates += 1

            continue

        evaluation = self.recruiter.evaluate(job)

        if not evaluation.accepted:

            rejected += 1

            continue

        job.score = evaluation.score

        self.db.save(job)

        new_jobs += 1

        if evaluation.priority == "HOT":

            hot += 1

            self.bot.send_hot_match(job)

        elif evaluation.priority == "HIGH":

            high += 1

        elif evaluation.priority == "GOOD":

            good += 1

    logger.info("--------------------------------")
    logger.info(f"Jobs Collected : {len(jobs)}")
    logger.info(f"New Jobs       : {new_jobs}")
    logger.info(f"Duplicates     : {duplicates}")
    logger.info(f"Rejected       : {rejected}")
    logger.info(f"HOT            : {hot}")
    logger.info(f"HIGH           : {high}")
    logger.info(f"GOOD           : {good}")
    logger.info("--------------------------------")