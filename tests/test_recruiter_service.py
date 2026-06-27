import unittest

from candidate.profile import MY_PROFILE
from core.models import Job
from services.ai_recruiter_service import AIRecruiterAnalysis
from services.recruiter_service import RecruiterService


class EmptyDatabase:
    def exists(self, fingerprint: str) -> bool:
        return False


class ExistingDatabase:
    def exists(self, fingerprint: str) -> bool:
        return True


class StubAIRecruiter:
    def __init__(self, analysis: AIRecruiterAnalysis | None = None) -> None:
        self.analysis = analysis

    def evaluate(self, job: Job) -> AIRecruiterAnalysis | None:
        return self.analysis


class RecruiterServiceTest(unittest.TestCase):
    def test_accepts_matching_job_without_ai_service_dependency(self) -> None:
        service = RecruiterService(ai_recruiter=StubAIRecruiter())
        job = Job(
            title="Junior Laravel Developer",
            company="Example Co",
            description=(
                "Remote role building REST API features with PHP, Laravel, "
                "MySQL, Git, HTML, CSS, and JavaScript."
            ),
            url="https://example.com/jobs/laravel",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
            fingerprint="accepted-job",
        )

        accepted = service.process([job], EmptyDatabase())

        self.assertEqual(len(accepted), 1)
        self.assertGreaterEqual(accepted[0].score, MY_PROFILE.minimum_score)
        self.assertGreater(accepted[0].interview_probability, 0)
        self.assertIn("Laravel", accepted[0].matched_skills)
        self.assertIn("REST API", accepted[0].matched_skills)

    def test_applies_ai_enrichment_when_available(self) -> None:
        service = RecruiterService(
            ai_recruiter=StubAIRecruiter(
                AIRecruiterAnalysis(
                    interview_probability=88,
                    matched_skills=["PHP", "Laravel"],
                    missing_skills=["Docker"],
                    recommendation="Apply",
                    reasoning="Strong overlap for a junior backend profile.",
                )
            )
        )
        job = Job(
            title="Junior Laravel Developer",
            company="Example Co",
            description="Remote backend role using PHP and Laravel.",
            url="https://example.com/jobs/laravel",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
            fingerprint="ai-enriched-job",
        )

        accepted = service.process([job], EmptyDatabase())

        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0].interview_probability, 88)
        self.assertEqual(accepted[0].ai_recommendation, "Apply")
        self.assertIn("Docker", accepted[0].missing_skills)

    def test_skips_existing_job(self) -> None:
        service = RecruiterService(ai_recruiter=StubAIRecruiter())
        job = Job(
            title="Junior PHP Developer",
            company="Example Co",
            description="Remote PHP role.",
            url="https://example.com/jobs/php",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
            fingerprint="existing-job",
        )

        accepted = service.process([job], ExistingDatabase())

        self.assertEqual(accepted, [])

    def test_rejects_non_remote_jobs_when_profile_requires_remote_only(self) -> None:
        service = RecruiterService(ai_recruiter=StubAIRecruiter())
        job = Job(
            title="Junior Backend Developer",
            company="Example Co",
            description="Backend role with Python and PostgreSQL.",
            url="https://example.com/jobs/on-site-backend",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Singapore",
            remote=False,
            source="UnitTest",
            fingerprint="non-remote-job",
        )

        accepted = service.process([job], EmptyDatabase())

        self.assertEqual(accepted, [])

    def test_rejects_excluded_seniority_terms_with_word_boundary_matching(self) -> None:
        service = RecruiterService(ai_recruiter=StubAIRecruiter())
        job = Job(
            title="Engineering Lead",
            company="Example Co",
            description="Remote backend role using PHP and Laravel.",
            url="https://example.com/jobs/engineering-lead",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
            fingerprint="lead-job",
        )

        accepted = service.process([job], EmptyDatabase())

        self.assertEqual(accepted, [])


if __name__ == "__main__":
    unittest.main()
