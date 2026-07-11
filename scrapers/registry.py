"""
Scraper Registry

Register every scraper here.

Removed scrapers (broken as of 2026-07):
  - GoogleJobsScraper    : Always CAPTCHA-blocked in headless mode
  - KalibrrScraper       : API endpoint returns 404 (removed/changed)
  - GlintsScraper        : API returns 400 for all queries (now requires auth)
  - JobStreetPhScraper   : Returns 403 Forbidden (blocks server-side requests)
  - ArcDevScraper        : Playwright timeout — JS-heavy SPA, no public API
  - RemotifyScraper      : Playwright timeout — JS-heavy, low yield
  - DynamiteJobsScraper  : Playwright — consistently returns 0 jobs
  - JustRemoteScraper    : Playwright — returns only 1 job, not worth overhead
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
from scrapers.hubstafftalent import HubstaffTalentScraper
from scrapers.hiremeph import HireMePhScraper
from scrapers.nodesk import NoDeskScraper

SCRAPERS = [
    # Global / international remote job boards (API-based, reliable)
    RemotiveScraper(),
    RemoteOKScraper(),
    WeWorkRemotelyScraper(),
    HimalayasScraper(),
    JobicyScraper(),
    ArbeitnowScraper(),
    WorkingNomadsScraper(),
    RemoteCoScraper(),
    JobsColliderScraper(),
    # Niche / tech-specific boards (RSS/API-based, reliable)
    LaraJobsScraper(),
    VueJobsScraper(),
    PythonOrgScraper(),
    HubstaffTalentScraper(),
    NoDeskScraper(),
    # Philippines-specific boards
    OnlineJobsPhScraper(),
    HireMePhScraper(),
]
