"""
Telegram notification client.
"""

from __future__ import annotations

import requests

from config.settings import settings
from core.logger import get_logger
from core.models import Job
from telegram.formatter import escape_markdown, format_digest, format_job_message

logger = get_logger(__name__)


class TelegramBot:
    def __init__(self) -> None:
        self.token = settings.telegram_token
        self.chat_id = settings.telegram_chat_id

    @property
    def is_enabled(self) -> bool:
        return bool(self.token and self.chat_id)

    @property
    def base_url(self) -> str:
        return f"https://api.telegram.org/bot{self.token}"

    def send(self, message: str) -> bool:
        if not self.is_enabled:
            logger.info("Telegram disabled — token or chat_id missing. Skipping notification.")
            return False

        # Telegram messages have a 4096-char hard limit
        if len(message) > 4096:
            message = message[:4090] + "\\.\\.\\."

        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "MarkdownV2",
                    "disable_web_page_preview": True,
                    "disable_notification": False,
                },
                timeout=30,
            )

            if not response.ok:
                # Log the full Telegram error so we can see exactly what went wrong
                logger.error(
                    "Telegram API rejected message (status %d): %s",
                    response.status_code,
                    response.text,
                )
                return False

            logger.info("Telegram message sent successfully.")
            return True

        except requests.exceptions.Timeout:
            logger.error("Telegram send timed out.")
            return False

        except Exception:
            logger.exception("Telegram send failed with unexpected error.")
            return False

    def send_hot_match(self, job: Job) -> bool:
        logger.info("Sending HOT match notification: %s @ %s", job.title, job.company)
        return self.send(format_job_message(job))

    def send_high_match(self, job: Job) -> bool:
        logger.info("Sending HIGH match notification: %s @ %s", job.title, job.company)
        return self.send(format_job_message(job))

    def send_digest(self, jobs: list[Job]) -> bool:
        logger.info("Sending digest for %d jobs.", len(jobs))
        return self.send(format_digest(jobs))

    def send_error(self, message: str) -> bool:
        safe_message = escape_markdown(message)
        return self.send(f"*JobHunterAI Error*\n\n{safe_message}")

    def test_connection(self) -> bool:
        """Send a test ping to verify the bot token and chat_id are valid."""
        if not self.is_enabled:
            logger.warning("Cannot test: Telegram token or chat_id is missing.")
            return False
        return self.send("✅ *JobHunterAI* is online and connected\\!")
