import unittest

from core.models import Job
from core.prefilter import JobPrefilter


class JobPrefilterTest(unittest.TestCase):
    def setUp(self) -> None:
        self.prefilter = JobPrefilter()

    def test_keeps_target_backend_role(self) -> None:
        job = Job(
            title="Junior Backend Developer",
            company="Example Co",
            description="Remote backend role using PHP and Laravel.",
            url="https://example.com/jobs/backend",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )

        self.assertTrue(self.prefilter.should_keep(job))

    def test_rejects_generic_openings(self) -> None:
        job = Job(
            title="View Open Positions",
            company="Example Co",
            description="General careers page.",
            url="https://example.com/jobs/open",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )

        self.assertFalse(self.prefilter.should_keep(job))

    def test_rejects_non_software_role_families(self) -> None:
        job = Job(
            title="Marketing Assistant",
            company="Example Co",
            description="Remote role.",
            url="https://example.com/jobs/marketing",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )

        self.assertFalse(self.prefilter.should_keep(job))

    def test_keeps_internship_when_technical_stack_is_present(self) -> None:
        job = Job(
            title="Web Development Intern",
            company="Example Co",
            description="PHP, Laravel, Git, and MySQL.",
            url="https://example.com/jobs/intern",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )

        self.assertTrue(self.prefilter.should_keep(job))

    def test_rejects_senior_role_before_recruiter(self) -> None:
        job = Job(
            title="Senior Software Engineer",
            company="Example Co",
            description="Remote role with Python.",
            url="https://example.com/jobs/senior",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )

        self.assertFalse(self.prefilter.should_keep(job))


if __name__ == "__main__":
    unittest.main()
