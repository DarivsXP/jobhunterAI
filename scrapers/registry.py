"""
Scraper Registry

Register every scraper here.
"""

from scrapers.arbeitnow import ArbeitnowScraper
from scrapers.himalayas import HimalayasScraper
from scrapers.jobicy import JobicyScraper
from scrapers.jobscollider import JobsColliderScraper
from scrapers.remoteco import RemoteCoScraper
from scrapers.remoteok import RemoteOKScraper
from scrapers.remotive import RemotiveScraper
from scrapers.weworkremotely import WeWorkRemotelyScraper
from scrapers.workingnomads import WorkingNomadsScraper
from scrapers.larajobs import LaraJobsScraper
from scrapers.vuejobs import VueJobsScraper
from scrapers.pythonorg import PythonOrgScraper

SCRAPERS = [
    RemotiveScraper(),
    RemoteOKScraper(),
    WeWorkRemotelyScraper(),
    HimalayasScraper(),
    JobicyScraper(),
    ArbeitnowScraper(),
    WorkingNomadsScraper(),
    RemoteCoScraper(),
    JobsColliderScraper(),
    LaraJobsScraper(),
    VueJobsScraper(),
    PythonOrgScraper(),
]
