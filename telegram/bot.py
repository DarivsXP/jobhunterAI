"""
Telegram Service
"""

import os

import requests

from dotenv import load_dotenv

from core.logger import get_logger
from core.models import Job

load_dotenv()

logger = get_logger(__name__)


class TelegramBot:

    def __init__(self):

        self.token = os.getenv("BOT_TOKEN")

        self.chat_id = os.getenv("CHAT_ID")

        self.base_url = (
            f"https://api.telegram.org/bot{self.token}"
        )

    def send(self, message: str):

        try:

            response = requests.post(

                f"{self.base_url}/sendMessage",

                json={

                    "chat_id": self.chat_id,

                    "text": message,

                    "parse_mode": "Markdown",

                    "disable_web_page_preview": True,

                },

                timeout=30,

            )

            response.raise_for_status()

            logger.info(
                "Telegram message sent."
            )

        except Exception as error:

            logger.exception(error)

    def send_hot_match(self, job: Job):

        self.send(
f"""
🔥 *HOT MATCH*

💼 *Role*
{job.title}

🏢 *Company*
{job.company}

⭐ *Score*
{job.score}

🌍 *Country*
{job.country}

🔗 {job.url}
"""
        )

    def send_high_match(self, job: Job):

        self.send(
f"""
⭐ *HIGH MATCH*

💼 {job.title}

🏢 {job.company}

⭐ Score: {job.score}

🔗 {job.url}
"""
        )

    def send_digest(self, message: str):

        self.send(message)

    def send_error(self, message: str):

        self.send(
f"""
❌ *JobHunterAI Error*

{message}
"""
        )