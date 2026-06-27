import unittest

from core.models import Job
from core.normalizer import JobNormalizer


class JobNormalizerTest(unittest.TestCase):
    def test_converts_non_string_salary_and_posted_at(self) -> None:
        normalizer = JobNormalizer()
        job = Job(
            title="php developer",
            company="Example Co",
            description="Build APIs",
            url="HTTPS://EXAMPLE.COM/jobs/1?utm_source=test",
            posted_at=1234567890,
            salary=50000,
            country="Canada",
            remote=True,
            source="UnitTest",
        )

        normalized = normalizer.normalize(job)

        self.assertEqual(normalized.salary, "50000")
        self.assertEqual(normalized.posted_at, "1234567890")
        self.assertEqual(normalized.url, "https://example.com/jobs/1")


if __name__ == "__main__":
    unittest.main()
