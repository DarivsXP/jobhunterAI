"""
Database Repository
"""

from pathlib import Path
import sqlite3

from core.logger import get_logger
from core.models import Job
from core.schema import JOBS_TABLE
from core.migrations import MigrationManager

logger = get_logger(__name__)


class JobRepository:

    def __init__(self):

        Path("database").mkdir(exist_ok=True)

        self.connection = sqlite3.connect(
            "database/jobs.db",
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

        self.create_tables()

        MigrationManager(
            self.connection
        ).migrate()

    def create_tables(self):

        logger.info("Creating database tables...")

        self.cursor.execute(JOBS_TABLE)

        self.connection.commit()

    def exists(self, fingerprint: str) -> bool:

        self.cursor.execute(

            "SELECT id FROM jobs WHERE fingerprint=?",

            (fingerprint,)

        )

        return self.cursor.fetchone() is not None

    def save(self, job: Job):

        logger.info(f"Saving: {job.title}")

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO jobs(
                job.title,
                job.company,
                job.source,
                job.url,
                job.fingerprint,
                job.score,
                job.posted_at,
                job.description
                )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                job.title,
                job.company,
                job.source,
                job.url,
                job.score,
                job.posted_at,
                job.description,
            ),
        )

        self.connection.commit()

    def count(self) -> int:

        self.cursor.execute(
            "SELECT COUNT(*) FROM jobs"
        )

        return self.cursor.fetchone()[0]

    def today(self):

        self.cursor.execute("""
        SELECT *
        FROM jobs
        ORDER BY score DESC
        """)

        return self.cursor.fetchall()

    def close(self):

        self.connection.close()