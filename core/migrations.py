"""
Database migrations.
"""

from core.logger import get_logger

logger = get_logger(__name__)


class MigrationManager:

    def __init__(self, connection):

        self.connection = connection

        self.cursor = connection.cursor()

    def migrate(self):

        logger.info("Checking database schema...")

        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS schema_version(

            version INTEGER
        )
        """)

        self.connection.commit()

        self.cursor.execute(
            "SELECT COUNT(*) FROM schema_version"
        )

        if self.cursor.fetchone()[0] == 0:

            self.cursor.execute(
                "INSERT INTO schema_version VALUES (1)"
            )

            self.connection.commit()

            logger.info("Database version: 1")

        self.cursor.execute(
            "SELECT version FROM schema_version"
        )

        version = self.cursor.fetchone()[0]

        logger.info(f"Current schema version: {version}")

        #
        # Future migrations
        #

        if version < 2:

            logger.info("Migration v2 skipped (not created yet).")

        if version < 3:

            logger.info("Migration v3 skipped (not created yet).")