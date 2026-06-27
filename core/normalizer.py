"""
Job Normalizer

Normalizes job data from different job boards into
a consistent format before the job enters the pipeline.
"""

from __future__ import annotations

import html
import re
from urllib.parse import urlsplit, urlunsplit

from core.models import Job


class JobNormalizer:
    """Normalizes Job objects."""

    _whitespace = re.compile(r"\s+")
    _html_tags = re.compile(r"<[^>]+>")

    def normalize(self, job: Job) -> Job:
        job.title = self._clean_text(str(job.title)).title()
        job.company = self._clean_text(str(job.company))
        job.description = self._clean_description(str(job.description))
        job.country = self._clean_text(str(job.country))
        job.source = self._clean_text(str(job.source))
        job.url = self._normalize_url(str(job.url))
        job.salary = self._clean_text(str(job.salary))
        job.posted_at = self._normalize_posted_at(str(job.posted_at))

        if not job.salary:
            job.salary = "Not specified"

        if not job.country:
            job.country = "Worldwide"

        if not job.posted_at:
            job.posted_at = "Unknown"

        return job

    def _normalize_posted_at(self, value: str) -> str:
        value = self._clean_text(value)
        if not value or value == "Unknown":
            return "Unknown"

        import datetime
        import email.utils

        # Handle Unix timestamps (e.g. RemoteOK)
        if value.isdigit():
            try:
                dt = datetime.datetime.fromtimestamp(int(value), tz=datetime.timezone.utc)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass

        # Try parsing RFC 2822 format (e.g. WeWorkRemotely/Himalayas RSS)
        try:
            dt = email.utils.parsedate_to_datetime(value)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

        # Try parsing ISO 8601 (e.g. Remotive)
        try:
            clean_str = value.replace("Z", "+00:00")
            dt = datetime.datetime.fromisoformat(clean_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            pass

        # Try other standard datetime formats
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"):
            try:
                dt = datetime.datetime.strptime(value[:19], fmt)
                return dt.strftime("%Y-%m-%d %H:%M:%S")
            except Exception:
                pass

        return value

    def _clean_text(self, value: str) -> str:
        if not value:
            return ""

        value = html.unescape(value)
        value = value.replace("\u00a0", " ")
        value = self._whitespace.sub(" ", value)

        return value.strip()

    def _clean_description(self, value: str) -> str:
        value = self._clean_text(value)
        value = self._html_tags.sub(" ", value)
        value = self._whitespace.sub(" ", value)
        return value.strip()

    def _normalize_url(self, url: str) -> str:
        if not url:
            return ""

        parts = urlsplit(url.strip())

        return urlunsplit(
            (
                parts.scheme.lower(),
                parts.netloc.lower(),
                parts.path,
                "",
                "",
            )
        )
