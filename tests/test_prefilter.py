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

    def test_rejects_non_junior_role_requiring_too_much_experience(self) -> None:
        job = Job(
            title="Software Engineer",
            company="Example Co",
            description="We require 3+ years of experience in PHP.",
            url="https://example.com/jobs/se",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )
        self.assertFalse(self.prefilter.should_keep(job))

    def test_keeps_non_junior_role_with_acceptable_experience(self) -> None:
        job = Job(
            title="Software Engineer",
            company="Example Co",
            description="We require 2 years of experience in PHP.",
            url="https://example.com/jobs/se2",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )
        self.assertTrue(self.prefilter.should_keep(job))

    def test_rejects_junior_role_requiring_too_much_experience(self) -> None:
        job = Job(
            title="Junior Backend Developer",
            company="Example Co",
            description="Requirements: at least 4 years of experience.",
            url="https://example.com/jobs/jr",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )
        self.assertFalse(self.prefilter.should_keep(job))

    def test_keeps_junior_role_with_acceptable_experience(self) -> None:
        job = Job(
            title="Junior Backend Developer",
            company="Example Co",
            description="Requirements: at least 3 years of experience.",
            url="https://example.com/jobs/jr3",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )
        self.assertTrue(self.prefilter.should_keep(job))

    def test_does_not_reject_on_unrelated_number_of_years(self) -> None:
        job = Job(
            title="Software Engineer",
            company="Example Co",
            description="Our company was founded 10 years ago. Looking for PHP dev.",
            url="https://example.com/jobs/founded",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )
        self.assertTrue(self.prefilter.should_keep(job))

    def test_rejects_jobs_older_than_thirty_days(self) -> None:
        import datetime
        old_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=35)).strftime("%Y-%m-%d %H:%M:%S")
        job = Job(
            title="Software Engineer",
            company="Example Co",
            description="We are looking for a PHP developer.",
            url="https://example.com/jobs/old",
            posted_at=old_date,
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )
        self.assertFalse(self.prefilter.should_keep(job))

    def test_keeps_recent_jobs(self) -> None:
        import datetime
        recent_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=2)).strftime("%Y-%m-%d %H:%M:%S")
        job = Job(
            title="Software Engineer",
            company="Example Co",
            description="We are looking for a PHP developer.",
            url="https://example.com/jobs/recent",
            posted_at=recent_date,
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )
        self.assertTrue(self.prefilter.should_keep(job))

    def test_keeps_technical_support_role_requiring_up_to_four_years_experience(self) -> None:
        import datetime
        recent_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        job = Job(
            title="Technical Support Engineer",
            company="Example Co",
            description="Requirements: at least 4 years of experience.",
            url="https://example.com/jobs/support-4",
            posted_at=recent_date,
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )
        self.assertTrue(self.prefilter.should_keep(job))

    def test_rejects_technical_support_role_requiring_five_years_experience(self) -> None:
        import datetime
        recent_date = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        job = Job(
            title="Technical Support Engineer",
            company="Example Co",
            description="Requirements: at least 5 years of experience.",
            url="https://example.com/jobs/support-5",
            posted_at=recent_date,
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
        )
        self.assertFalse(self.prefilter.should_keep(job))


if __name__ == "__main__":
    unittest.main()
