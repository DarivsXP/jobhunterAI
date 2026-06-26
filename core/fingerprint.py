"""
Job Fingerprint

Creates a unique fingerprint for a job.
"""

import hashlib

from core.models import Job


class JobFingerprint:

    @staticmethod
    def create(job: Job) -> str:

        text = (
            f"{job.company}|"
            f"{job.title}|"
            f"{job.country}"
        ).lower()

        return hashlib.sha256(
            text.encode("utf-8")
        ).hexdigest()