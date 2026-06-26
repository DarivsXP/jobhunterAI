"""
Job Normalizer

Normalizes job data from different job boards into
a consistent format.
"""

from core.models import Job


class JobNormalizer:

    def normalize(self, job: Job) -> Job:
        """
        Clean and normalize job fields.
        """

        job.title = job.title.strip()

        job.company = job.company.strip()

        job.description = job.description.strip()

        job.country = job.country.strip()

        job.source = job.source.strip()

        if not job.salary:
            job.salary = "Not specified"

        if not job.country:
            job.country = "Worldwide"

        if not job.posted_at:
            job.posted_at = "Unknown"

        return job