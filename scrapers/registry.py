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
from scrapers.onlinejobsph import OnlineJobsPhScraper
from scrapers.dynamitejobs import DynamiteJobsScraper
from scrapers.justremote import JustRemoteScraper
from scrapers.hubstafftalent import HubstaffTalentScraper
from scrapers.arcdev import ArcDevScraper
from scrapers.remotify import RemotifyScraper
from scrapers.hiremeph import HireMePhScraper
from scrapers.googlejobs import GoogleJobsScraper

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
    OnlineJobsPhScraper(),
    DynamiteJobsScraper(),
    JustRemoteScraper(),
    HubstaffTalentScraper(),
    ArcDevScraper(),
    RemotifyScraper(),
    HireMePhScraper(),
    GoogleJobsScraper(),
]
