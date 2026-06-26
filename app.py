from core.database import Database
from core.logger import logger


def main() -> None:

    logger.info("Starting JobHunterAI v0.8")

    database = Database()

    database.initialize()

    logger.info("Application ready.")


if __name__ == "__main__":
    main()