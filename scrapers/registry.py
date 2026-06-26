"""
Scraper Registry

Register every scraper here.
"""

from scrapers.remotive import RemotiveScraper

SCRAPERS = [
    RemotiveScraper(),
]