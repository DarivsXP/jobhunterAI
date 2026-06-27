"""
Scraper Registry

Register every scraper here.
"""

from scrapers.remoteok import RemoteOKScraper
from scrapers.remotive import RemotiveScraper
from scrapers.weworkremotely import WeWorkRemotelyScraper

SCRAPERS = [
    RemotiveScraper(),
    RemoteOKScraper(),
    WeWorkRemotelyScraper(),
]
