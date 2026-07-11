"""
Notification Service
"""

from __future__ import annotations

from core.logger import get_logger
from core.models import Job
from telegram.bot import TelegramBot
from telegram.formatter import format_scan_summary

logger = get_logger(__name__)


class NotificationService:
    def __init__(self) -> None:
        self.bot = TelegramBot()

    def notify(self, new_jobs: list[Job], total_scraped: int = 0, total_kept: int = 0) -> None:
        """
        Send Telegram notifications for a completed scan.

        Args:
            new_jobs:      Only the jobs that were NEWLY saved in this scan run.
            total_scraped: Total jobs scraped (for scan summary).
            total_kept:    Total jobs that passed the pipeline (for scan summary).
        """
        if not self.bot.is_enabled:
            logger.info("Telegram not configured — skipping notifications.")
            return

        if not new_jobs and total_scraped == 0:
            logger.info("Nothing to notify about.")
            return

        hot_jobs = [j for j in new_jobs if j.priority == "HOT"]
        high_jobs = [j for j in new_jobs if j.priority == "HIGH"]

        hot = len(hot_jobs)
        high = len(high_jobs)
        good = sum(j.priority == "GOOD" for j in new_jobs)

        # 1. Send individual alerts for HOT and HIGH priority new jobs (max 5 total)
        important = (hot_jobs + high_jobs)[:5]
        for job in important:
            if job.priority == "HOT":
                self.bot.send_hot_match(job)
            else:
                self.bot.send_high_match(job)

        # 2. Send scan summary if there were any new jobs
        if new_jobs:
            summary = format_scan_summary(
                total_scraped=total_scraped,
                total_kept=total_kept,
                hot=hot,
                high=high,
                good=good,
            )
            self.bot.send(summary)

        # 3. Send digest only for scans that found new jobs
        if new_jobs:
            self.bot.send_digest(new_jobs)

    def send_error(self, message: str) -> None:
        self.bot.send_error(message)

    def test(self) -> bool:
        """Send a test message to verify connectivity."""
        return self.bot.test_connection()
