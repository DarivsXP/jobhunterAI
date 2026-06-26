"""
Base scraper interface.
"""

from abc import ABC, abstractmethod
from typing import List

from core.models import Job


class BaseScraper(ABC):
    """Base class for all job scrapers."""

    @abstractmethod
    def fetch_jobs(self) -> List[Job]:
        """Return a list of Job objects."""
        pass