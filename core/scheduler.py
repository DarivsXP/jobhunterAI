"""
JobHunterAI Scheduler
"""

import time

import schedule

from core.logger import get_logger
from core.orchestrator import JobOrchestrator

logger = get_logger(__name__)


class Scheduler:

    def __init__(self):

        self.orchestrator = JobOrchestrator()

    def scan(self):

        logger.info("Running scheduled scan...")

        self.orchestrator.run()

    def start(self):

        logger.info("Scheduler started.")

        schedule.every(1).hours.do(self.scan)

        # Run immediately

        self.scan()

        while True:

            schedule.run_pending()

            time.sleep(10)