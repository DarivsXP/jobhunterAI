"""
JobHunterAI Database Repository
"""

from pathlib import Path
import sqlite3
from typing import Optional

from core.logger import get_logger
from core.models import Job

logger = get_logger(__name__)


class JobRepository:
    """
    Handles all database operations.
    """

    def __init__(self):

        Path("database").mkdir(exist_ok=True)

        self.connection = sqlite3.connect(
            "database/jobs.db",
            check_same_thread=False,
        )

        self.connection.row_factory = sqlite3.Row

        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):

        logger.info("Initializing database...")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            company TEXT,

            source TEXT,

            url TEXT UNIQUE,

            score INTEGER DEFAULT 0,

            posted_at TEXT,

            description TEXT,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        self.connection.commit()

    def exists(self, url: str) -> bool:

        self.cursor.execute(
            "SELECT id FROM jobs WHERE url=?",
            (url,),
        )

        return self.cursor.fetchone() is not None

    def save(self, job: Job):

        logger.info(f"Saving: {job.title}")

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO jobs(

                title,
                company,
                source,
                url,
                score,
                posted_at,
                description

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

    def find(self, job_id: int) -> Optional[sqlite3.Row]:

        self.cursor.execute(
            "SELECT * FROM jobs WHERE id=?",
            (job_id,),
        )

        return self.cursor.fetchone()

    def today(self):

        self.cursor.execute("""
        SELECT *
        FROM jobs
        WHERE DATE(created_at)=DATE('now')
        ORDER BY score DESC
        """)

        return self.cursor.fetchall()

    def top_matches(self, minimum_score: int = 80):

        self.cursor.execute(
            """
            SELECT *
            FROM jobs
            WHERE score >= ?
            ORDER BY score DESC
            """,
            (minimum_score,),
        )

        return self.cursor.fetchall()

    def count(self) -> int:

        self.cursor.execute(
            "SELECT COUNT(*) FROM jobs"
        )

        return self.cursor.fetchone()[0]

    def close(self):

        logger.info("Closing database connection.")

        self.connection.close()