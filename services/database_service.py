"""
Database Service

Handles saving jobs.
"""

from typing import List

from core.database import JobRepository
from core.models import Job


class DatabaseService:

    def __init__(self):

        self.repository = JobRepository()

    def exists(self, fingerprint: str) -> bool:

        return self.repository.exists(fingerprint)

    def save(self, job: Job):

        self.repository.save(job)

    def save_all(self, jobs: List[Job]):

        for job in jobs:

            self.save(job)

    def count(self):

        return self.repository.count()