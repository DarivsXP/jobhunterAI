"""
Job prefiltering rules.
"""

from __future__ import annotations

import re

from candidate.profile import MY_PROFILE
from core.models import Job


class JobPrefilter:
    _word_boundary_template = r"(?<![a-z0-9]){term}(?![a-z0-9])"

    def should_keep(self, job: Job) -> bool:
        title = self._text(job.title)
        description = self._text(job.description)
        combined = f"{title} {description}"

        if not title:
            return False

        if self._has_generic_noise(title):
            return False

        if self._contains_any(title, MY_PROFILE.excluded_titles):
            return False

        if self._contains_any(title, MY_PROFILE.prefilter_excluded_keywords):
            return False

        if self._has_target_title_signal(title):
            return True

        return self._is_internship_match(title, combined)

    def _has_target_title_signal(self, title: str) -> bool:
        return any(
            keyword in title
            for keyword in MY_PROFILE.target_title_keywords
        )

    def _is_internship_match(self, title: str, combined: str) -> bool:
        if "intern" not in title:
            return False

        internship_stack = (
            "developer",
            "engineer",
            "software",
            "backend",
            "php",
            "laravel",
            "python",
            "web",
            "application support",
            "technical support",
        )

        return any(term in combined for term in internship_stack)

    def _has_generic_noise(self, title: str) -> bool:
        generic_titles = (
            "view open positions",
            "job vacancies",
            "open position",
            "open positions",
            "test job",
            "test job post",
            "speculative application",
        )

        return any(term in title for term in generic_titles)

    def _contains_any(self, text: str, terms: list[str]) -> bool:
        return any(self._contains_term(text, term) for term in terms)

    def _contains_term(self, text: str, term: str) -> bool:
        pattern = self._word_boundary_template.format(
            term=re.escape(term.lower())
        )
        return re.search(pattern, text) is not None

    def _text(self, value: str) -> str:
        return (value or "").casefold().strip()
