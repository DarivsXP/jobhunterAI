"""
Job Scoring Engine
"""

from __future__ import annotations

import re

from candidate.profile import MY_PROFILE
from core.models import Job


class JobScorer:
    ROLE_TITLE_WEIGHT = 25
    ROLE_TEXT_WEIGHT = 10
    SKILL_WEIGHT = 6
    COUNTRY_WEIGHT = 15
    REMOTE_WEIGHT = 10
    JUNIOR_WEIGHT = 20
    TITLE_FOCUS_WEIGHT = 6
    DISCOURAGED_TITLE_PENALTY = 25
    PORTFOLIO_WEIGHT = 5

    _word_boundary_template = r"(?<![a-z0-9]){term}(?![a-z0-9])"

    def score(self, job: Job) -> tuple[int, list[str]]:
        score = 0
        reasons: list[str] = []

        title = self._text(job.title)
        text = self._build_search_text(job)

        if MY_PROFILE.remote_only and not job.remote:
            reasons.append("Rejected (Not Remote)")
            return self._reject(job, reasons)

        for title_filter in MY_PROFILE.excluded_titles:
            if self._contains_term(text, title_filter):
                reasons.append(f"Rejected ({title_filter})")
                return self._reject(job, reasons)

        role_score, role_reason = self._role_score(title, text)
        score += role_score
        if role_reason:
            reasons.append(role_reason)

        matched_skills: list[str] = []
        for skill in MY_PROFILE.preferred_skills:
            if self._matches_skill(text, skill):
                matched_skills.append(skill)

        if matched_skills:
            score += len(matched_skills) * self.SKILL_WEIGHT
            reasons.append(f"{len(matched_skills)} skill matches")
            job.matched_skills = matched_skills

        for country in MY_PROFILE.preferred_countries:
            if country.lower() in text:
                score += self.COUNTRY_WEIGHT
                reasons.append(country)
                break

        if job.remote:
            score += self.REMOTE_WEIGHT
            reasons.append("Remote")

        if any(keyword in title for keyword in MY_PROFILE.strong_title_keywords):
            score += self.TITLE_FOCUS_WEIGHT
            reasons.append("Target Title")

        if any(keyword in title for keyword in MY_PROFILE.junior_title_keywords):
            score += self.JUNIOR_WEIGHT
            reasons.append("Junior Friendly")

        if any(keyword in title for keyword in MY_PROFILE.discouraged_title_keywords):
            score -= self.DISCOURAGED_TITLE_PENALTY
            reasons.append("Adjacent Role Penalty")

        score += self.PORTFOLIO_WEIGHT
        score = max(0, min(score, 100))

        job.score = score
        job.reasons = reasons
        job.priority = self._priority_for_score(score)

        return score, reasons

    def _reject(self, job: Job, reasons: list[str]) -> tuple[int, list[str]]:
        job.score = 0
        job.reasons = reasons
        job.priority = "LOW"
        return 0, reasons

    def _role_score(self, title: str, text: str) -> tuple[int, str]:
        for role in MY_PROFILE.preferred_roles:
            role_lower = role.lower()
            if role_lower in title:
                return self.ROLE_TITLE_WEIGHT, role

        for role in MY_PROFILE.preferred_roles:
            role_lower = role.lower()
            if role_lower in text:
                return self.ROLE_TEXT_WEIGHT, role

        return 0, ""

    def _build_search_text(self, job: Job) -> str:
        return " ".join(
            [
                job.title,
                job.description,
                job.country,
                job.company,
            ]
        ).lower()

    def _contains_term(self, text: str, term: str) -> bool:
        pattern = self._word_boundary_template.format(
            term=re.escape(term.lower())
        )
        return re.search(pattern, text) is not None

    def _matches_skill(self, text: str, skill: str) -> bool:
        aliases = {
            "REST API": ("rest api", "rest apis", "restful api", "restful apis"),
            "JavaScript": ("javascript", "js"),
            "GitHub": ("github", "git hub"),
        }

        for term in aliases.get(skill, (skill.lower(),)):
            if term in text:
                return True

        return False

    def _priority_for_score(self, score: int) -> str:
        if score >= 90:
            return "HOT"
        if score >= 75:
            return "HIGH"
        if score >= MY_PROFILE.minimum_score:
            return "GOOD"
        return "LOW"

    def _text(self, value: str) -> str:
        return (value or "").lower().strip()
