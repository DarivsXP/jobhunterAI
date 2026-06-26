"""
Database Service

Handles saving jobs.
"""

from typing import List

from core.database import Database
from core.models import Job


class DatabaseService:

    def __init__(self):

        # Use the existing Database class which manages sqlite connections
        # and schema initialization. This service provides a thin wrapper
        # with simpler method names used across the codebase.
        self.db = Database()
        self.db.initialize()

    def exists(self, fingerprint: str) -> bool:

        conn = self.db.connect()

        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(1) FROM jobs WHERE fingerprint = ?",
            (fingerprint,)
        )

        exists = cursor.fetchone()[0] > 0

        conn.close()

        return exists

    def save(self, job: Job):

        conn = self.db.connect()

        cursor = conn.cursor()

        cursor.execute(
            "INSERT OR IGNORE INTO jobs(title, company, source, url, fingerprint, score, priority, posted_at, description, salary, country) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                job.title,
                job.company,
                job.source,
                job.url,
                job.fingerprint,
                job.score,
                job.priority,
                job.posted_at,
                job.description,
                job.salary,
                job.country,
            ),
        )

        conn.commit()

        conn.close()

    def save_all(self, jobs: List[Job]):

        for job in jobs:

            self.save(job)

    def count(self):

        conn = self.db.connect()

        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(1) FROM jobs")

        c = cursor.fetchone()[0]

        conn.close()

        return c