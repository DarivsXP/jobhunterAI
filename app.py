"""
JobHunterAI
"""

from core.logger import get_logger
from core.orchestrator import JobOrchestrator

logger = get_logger(__name__)


def main():

    logger.info("Starting JobHunterAI")

    orchestrator = JobOrchestrator()

    orchestrator.run()


if __name__ == "__main__":
    main()