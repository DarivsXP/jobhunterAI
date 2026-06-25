"""
JobHunterAI Telegram Service
"""

import os
import requests

from dotenv import load_dotenv

from core.logger import get_logger

logger = get_logger(__name__)

load_dotenv()


class TelegramBot:

    def __init__(self):

        self.token = os.getenv("BOT_TOKEN")
        self.chat_id = os.getenv("CHAT_ID")

        self.base_url = (
            f"https://api.telegram.org/bot{self.token}"
        )

    def send(self, message: str):

        logger.info("Sending Telegram message...")

        response = requests.post(
            f"{self.base_url}/sendMessage",
            json={
                "chat_id": self.chat_id,
                "text": message
            },
            timeout=30
        )

        response.raise_for_status()

        return response.json()

    def send_hot_match(self, job: dict):

        self.send(
f"""🔥 APPLY IMMEDIATELY

Role:
{job['title']}

Company:
{job['company']}

Score:
{job['score']}

Source:
{job['source']}

Apply:
{job['url']}
"""
        )

    def send_digest(self, digest: str):

        self.send(digest)

    def send_error(self, error: str):

        self.send(
f"""❌ JobHunterAI Error

{error}
"""
        )