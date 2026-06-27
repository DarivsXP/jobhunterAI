"""
Notification Service
"""

from __future__ import annotations

from core.models import Job
from telegram.bot import TelegramBot


class NotificationService:
    def __init__(self) -> None:
        self.bot = TelegramBot()

    def notify(self, jobs: list[Job]) -> None:
        important_jobs = [
            job
            for job in jobs
            if job.priority in {"HOT", "HIGH"}
        ]

        for job in important_jobs[:5]:
            if job.priority == "HOT":
                self.bot.send_hot_match(job)
            else:
                self.bot.send_high_match(job)

        self.bot.send_digest(jobs[:5])

    def send_error(self, message: str) -> None:
        self.bot.send_error(message)
