"""
OnlineJobs.ph Scraper

Scrapes jobs using BeautifulSoup.
"""

from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from core.logger import get_logger
from core.models import Job
from scrapers.base import BaseScraper

logger = get_logger(__name__)


class OnlineJobsPhScraper(BaseScraper):
    _URL = "https://www.onlinejobs.ph/jobseekers/jobsearch"
    _BASE_URL = "https://www.onlinejobs.ph"
    _WHITESPACE = re.compile(r"\s+")

    def fetch_jobs(self) -> list[Job]:
        logger.info("Fetching jobs from OnlineJobs.ph...")

        all_jobs: list[Job] = []

        try:
            response = requests.get(
                self._URL,
                headers={"User-Agent": "JobHunterAI/1.0"},
                timeout=15,
            )
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            job_cards = soup.select(".jobpost-cat-box")

            for card in job_cards:
                # Extract title
                title_elem = card.find("h4")
                if not title_elem:
                    continue
                
                # Remove badge text from title if present
                badge = title_elem.find("span", class_="badge")
                if badge:
                    badge.extract()
                title = self._clean(title_elem.get_text())

                # Extract URL
                url_elem = card.select_one(".desc a")
                url = url_elem["href"] if url_elem and url_elem.has_attr("href") else ""
                if url and url.startswith("/"):
                    url = self._BASE_URL + url

                if not url:
                    continue

                # Extract Description
                desc_elem = card.select_one(".desc")
                if desc_elem:
                    # Remove the "See More" link text
                    if url_elem:
                        url_elem.extract()
                    description = self._clean(desc_elem.get_text())
                else:
                    description = ""

                # Extract Salary
                salary_elem = card.select_one("dd.col")
                salary = self._clean(salary_elem.get_text()) if salary_elem else "Not specified"

                # Extract Posted At
                posted_elem = card.find("p", {"data-temp": True})
                posted_at = posted_elem["data-temp"] if posted_elem else "Unknown"

                all_jobs.append(
                    Job(
                        title=title,
                        company="Unknown",  # OnlineJobs.ph usually hides company names unless clicked
                        description=description,
                        url=url,
                        posted_at=posted_at,
                        salary=salary,
                        country="Philippines",
                        remote=True,
                        source="OnlineJobs.ph",
                    )
                )

        except Exception:
            logger.exception("OnlineJobs.ph request failed")

        logger.info("Fetched %d OnlineJobs.ph jobs.", len(all_jobs))
        return all_jobs

    def _clean(self, value: str) -> str:
        return self._WHITESPACE.sub(" ", value).strip()
