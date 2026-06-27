"""
SQLite database connection and initialization.
"""

from __future__ import annotations

import sqlite3

from config.settings import settings
from core.logger import logger
from core.migrations import MigrationManager
from core.schema import JOBS_TABLE


class Database:
    def __init__(self) -> None:
        self.path = settings.database_path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        connection = self.connect()

        try:
            cursor = connection.cursor()
            cursor.execute(JOBS_TABLE)
            connection.commit()

            MigrationManager(connection).migrate()

            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_fingerprint ON jobs(fingerprint)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_score ON jobs(score DESC)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_priority ON jobs(priority)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_applied ON jobs(applied)"
            )
            cursor.execute(
                "CREATE INDEX IF NOT EXISTS idx_jobs_application_status "
                "ON jobs(application_status)"
            )

            connection.commit()

        finally:
            connection.close()

        logger.info("Database initialized.")
