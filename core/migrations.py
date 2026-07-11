"""
Database migrations.
"""

from __future__ import annotations

import sqlite3

from core.logger import get_logger

logger = get_logger(__name__)


class MigrationManager:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.cursor = connection.cursor()

    def migrate(self) -> None:
        logger.info("Checking database schema...")

        self._ensure_schema_version_table()

        version = self._get_version()

        if version < 2:
            self._migration_v2()
            self._set_version(2)

        if version < 3:
            self._migration_v3()
            self._set_version(3)

        if version < 4:
            self._migration_v4()
            self._set_version(4)

        if version < 5:
            self._migration_v5()
            self._set_version(5)

        logger.info("Database schema is up to date.")

    def _ensure_schema_version_table(self) -> None:
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_version(
                version INTEGER NOT NULL
            )
            """
        )

        self.connection.commit()
        self.cursor.execute("SELECT COUNT(*) FROM schema_version")

        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(
                "INSERT INTO schema_version(version) VALUES (1)"
            )
            self.connection.commit()

    def _get_version(self) -> int:
        self.cursor.execute("SELECT version FROM schema_version LIMIT 1")
        row = self.cursor.fetchone()
        return int(row[0]) if row else 1

    def _set_version(self, version: int) -> None:
        self.cursor.execute("UPDATE schema_version SET version = ?", (version,))
        self.connection.commit()

    def _column_exists(self, table: str, column: str) -> bool:
        self.cursor.execute(f"PRAGMA table_info({table})")
        return any(row[1] == column for row in self.cursor.fetchall())

    def _migration_v2(self) -> None:
        logger.info("Running migration v2...")

        columns = {
            "location": "TEXT",
            "fingerprint": "TEXT",
            "score": "INTEGER DEFAULT 0",
            "priority": "TEXT DEFAULT 'LOW'",
            "applied": "INTEGER DEFAULT 0",
            "country": "TEXT",
            "salary": "TEXT",
            "posted_at": "TEXT",
        }

        self._add_missing_columns(columns)
        self.connection.commit()
        logger.info("Migration v2 complete.")

    def _migration_v3(self) -> None:
        logger.info("Running migration v3...")

        columns = {
            "interview_probability": "INTEGER DEFAULT 0",
        }

        self._add_missing_columns(columns)
        self.connection.commit()
        logger.info("Migration v3 complete.")

    def _migration_v4(self) -> None:
        logger.info("Running migration v4...")

        columns = {
            "matched_skills_json": "TEXT DEFAULT '[]'",
            "missing_skills_json": "TEXT DEFAULT '[]'",
            "ai_recommendation": "TEXT DEFAULT ''",
            "ai_reasoning": "TEXT DEFAULT ''",
            "application_status": "TEXT DEFAULT 'new'",
        }

        self._add_missing_columns(columns)
        self.connection.commit()
        logger.info("Migration v4 complete.")

    def _migration_v5(self) -> None:
        logger.info("Running migration v5...")

        columns = {
            "notes": "TEXT DEFAULT ''",
        }

        self._add_missing_columns(columns)
        self.connection.commit()
        logger.info("Migration v5 complete.")

    def _add_missing_columns(self, columns: dict[str, str]) -> None:
        for column, definition in columns.items():
            if self._column_exists("jobs", column):
                continue

            logger.info("Adding column: %s", column)

            try:
                self.cursor.execute(
                    f"ALTER TABLE jobs ADD COLUMN {column} {definition}"
                )
            except sqlite3.OperationalError as error:
                if "duplicate column name" not in str(error).lower():
                    raise

                logger.info(
                    "Column already exists after concurrent migration: %s",
                    column,
                )
