import logging
from pathlib import Path

from config.settings import settings


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def build_logger() -> logging.Logger:

    logger = logging.getLogger("JobHunterAI")

    if logger.handlers:
        return logger

    logger.setLevel(settings.log_level)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    file_handler = logging.FileHandler(
        LOG_DIR / "jobhunter.log",
        encoding="utf-8",
    )

    console_handler = logging.StreamHandler()

    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


logger = build_logger()


def get_logger(name: str) -> logging.Logger:
    """Return a child logger for the given module name.

    This keeps a single configured root logger but allows modules
    to request a namespaced child logger via `get_logger(__name__)`.
    """

    base = build_logger()

    if not name:
        return base

    # Use getChild so handlers configured on the root logger are inherited
    return base.getChild(name)