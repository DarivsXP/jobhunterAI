import unittest

from config.settings import settings
from core.models import Job
from services.ai_recruiter_service import AIRecruiterService


class AIRecruiterServiceTest(unittest.TestCase):
    def test_returns_none_when_api_key_is_missing(self) -> None:
        service = AIRecruiterService()
        original_key = settings.openai_api_key
        object.__setattr__(settings, "openai_api_key", "")

        try:
            job = Job(
                title="Junior Backend Developer",
                company="Example Co",
                description="Remote backend role.",
                url="https://example.com/jobs/backend",
                posted_at="2026-06-27",
                salary="Not specified",
                country="Worldwide",
                remote=True,
                source="UnitTest",
            )

            self.assertIsNone(service.evaluate(job))

        finally:
            object.__setattr__(settings, "openai_api_key", original_key)

    def test_parses_response_output_text(self) -> None:
        service = AIRecruiterService()
        payload = {
            "output_text": (
                '{"interview_probability": 81,'
                '"matched_skills":["PHP","Laravel"],'
                '"missing_skills":["Docker"],'
                '"recommendation":"Apply",'
                '"reasoning":"Strong backend overlap for a junior candidate."}'
            )
        }
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
        )

        analysis = service._parse_response(payload, job)

        self.assertIsNotNone(analysis)
        assert analysis is not None
        self.assertEqual(analysis.interview_probability, 81)
        self.assertEqual(analysis.recommendation, "Apply")
        self.assertIn("Laravel", analysis.matched_skills)


if __name__ == "__main__":
    unittest.main()
