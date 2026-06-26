"""
Notification Service
"""

from typing import List

from core.models import Job
from telegram.bot import TelegramBot


class NotificationService:

    def __init__(self):

        self.bot = TelegramBot()

    def notify(self, jobs: List[Job]):

        for job in jobs:

            if job.priority == "HOT":

                self.bot.send_hot_match(job)

            elif job.priority == "HIGH":

                self.bot.send_high_match(job)

    def send_error(self, message: str):

        self.bot.send_error(message)