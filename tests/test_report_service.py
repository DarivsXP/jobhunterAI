import tempfile
import unittest
from pathlib import Path

from config.settings import settings
from core.models import Job
from services.database_service import DatabaseService
from services.report_service import ReportService


class ReportServiceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.original_database_path = settings.database_path
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "jobs.db"
        object.__setattr__(settings, "database_path", self.database_path)

    def tearDown(self) -> None:
        object.__setattr__(
            settings,
            "database_path",
            self.original_database_path,
        )
        self.temp_dir.cleanup()

    def test_builds_dashboard_output(self) -> None:
        database = DatabaseService()
        database.save(
            Job(
                title="Junior Laravel Developer",
                company="Example Co",
                description="Remote PHP/Laravel role.",
                url="https://example.com/jobs/laravel",
                posted_at="2026-06-27",
                salary="Not specified",
                country="Worldwide",
                remote=True,
                source="UnitTest",
                fingerprint="dashboard-job",
                score=88,
                priority="HIGH",
                interview_probability=80,
                matched_skills=["PHP", "Laravel"],
                ai_recommendation="Strong Apply",
                ai_reasoning="Very good match.",
            )
        )
        report = ReportService(database).build_dashboard(limit=5)

        self.assertIn("JobHunterAI Dashboard", report)
        self.assertIn("Junior Laravel Developer", report)
        self.assertIn("Top Sources", report)


if __name__ == "__main__":
    unittest.main()
