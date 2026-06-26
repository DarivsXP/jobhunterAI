import sqlite3
from pathlib import Path

from config.settings import settings
from core.logger import logger


class Database:

    def __init__(self) -> None:

        self.path = settings.database_path

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

    def connect(self) -> sqlite3.Connection:

        return sqlite3.connect(self.path)

    def initialize(self) -> None:

        connection = self.connect()

        cursor = connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                title TEXT NOT NULL,

                company TEXT NOT NULL,

                location TEXT,

                source TEXT NOT NULL,

                url TEXT UNIQUE NOT NULL,

                description TEXT,

                posted_at TEXT,

                score INTEGER DEFAULT 0,

                applied INTEGER DEFAULT 0,

                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

        connection.close()

        logger.info("Database initialized.")