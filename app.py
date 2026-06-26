"""
JobHunterAI

Application entry point.
"""

from core.logger import get_logger
from core.scheduler import Scheduler

logger = get_logger(__name__)


def main():

    logger.info("=" * 50)
    logger.info("Starting JobHunterAI")
    logger.info("=" * 50)

    scheduler = Scheduler()

    scheduler.start()


if __name__ == "__main__":
    main()