import tempfile
import unittest
from pathlib import Path

from config.settings import settings
from core.models import Job
from services.database_service import DatabaseService


class DatabaseServiceTest(unittest.TestCase):
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

    def test_initializes_fresh_database_and_saves_job(self) -> None:
        service = DatabaseService()
        job = Job(
            title="Junior Laravel Developer",
            company="Example Co",
            description="Build APIs with PHP and Laravel.",
            url="https://example.com/jobs/junior-laravel",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
            fingerprint="unit-test-fingerprint",
            score=86,
            priority="HIGH",
            interview_probability=82,
            matched_skills=["PHP", "Laravel"],
            missing_skills=["Docker"],
            ai_recommendation="Apply",
            ai_reasoning="Strong overlap for a junior profile.",
        )

        inserted = service.save_all([job])

        self.assertEqual(inserted, 1)
        self.assertTrue(service.exists("unit-test-fingerprint"))
        self.assertEqual(service.count(), 1)

        saved = service.list_jobs(limit=1)[0]
        self.assertEqual(saved["ai_recommendation"], "Apply")
        self.assertIn("Laravel", saved["matched_skills"])

    def test_duplicate_fingerprint_is_ignored(self) -> None:
        service = DatabaseService()
        job = Job(
            title="Junior Backend Developer",
            company="Example Co",
            description="Python and REST APIs.",
            url="https://example.com/jobs/backend",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Canada",
            remote=True,
            source="UnitTest",
            fingerprint="duplicate-fingerprint",
            score=78,
            priority="HIGH",
        )

        self.assertEqual(service.save_all([job, job]), 1)
        self.assertEqual(service.count(), 1)

    def test_updates_application_status(self) -> None:
        service = DatabaseService()
        job = Job(
            title="PHP Web Developer",
            company="Example Co",
            description="Remote PHP role.",
            url="https://example.com/jobs/php",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
            fingerprint="status-fingerprint",
            score=63,
            priority="GOOD",
        )

        service.save(job)
        job_id = service.list_jobs(limit=1)[0]["id"]

        self.assertTrue(service.mark_application_status(job_id, "applied"))

        updated = service.list_jobs(limit=1)[0]
        self.assertEqual(updated["application_status"], "applied")

    def test_updates_application_status_to_archived(self) -> None:
        service = DatabaseService()
        job = Job(
            title="Python Engineer",
            company="Example Co",
            description="Remote Django role.",
            url="https://example.com/jobs/django",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
            fingerprint="archived-fingerprint",
            score=63,
            priority="GOOD",
        )

        service.save(job)
        job_id = [j for j in service.list_jobs(limit=10) if j["url"] == job.url][0]["id"]

        self.assertTrue(service.mark_application_status(job_id, "archived"))

        # Verify in database directly that applied is 0 and status is archived
        conn = service.db.connect()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT applied, application_status FROM jobs WHERE id = ?", (job_id,))
            row = cursor.fetchone()
            self.assertEqual(row["applied"], 0)
            self.assertEqual(row["application_status"], "archived")
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
