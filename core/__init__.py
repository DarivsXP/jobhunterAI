"""
Core package for JobHunterAI.
"""

from scrapers.remotive import RemotiveScraper


def run(self):

    self.scrapers = [
        RemotiveScraper(),
    ]