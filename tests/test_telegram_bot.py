import unittest

from config.settings import settings
from core.models import Job
from telegram.bot import TelegramBot
from telegram.formatter import format_job_message


class TelegramBotTest(unittest.TestCase):
    def test_disabled_without_credentials(self) -> None:
        original_token = settings.telegram_token
        original_chat_id = settings.telegram_chat_id
        object.__setattr__(settings, "telegram_token", "")
        object.__setattr__(settings, "telegram_chat_id", "")

        try:
            bot = TelegramBot()
            self.assertFalse(bot.is_enabled)
            self.assertFalse(bot.send("hello"))

        finally:
            object.__setattr__(settings, "telegram_token", original_token)
            object.__setattr__(settings, "telegram_chat_id", original_chat_id)

    def test_formats_job_message_with_ai_fields(self) -> None:
        job = Job(
            title="Junior Laravel Developer",
            company="Example Co",
            description="Remote backend role.",
            url="https://example.com/jobs/laravel",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
            priority="HIGH",
            score=90,
            interview_probability=82,
            matched_skills=["PHP", "Laravel"],
            ai_recommendation="Apply",
            ai_reasoning="Good overlap for a junior backend candidate.",
        )

        message = format_job_message(job)

        self.assertIn("Interview Probability", message)
        self.assertIn("AI Recommendation", message)
        self.assertIn("Laravel", message)
        self.assertIn("[Link to Job](https://example.com/jobs/laravel)", message)

    def test_escape_url(self) -> None:
        from telegram.formatter import escape_url
        url = "https://example.com/jobs/laravel(1)?ref=abc\\xyz"
        escaped = escape_url(url)
        self.assertEqual(escaped, "https://example.com/jobs/laravel(1\\)?ref=abc\\\\xyz")


if __name__ == "__main__":
    unittest.main()
