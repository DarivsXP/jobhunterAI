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

        if self._requires_too_much_experience(title, description):
            return False

        if self._is_too_old(job.posted_at):
            return False

        if self._has_target_title_signal(title):
            return True

        return self._is_internship_match(title, combined)

    def _is_too_old(self, posted_at: str) -> bool:
        if not posted_at or posted_at == "Unknown":
            return False

        import datetime

        try:
            posted_dt = datetime.datetime.strptime(
                posted_at[:19], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=datetime.timezone.utc)
            now = datetime.datetime.now(datetime.timezone.utc)
            age_days = (now - posted_dt).days
            if age_days > 30:
                return True
        except Exception:
            pass

        return False

    def _requires_too_much_experience(self, title: str, description: str) -> bool:
        is_junior_title = any(
            keyword in title
            for keyword in MY_PROFILE.junior_title_keywords
        )
        is_support_title = "support" in title

        # If it's a support role, we allow up to 5 years of experience.
        # If it is a junior role, we allow up to 5 years.
        # Otherwise, we allow up to 4 years (was 3; relaxed to capture more roles
        # that are technically mid-level but match Cyril's growing skillset).
        if is_support_title:
            max_allowed_years = 5
        elif is_junior_title:
            max_allowed_years = 5
        else:
            max_allowed_years = 4

        matches = re.finditer(
            r"\b(\d+)\+?\s*(?:-\s*\d+\+?|\s+to\s+\d+)?\s*(?:years?|yrs?)\b",
            description,
            re.IGNORECASE,
        )
        for m in matches:
            try:
                years = int(m.group(1))
                if years > max_allowed_years:
                    # Double check context to avoid false positives (e.g. company age)
                    start = max(0, m.start() - 50)
                    end = min(len(description), m.end() + 50)
                    context = description[start:end].lower()
                    context_keywords = [
                        "experience", "exp", "work", "background", "minimum", "at least",
                        "require", "preferred", "qualification", "level", "mid", "senior",
                        "coding", "programming", "development", "need", "must have", "track record",
                        "relevant", "professional"
                    ]
                    if any(k in context for k in context_keywords):
                        return True
            except ValueError:
                continue

        return False

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
