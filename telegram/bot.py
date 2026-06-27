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
            logger.info("Telegram disabled. Skipping notification send.")
            return False

        try:
            response = requests.post(
                f"{self.base_url}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "MarkdownV2",
                    "disable_web_page_preview": True,
                },
                timeout=30,
            )
            response.raise_for_status()
            logger.info("Telegram message sent.")
            return True

        except Exception:
            logger.exception("Telegram send failed.")
            return False

    def send_hot_match(self, job: Job) -> bool:
        return self.send(format_job_message(job))

    def send_high_match(self, job: Job) -> bool:
        return self.send(format_job_message(job))

    def send_digest(self, jobs: list[Job]) -> bool:
        return self.send(format_digest(jobs))

    def send_error(self, message: str) -> bool:
        safe_message = escape_markdown(message)
        return self.send(f"*JobHunterAI Error*\n\n{safe_message}")
