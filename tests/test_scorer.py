import unittest

from candidate.profile import MY_PROFILE
from core.models import Job
from core.recruiter import Recruiter


class RecruiterThresholdTest(unittest.TestCase):
    def test_uses_profile_minimum_score_for_acceptance(self) -> None:
        recruiter = Recruiter()
        original_minimum_score = MY_PROFILE.minimum_score
        MY_PROFILE.minimum_score = 80

        try:
            job = Job(
                title="Backend Developer",
                company="Example Co",
                description="Remote backend role using PHP and MySQL.",
                url="https://example.com/jobs/backend-developer",
                posted_at="2026-06-27",
                salary="Not specified",
                country="Worldwide",
                remote=True,
                source="UnitTest",
                fingerprint="threshold-job",
            )

            evaluation = recruiter.evaluate(job)

            self.assertEqual(evaluation.score, 73)
            self.assertFalse(evaluation.accepted)

        finally:
            MY_PROFILE.minimum_score = original_minimum_score

    def test_discourages_adjacent_devops_roles(self) -> None:
        recruiter = Recruiter()
        job = Job(
            title="Devops & Platform Engineer (Aws / Ci/Cd)",
            company="Example Co",
            description=(
                "Remote role using Python, GitHub, REST APIs, JavaScript, "
                "and Git. Option to work remote in United Kingdom."
            ),
            url="https://example.com/jobs/devops",
            posted_at="2026-06-27",
            salary="Not specified",
            country="United Kingdom",
            remote=True,
            source="UnitTest",
            fingerprint="devops-job",
        )

        evaluation = recruiter.evaluate(job)

        self.assertLess(evaluation.score, MY_PROFILE.minimum_score)
        self.assertFalse(evaluation.accepted)

    def test_keeps_php_web_roles_viable(self) -> None:
        recruiter = Recruiter()
        job = Job(
            title="PHP Web Developer",
            company="Example Co",
            description=(
                "Remote role with PHP, JavaScript, HTML, CSS, MySQL, Git, "
                "and GitHub."
            ),
            url="https://example.com/jobs/php-web",
            posted_at="2026-06-27",
            salary="Not specified",
            country="Worldwide",
            remote=True,
            source="UnitTest",
            fingerprint="php-web-job",
        )

        evaluation = recruiter.evaluate(job)

        self.assertGreaterEqual(evaluation.score, MY_PROFILE.minimum_score)
        self.assertTrue(evaluation.accepted)


if __name__ == "__main__":
    unittest.main()
