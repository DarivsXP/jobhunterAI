"""
Job Fingerprint

Generates a stable fingerprint for duplicate detection.
"""

from __future__ import annotations

import hashlib
import re

from core.models import Job


class JobFingerprint:
    """Creates deterministic fingerprints for jobs."""

    _whitespace = re.compile(r"\s+")

    @classmethod
    def create(cls, job: Job) -> str:
        parts = [
            cls._normalize(job.company),
            cls._normalize(job.title),
            cls._normalize(job.country),
            cls._normalize(job.source),
        ]

        if job.remote:
            parts.append("remote")

        key = "|".join(parts)

        return hashlib.sha256(
            key.encode("utf-8")
        ).hexdigest()

    @classmethod
    def short(cls, job: Job) -> str:
        return cls.create(job)[:16]

    @classmethod
    def matches(cls, first: Job, second: Job) -> bool:
        return cls.create(first) == cls.create(second)

    @classmethod
    def assign(cls, job: Job) -> Job:
        job.fingerprint = cls.create(job)
        return job

    @classmethod
    def _normalize(cls, value: str) -> str:
        if not value:
            return ""

        value = value.casefold().strip()

        value = cls._whitespace.sub(" ", value)

        return value